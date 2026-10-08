"""OpenAI-compatible transport shared across indexing and answer operations.

The application owns one provider for its lifetime. Configuration and API keys
are passed per call, so concurrent operations never mutate client credentials.
Injected clients are owned by their caller; close() closes only our own client.
"""

import json
import math
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx


class ModelError(Exception):
    """A user-safe provider failure, without response bodies or credentials."""

    def __init__(self, message, *, code="model_error", status_code=None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


def normalize(vector):
    if not isinstance(vector, list) or not 1 <= len(vector) <= 16384:
        raise ModelError("Embedding 返回了无效的向量维度。", code="embedding_dimensions")
    try:
        invalid = any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in vector)
    except OverflowError:
        invalid = True
    if invalid:
        raise ModelError("Embedding 返回了无效数值。", code="embedding_values")
    norm = math.hypot(*vector)
    if not math.isfinite(norm) or norm == 0:
        raise ModelError("Embedding 返回了无效的零向量或溢出向量。", code="embedding_values")
    return [x / norm for x in vector]


class OpenAICompatibleProvider:
    RETRYABLE = frozenset({408, 409, 429, 500, 502, 503, 504})

    def __init__(self, client=None, *, max_attempts=3, sleep=time.sleep):
        if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or not 1 <= max_attempts <= 5:
            raise ValueError("max_attempts must be between 1 and 5.")
        self._owns_client = client is None
        self.client = (
            client
            if client is not None
            else httpx.Client(
                timeout=httpx.Timeout(90, connect=10),
                follow_redirects=False,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10, keepalive_expiry=60),
            )
        )
        self.max_attempts = max_attempts
        self._sleep = sleep

    def close(self):
        if self._owns_client:
            self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @staticmethod
    def _retry_delay(response, attempt):
        header = response.headers.get("Retry-After") if response is not None else None
        if header:
            try:
                delay = float(header)
            except ValueError:
                try:
                    retry_at = parsedate_to_datetime(header)
                    if retry_at.tzinfo is None:
                        retry_at = retry_at.replace(tzinfo=timezone.utc)
                    delay = (retry_at - datetime.now(timezone.utc)).total_seconds()
                except (TypeError, ValueError, OverflowError):
                    delay = None
            if delay is not None and math.isfinite(delay):
                return min(30.0, max(0.0, delay))
        return min(2 ** (attempt - 1), 30)

    def request(self, settings, api_key, endpoint, payload, metrics=None, *, role=None, price_group="chat"):
        if endpoint not in ("/embeddings", "/chat/completions"):
            raise ValueError("Unsupported provider endpoint.")
        kind = "embedding" if endpoint == "/embeddings" else "chat"
        for attempt in range(1, self.max_attempts + 1):
            started = time.perf_counter()
            response = None
            data = None
            error = None
            transport_error = None
            try:
                request = self.client.build_request("POST", settings.base_url.rstrip("/") + endpoint, json=payload)
                # Do not retain a key on the client or inherit an injected client's
                # default authorization. Disable redirects to prevent key forwarding.
                request.headers.pop("Authorization", None)
                if api_key:
                    request.headers["Authorization"] = f"Bearer {api_key}"
                response = self.client.send(request, auth=None, follow_redirects=False)
                try:
                    data = response.json()
                except (ValueError, UnicodeDecodeError):
                    error = "invalid_json"
                if not 200 <= response.status_code < 300:
                    error = f"http_{response.status_code}"
                    detail = data.get("error") if isinstance(data, dict) else None
                    if (
                        response.status_code == 429
                        and isinstance(detail, dict)
                        and (
                            detail.get("code") in ("insufficient_quota", "credit_balance_exhausted")
                            or detail.get("type") == "insufficient_quota"
                        )
                    ):
                        error = "insufficient_quota"
                elif not isinstance(data, dict):
                    error = "invalid_json"
            except httpx.TimeoutException:
                transport_error = "timeout"
                error = transport_error
            except httpx.HTTPError:
                transport_error = "connection_error"
                error = transport_error
            finally:
                if metrics is not None:
                    metrics.record_request(
                        kind=kind,
                        model=str(payload.get("model", "")),
                        elapsed_ms=(time.perf_counter() - started) * 1000,
                        attempt=attempt,
                        status_code=response.status_code if response is not None else None,
                        usage=data.get("usage") if isinstance(data, dict) else None,
                        error=error,
                        role=role or kind,
                        price_group=price_group,
                    )
            retryable = error != "insufficient_quota" and (
                transport_error is not None or (response is not None and response.status_code in self.RETRYABLE)
            )
            if error and retryable and attempt < self.max_attempts:
                delay = self._retry_delay(response, attempt)
                if metrics is not None:
                    with metrics.measure("provider_backoff"):
                        self._sleep(delay)
                else:
                    self._sleep(delay)
                continue
            if transport_error == "timeout":
                raise ModelError("模型服务超时，请稍后重试或检查服务地址。", code="timeout") from None
            if transport_error:
                raise ModelError("无法连接模型服务，请检查网络和 API 地址。", code="connection_error") from None
            if response is not None and not 200 <= response.status_code < 300:
                if error == "insufficient_quota":
                    raise ModelError(
                        "API 账户额度不足，请在服务商 API 控制台检查余额与账单设置。", code=error, status_code=429
                    ) from None
                messages = {
                    401: "API 密钥无效或已过期。",
                    403: "没有访问该模型的权限。",
                    404: "API 地址或模型不存在，请检查配置。",
                    429: "模型服务限流或额度不足，请稍后重试。",
                }
                raise ModelError(
                    messages.get(response.status_code, f"模型服务返回 HTTP {response.status_code}，请检查模型兼容性。"),
                    code=error,
                    status_code=response.status_code,
                ) from None
            if error:
                raise ModelError("模型服务未返回有效的 JSON 数据。", code="invalid_json") from None
            return data
        raise ModelError("模型请求未能完成。", code="request_failed")

    def embed(self, texts, settings, api_key, metrics=None):
        if not isinstance(texts, (list, tuple)) or any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ModelError("Embedding 输入必须是非空文本列表。", code="embedding_input")
        vectors = []
        for start in range(0, len(texts), 16):
            batch = texts[start : start + 16]
            data = self.request(
                settings,
                api_key,
                "/embeddings",
                {
                    "model": settings.embedding_model,
                    "input": batch,
                    "encoding_format": "float",
                },
                metrics,
            )
            try:
                rows = data["data"]
                if not isinstance(rows, list) or len(rows) != len(batch):
                    raise ValueError("count")
                indices = [row["index"] for row in rows]
                if any(type(index) is not int for index in indices) or sorted(indices) != list(range(len(batch))):
                    raise ValueError("indices")
                vectors.extend(normalize(row["embedding"]) for row in sorted(rows, key=lambda row: row["index"]))
            except (KeyError, TypeError, ValueError):
                raise ModelError("Embedding 响应的条数、顺序或格式不正确。", code="embedding_schema") from None
        if vectors and len({len(vector) for vector in vectors}) != 1:
            raise ModelError("Embedding 批次之间的向量维度不一致。", code="embedding_dimensions")
        return vectors

    def chat(self, settings, api_key, messages, metrics=None, *, role="generator", **options):
        if role not in ("generator", "verifier", "judge", "reranker", "planner"):
            raise ValueError("Unknown model role.")
        model = (
            settings.effective_verifier_model
            if role == "verifier"
            else settings.effective_reranker_model
            if role == "reranker"
            else settings.chat_model
        )
        group = "judge" if role == "judge" else role if model != settings.chat_model else "chat"
        payload = {"model": model, "messages": messages, **options}
        if payload.get("stream"):
            raise ValueError("This provider requires a non-streaming chat response.")
        data = self.request(settings, api_key, "/chat/completions", payload, metrics, role=role, price_group=group)
        try:
            choice = data["choices"][0]
            message = choice["message"]
            if message.get("refusal"):
                raise ModelError("回答模型拒绝了本次请求。", code="provider_refusal")
            if choice.get("finish_reason") in ("length", "content_filter"):
                raise ModelError("回答模型返回的内容不完整。", code="incomplete_answer")
            result = message["content"].strip()
            if not result or len(result) > 30000:
                raise ValueError("Invalid answer length")
        except (KeyError, IndexError, TypeError, AttributeError, ValueError):
            raise ModelError("回答模型没有返回有效文本。", code="chat_schema") from None
        return result

    def chat_json(self, settings, api_key, messages, metrics=None, **options):
        options.setdefault("response_format", {"type": "json_object"})
        content = self.chat(settings, api_key, messages, metrics, **options)
        try:
            result = json.loads(content)
            if not isinstance(result, dict):
                raise ValueError("Expected an object")
        except (ValueError, TypeError):
            raise ModelError("回答模型未返回有效的 JSON 对象。", code="chat_json") from None
        return result
