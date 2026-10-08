"""Exercise real HTTPS proxy + pgvector + authenticated read-only demo; no model API."""

import argparse
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://localhost:18443")
    parser.add_argument("--ca", type=Path, required=True)
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--after-restart", action="store_true")
    args = parser.parse_args()
    checks = []
    context = ssl.create_default_context(cafile=str(args.ca))
    with httpx.Client(base_url=args.url, verify=context, timeout=30, trust_env=False) as client:
        health = client.get("/api/health")
        assert health.status_code == 200 and health.json()["storage"] == "pgvector"
        assert client.get("/api/documents").status_code == 401
        response = client.post("/api/auth/login", json={"token": args.token_file.read_text().strip()})
        assert response.status_code == 200
        assert all(s in response.headers["set-cookie"].lower() for s in ("secure", "httponly", "samesite=strict"))
        checks += ["trusted HTTPS certificate", "pgvector healthy", "authentication and secure cookie"]
        assert client.get("/api/auth/status").json()["demo"] is True
        docs = client.get("/api/documents").json()["documents"]
        assert len(docs) == 1 and not docs[0]["can_write"] and docs[0]["status"] == "ready"
        checks.append("fictional document persists and is read-only")
        assert client.post("/api/documents/sample").status_code == 403
        assert client.put("/api/settings", json={}).status_code == 403
        assert client.post("/api/auth/logout", headers={"Origin": "https://evil.example"}).status_code == 403
        checks += ["mutation denied", "cross-origin write denied"]
        if not args.after_restart:
            assert client.post("/api/chat", json={"question": "policy", "document_ids": ["secret"]}).status_code == 404
            response = client.post("/api/chat", json={"question": "PROC-26 5000 JPY"})
            assert response.status_code == 200 and response.json()["retrieved_sources"]
            checks += ["ACL before retrieval", "real local retrieval over pgvector"]
        assert client.post("/api/chat", json={"question": "policy"}).status_code == 429
        assert (
            client.post(
                "/api/chat", json={"question": "policy"}, headers={"X-Forwarded-For": "203.0.113.41"}
            ).status_code
            == 429
        )
        # Login IP limit must ignore attacker-controlled XFF at the proxy too.
        checks.append("persistent per-user quota")
        if args.after_restart:
            for index in range(10):
                client.post(
                    "/api/auth/login",
                    json={"token": "invalid-demo-token-000000"},
                    headers={"X-Forwarded-For": f"203.0.113.{index + 1}"},
                )
            assert (
                client.post(
                    "/api/auth/login",
                    json={"token": "invalid-demo-token-000000"},
                    headers={"X-Forwarded-For": "203.0.113.99"},
                ).status_code
                == 429
            )
            checks.append("spoofed XFF cannot bypass login IP quota")
    output = Path("reports/portfolio-sharing/demo-" + ("restart" if args.after_restart else "initial") + ".json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "status": "passed",
                "checks": checks,
                "scope": "Real Docker/Caddy TLS/PostgreSQL; local retrieval; no paid model calls",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "passed", "checks": checks}))


if __name__ == "__main__":
    main()
