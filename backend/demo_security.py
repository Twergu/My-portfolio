"""Opt-in, single-process portfolio demo admission and persistent spend reservations.

No prompts or evidence rules live here. Budgets use configured prices, not bills.
Unknown usage keeps the full reservation, including across process restarts.
"""

import hashlib
import json
import math
import os
import re
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from .providers import ModelError, OpenAICompatibleProvider
from .telemetry import configured_prices


class DemoLimit(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def allowed_hosts():
    hosts = [
        h.strip().lower() for h in os.getenv("RAG_ALLOWED_HOSTS", "127.0.0.1,localhost,[::1],testserver").split(",")
    ]
    if not hosts or any(
        not h or h != "[::1]" and not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", h) for h in hosts
    ):
        raise ValueError("RAG_ALLOWED_HOSTS must contain explicit hostnames/IPs, without wildcards, ports or URLs")
    return hosts


class DemoGuard:
    def __init__(self, folder, *, clock=time.time):
        self.clock = clock
        self.lock = threading.RLock()
        self.active = set()
        self.path = folder / "demo-usage.sqlite3"
        self.user_daily = self._integer("RAG_DEMO_USER_DAILY", 20)
        self.ip_minute = self._integer("RAG_DEMO_IP_MINUTE", 10)
        self.global_daily = self._integer("RAG_DEMO_GLOBAL_DAILY", 100)
        self.concurrent = self._integer("RAG_DEMO_CONCURRENT", 2)
        self.output_tokens = self._integer("RAG_DEMO_OUTPUT_TOKENS", 4096)
        self.input_bytes = self._integer("RAG_DEMO_INPUT_BYTES", 60000)
        self.budget = float(os.getenv("RAG_DEMO_DAILY_USD", "1"))
        if not math.isfinite(self.budget) or not 0 < self.budget <= 100:
            raise ValueError("RAG_DEMO_DAILY_USD must be between 0 and 100")
        with self.connect() as db:
            db.executescript(
                "CREATE TABLE IF NOT EXISTS quota (kind TEXT, identity TEXT, window INTEGER, count INTEGER, "
                "PRIMARY KEY(kind,identity,window));"
                "CREATE TABLE IF NOT EXISTS spend (day TEXT PRIMARY KEY, reserved REAL NOT NULL, blocked INTEGER NOT NULL);"
            )

    @staticmethod
    def _integer(name, default):
        value = int(os.getenv(name, str(default)))
        if not 1 <= value <= 100000:
            raise ValueError(f"{name} must be a positive bounded integer")
        return value

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def _quotas(self, limits):
        now = int(self.clock())
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "DELETE FROM quota WHERE (kind LIKE '%minute' AND window < ?) OR (kind LIKE '%daily' AND window < ?)",
                (now // 60 - 1, now // 86400 - 1),
            )
            for kind, identity, period, maximum in limits:
                key = hashlib.sha256(identity.encode()).hexdigest()
                window = now // period
                row = db.execute(
                    "SELECT count FROM quota WHERE kind=? AND identity=? AND window=?", (kind, key, window)
                ).fetchone()
                if row and row[0] >= maximum:
                    raise DemoLimit("demo_quota", "Demo request limit reached. Try later or contact the operator.")
                db.execute(
                    "INSERT INTO quota VALUES (?,?,?,1) ON CONFLICT(kind,identity,window) DO UPDATE SET count=count+1",
                    (kind, key, window),
                )

    def login_attempt(self, ip):
        # Global quota also bounds storage growth from many distinct client IPs.
        self._quotas([("login_global_minute", "all", 60, 60), ("login_ip_minute", ip, 60, 10)])

    @contextmanager
    def slot(self, user, ip):
        with self.lock:
            if user in self.active or len(self.active) >= self.concurrent:
                raise DemoLimit("demo_busy", "Demo is busy. Wait for the current request to finish.")
            self._quotas(
                [
                    ("requests_global_daily", "all", 86400, self.global_daily),
                    ("requests_user_daily", user, 86400, self.user_daily),
                    ("requests_ip_minute", ip, 60, self.ip_minute),
                ]
            )
            self.active.add(user)
        try:
            yield
        finally:
            with self.lock:
                self.active.discard(user)

    def reserve(self, amount):
        if not math.isfinite(amount) or amount <= 0:
            raise ModelError("Demo pricing is missing or invalid.", code="demo_pricing")
        day = datetime.fromtimestamp(self.clock(), timezone.utc).date().isoformat()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO spend VALUES (?,0,0)", (day,))
            used, blocked = db.execute("SELECT reserved,blocked FROM spend WHERE day=?", (day,)).fetchone()
            if blocked or used + amount > self.budget:
                raise ModelError("Demo daily API budget reached. Please try another day.", code="demo_budget")
            db.execute("UPDATE spend SET reserved=reserved+? WHERE day=?", (amount, day))
        return day

    def settle(self, day, reserved, actual):
        # Missing/invalid usage means no refund. Unexpected excess closes the circuit.
        if actual is None or not math.isfinite(actual) or actual < 0:
            return
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                "UPDATE spend SET reserved=MAX(0,reserved+?), blocked=MAX(blocked,?) WHERE day=?",
                (actual - reserved, int(actual > reserved), day),
            )


class DemoProvider(OpenAICompatibleProvider):
    def __init__(self, guard, client=None):
        # Each paid attempt must have its own reservation. No hidden HTTP retries.
        super().__init__(client, max_attempts=1)
        self.guard = guard

    def request(self, settings, api_key, endpoint, payload, metrics=None, *, role=None, price_group="chat"):
        payload = dict(payload)
        embedding = endpoint == "/embeddings"
        if not embedding:
            payload.pop("max_tokens", None)
            payload["max_completion_tokens"] = min(
                int(payload.get("max_completion_tokens", self.guard.output_tokens)), self.guard.output_tokens
            )
            if payload["max_completion_tokens"] <= 0:
                raise ModelError("Invalid demo output limit.", code="demo_context")
        size = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        if size > self.guard.input_bytes:
            raise ModelError("Demo model context limit reached.", code="demo_context")
        prices = configured_prices()
        input_price = prices.get("embedding" if embedding else price_group + "_input")
        output_price = 0 if embedding else prices.get(price_group + "_output")
        if input_price is None or output_price is None or input_price <= 0 or (not embedding and output_price <= 0):
            raise ModelError("Configure positive demo model prices before enabling API calls.", code="demo_pricing")
        # UTF-8 byte budget + protocol margin is a conservative configured estimate,
        # not a universal tokenizer/billing guarantee. Oversized actual usage trips a fuse.
        ceiling = (
            (size + 4096) * input_price + (0 if embedding else payload["max_completion_tokens"]) * output_price
        ) / 1_000_000
        day = self.guard.reserve(ceiling)
        data = super().request(settings, api_key, endpoint, payload, metrics, role=role, price_group=price_group)
        usage = data.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        a = usage.get("prompt_tokens", usage.get("input_tokens", usage.get("total_tokens") if embedding else None))
        b = 0 if embedding else usage.get("completion_tokens", usage.get("output_tokens"))
        actual = (
            (a * input_price + b * output_price) / 1_000_000
            if type(a) is int and type(b) is int and a >= 0 and b >= 0
            else None
        )
        self.guard.settle(day, ceiling, actual)
        return data
