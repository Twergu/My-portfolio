"""Per-operation latency, reported token usage, and explicit price estimates.

Prices are USD per million tokens supplied by the operator. Missing prices or
usage are unknown, never silently zero. These estimates are not provider bills;
uniform configured rates do not model cache discounts, taxes, or service tiers.
"""

import math
import os
import time
from contextlib import contextmanager


PRICE_ENV = {
    'embedding': 'RAG_EMBEDDING_USD_PER_MILLION_TOKENS',
    'chat_input': 'RAG_CHAT_INPUT_USD_PER_MILLION_TOKENS',
    'chat_output': 'RAG_CHAT_OUTPUT_USD_PER_MILLION_TOKENS',
    'verifier_input': 'RAG_VERIFIER_INPUT_USD_PER_MILLION_TOKENS',
    'verifier_output': 'RAG_VERIFIER_OUTPUT_USD_PER_MILLION_TOKENS',
    'judge_input': 'RAG_JUDGE_INPUT_USD_PER_MILLION_TOKENS',
    'judge_output': 'RAG_JUDGE_OUTPUT_USD_PER_MILLION_TOKENS',
}


def configured_prices(environ=None):
    environ = os.environ if environ is None else environ
    prices = {}
    for kind, name in PRICE_ENV.items():
        raw = environ.get(name)
        if raw is None or str(raw).strip() == '':
            prices[kind] = None
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = float('nan')
        if not math.isfinite(value) or value < 0:
            raise ValueError(f'{name} must be a non-negative finite USD price.')
        prices[kind] = value
    return prices


def _token_count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


class Metrics:
    """Mutable metrics for one indexing job or one question; do not share jobs.

    The HTTP provider is shared, while a Metrics object belongs to its caller.
    Successful usage is counted once per response, including retry responses
    with valid usage. Failed attempts without usage make total cost unknown.
    """

    def __init__(self, prices=None):
        self.started = time.perf_counter()
        self.timings = {}
        self.prices = configured_prices() if prices is None else {key: prices.get(key) for key in PRICE_ENV}
        for value in self.prices.values():
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                raise ValueError('Token prices must be non-negative finite numbers or None.')
        self.requests = []
        self.validation_failures = []
        self._usage = {'embedding_tokens': 0, 'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        self._known_cost = 0.0
        self._unknown = set()
        self._missing_usage = 0

    @contextmanager
    def measure(self, name):
        started = time.perf_counter()
        try:
            yield
        finally:
            self.timings[name] = self.timings.get(name, 0.0) + (time.perf_counter() - started) * 1000

    def record_request(self, *, kind, model, elapsed_ms, attempt, status_code=None,
                       usage=None, error=None, role=None, price_group='chat'):
        """Record a single HTTP attempt. No URL, key, prompt or body is stored."""
        self.requests.append({
            'kind': kind, 'model': model, 'elapsed_ms': round(elapsed_ms, 3),
            'attempt': attempt, 'status_code': status_code, 'error': error,
            'role': role or kind,
        })
        self.timings['provider_http'] = self.timings.get('provider_http', 0.0) + elapsed_ms
        if not isinstance(usage, dict):
            self._missing_usage += 1
            self._unknown.add('failed_attempt_without_usage' if error else 'provider_usage_missing')
            return
        input_tokens = _token_count(usage.get('prompt_tokens', usage.get('input_tokens')))
        output_tokens = 0 if kind == 'embedding' else _token_count(usage.get('completion_tokens', usage.get('output_tokens')))
        total_tokens = _token_count(usage.get('total_tokens'))
        if input_tokens is None or output_tokens is None or (total_tokens is not None and total_tokens != input_tokens + output_tokens):
            self._missing_usage += 1
            self._unknown.add('provider_usage_invalid')
            return
        self._usage['total_tokens'] += input_tokens + output_tokens
        self.requests[-1]['token_usage'] = {'input_tokens': input_tokens, 'output_tokens': output_tokens,
                                          'total_tokens': input_tokens + output_tokens}
        if kind == 'embedding':
            self._usage['embedding_tokens'] += input_tokens
            components = [('embedding', input_tokens)]
        else:
            self._usage['input_tokens'] += input_tokens
            self._usage['output_tokens'] += output_tokens
            components = [(price_group + '_input', input_tokens), (price_group + '_output', output_tokens)]
        for component, tokens in components:
            price = self.prices.get(component)
            if price is None:
                self._unknown.add(f'price_missing:{component}')
            else:
                self._known_cost += tokens * price / 1_000_000

    def as_dict(self):
        attempt_count = len(self.requests)
        retry_count = sum(request['attempt'] > 1 for request in self.requests)
        return {
            'elapsed_ms': round((time.perf_counter() - self.started) * 1000, 3),
            'timings_ms': {key: round(value, 3) for key, value in self.timings.items()},
            'token_usage': {**self._usage, 'complete': self._missing_usage == 0,
                            'attempts_without_usage': self._missing_usage},
            'request_count': attempt_count - retry_count,
            'attempt_count': attempt_count,
            'retry_count': retry_count,
            'cost_usd': None if self._unknown else round(self._known_cost, 10),
            'known_cost_usd': round(self._known_cost, 10),
            'cost_status': 'unknown' if self._unknown else ('estimated' if attempt_count else 'no_api_calls'),
            'cost_basis': 'configured_uniform_usd_per_million_tokens',
            'prices': dict(self.prices),
            'unknown_cost_reasons': sorted(self._unknown),
            'requests': [dict(request) for request in self.requests],
            'validation_failures': [dict(event) for event in self.validation_failures],
        }
