import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from backend.config import Settings
from backend.providers import ModelError, OpenAICompatibleProvider, normalize
from backend.telemetry import Metrics, configured_prices


SETTINGS = Settings(mode='api', base_url='https://provider.example/v1')
PRICES = {'embedding': 2.0, 'chat_input': 3.0, 'chat_output': 5.0}


def make_provider(handler, **options):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return OpenAICompatibleProvider(client, **options), client


def test_shared_client_concurrent_calls_keep_keys_separate_and_no_stored_credentials():
    def handler(request):
        number = json.loads(request.content)['input'][0]
        assert request.headers['Authorization'] == f'Bearer key-{number}'
        return httpx.Response(200, json={'data': [{'index': 0, 'embedding': [3, 4]}]})

    provider, client = make_provider(handler)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda number: provider.embed([str(number)], SETTINGS, f'key-{number}'), range(12)))
        assert all(result == [[0.6, 0.8]] for result in results)
        assert 'Authorization' not in client.headers
        provider.close()
        assert not client.is_closed  # Injected client remains caller-owned.
    finally:
        client.close()


def test_default_client_is_created_once_and_closed(monkeypatch):
    actual_client = httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={})))
    creates = []
    monkeypatch.setattr('backend.providers.httpx.Client', lambda **kwargs: creates.append(kwargs) or actual_client)
    with OpenAICompatibleProvider() as provider:
        provider.request(SETTINGS, 'one', '/embeddings', {})
        provider.request(SETTINGS, 'two', '/embeddings', {})
        assert len(creates) == 1
    assert actual_client.is_closed


def test_injected_default_authorization_is_not_used_for_keyless_request():
    def handler(request):
        assert 'Authorization' not in request.headers
        return httpx.Response(200, json={})

    with httpx.Client(transport=httpx.MockTransport(handler), headers={'Authorization': 'Bearer inherited'},
                      auth=('default-user', 'default-password')) as client:
        OpenAICompatibleProvider(client).request(SETTINGS, '', '/embeddings', {})


def test_embedding_batches_reorder_normalize_and_sum_reported_usage():
    batches = []

    def handler(request):
        batch = json.loads(request.content)['input']
        batches.append(batch)
        return httpx.Response(200, json={
            'data': [{'index': i, 'embedding': [int(text) + 1, 1]} for i, text in reversed(list(enumerate(batch)))],
            'usage': {'prompt_tokens': len(batch) * 10, 'total_tokens': len(batch) * 10},
        })

    metrics = Metrics(PRICES)
    provider, client = make_provider(handler)
    with client:
        vectors = provider.embed([str(i) for i in range(18)], SETTINGS, 'test-key', metrics)
    assert [len(batch) for batch in batches] == [16, 2]
    assert vectors[0] == normalize([1, 1])
    assert vectors[17] == normalize([18, 1])
    report = metrics.as_dict()
    assert report['token_usage']['embedding_tokens'] == 180
    assert report['cost_usd'] == pytest.approx(0.00036)
    assert report['request_count'] == 2
    assert report['attempt_count'] == 2
    assert report['timings_ms']['provider_http'] >= 0
    assert 'test-key' not in json.dumps(report)


@pytest.mark.parametrize('rows', [
    [{'index': 0, 'embedding': [1, 0]}, {'index': 0, 'embedding': [1, 0]}],
    [{'index': 0, 'embedding': [1, 0]}],
    [{'index': True, 'embedding': [1, 0]}, {'index': 0, 'embedding': [1, 0]}],
    [{'index': 0, 'embedding': [1, 0]}, {'index': 1, 'embedding': [1, 0, 1]}],
    [{'index': 0, 'embedding': [1, 0]}, {'index': 1, 'embedding': [0, 0]}],
])
def test_invalid_embedding_contract_is_rejected(rows):
    provider, client = make_provider(lambda _: httpx.Response(200, json={'data': rows}))
    with client, pytest.raises(ModelError):
        provider.embed(['first', 'second'], SETTINGS, '')


@pytest.mark.parametrize('vector', [[], [True, 1], [float('nan'), 1], [float('inf')], [0, 0], ['1'], [10 ** 400], [1] * 16385])
def test_normalization_rejects_non_vectors(vector):
    with pytest.raises(ModelError):
        normalize(vector)


def test_empty_embedding_input_has_no_cost_and_no_http_request():
    provider, client = make_provider(lambda _: pytest.fail('Should not request an empty batch'))
    metrics = Metrics({})
    with client:
        assert provider.embed([], SETTINGS, '', metrics) == []
    assert metrics.as_dict()['cost_usd'] == 0
    assert metrics.as_dict()['cost_status'] == 'no_api_calls'


def test_retry_after_is_used_and_unreported_failed_attempt_cost_stays_unknown():
    attempts = []
    delays = []

    def handler(request):
        attempts.append(request)
        if len(attempts) == 1:
            return httpx.Response(429, headers={'Retry-After': '0.1'}, json={'error': 'sensitive provider text'})
        return httpx.Response(200, json={'usage': {'prompt_tokens': 10, 'total_tokens': 10}})

    metrics = Metrics(PRICES)
    provider, client = make_provider(handler, sleep=delays.append)
    with client:
        provider.request(SETTINGS, 'test-key', '/embeddings', {'model': 'embedding'}, metrics)
    report = metrics.as_dict()
    assert delays == [0.1]
    assert report['request_count'] == 1 and report['attempt_count'] == 2 and report['retry_count'] == 1
    assert report['cost_usd'] is None
    assert report['known_cost_usd'] == pytest.approx(0.00002)
    assert report['token_usage']['complete'] is False
    assert report['unknown_cost_reasons'] == ['failed_attempt_without_usage']


def test_retry_after_date_is_bounded():
    response = httpx.Response(429, headers={'Retry-After': format_datetime(datetime.now(timezone.utc) + timedelta(minutes=5))})
    assert OpenAICompatibleProvider._retry_delay(response, 1) == 30


def test_retry_exhaustion_and_exception_trace_are_safe():
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout('secret-provider-url-and-key', request=request)

    metrics = Metrics(PRICES)
    provider, client = make_provider(handler, sleep=lambda _: None)
    with client:
        try:
            provider.request(SETTINGS, 'test-key', '/embeddings', {}, metrics)
        except ModelError as error:
            assert error.code == 'timeout'
            assert 'secret-provider-url-and-key' not in ''.join(traceback.format_exception(error))
        else:
            pytest.fail('Expected timeout error')
    assert len(calls) == 3
    assert metrics.as_dict()['cost_usd'] is None


def test_unauthorized_does_not_retry_or_expose_body():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(401, json={'error': 'private-key-and-prompt'})

    provider, client = make_provider(handler)
    with client, pytest.raises(ModelError) as failure:
        provider.request(SETTINGS, 'test-key', '/embeddings', {})
    assert len(calls) == 1 and failure.value.status_code == 401
    assert 'private-key-and-prompt' not in str(failure.value)


def test_redirect_never_forwards_authorization():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(307, headers={'Location': 'https://untrusted.example'})

    provider, client = make_provider(handler)
    with client, pytest.raises(ModelError) as failure:
        provider.request(SETTINGS, 'test-key', '/embeddings', {})
    assert len(calls) == 1 and failure.value.status_code == 307


@pytest.mark.parametrize('body', ['invalid', '[]', 'null'])
def test_invalid_provider_json_is_a_safe_error(body):
    provider, client = make_provider(lambda _: httpx.Response(200, text=body))
    with client, pytest.raises(ModelError) as failure:
        provider.request(SETTINGS, '', '/embeddings', {})
    assert failure.value.code == 'invalid_json'


def test_chat_json_preserves_usage_and_structured_options():
    def handler(request):
        payload = json.loads(request.content)
        assert payload['response_format'] == {'type': 'json_object'}
        assert payload['model'] == SETTINGS.chat_model
        return httpx.Response(200, json={
            'choices': [{'message': {'content': '{"status":"answered","claims":[]}'}, 'finish_reason': 'stop'}],
            'usage': {'prompt_tokens': 20, 'completion_tokens': 10, 'total_tokens': 30},
        })

    provider, client = make_provider(handler)
    metrics = Metrics(PRICES)
    with client:
        assert provider.chat_json(SETTINGS, '', [{'role': 'user', 'content': 'Return JSON'}], metrics)['status'] == 'answered'
    report = metrics.as_dict()
    assert report['token_usage'] == {'embedding_tokens': 0, 'input_tokens': 20, 'output_tokens': 10, 'total_tokens': 30,
                                     'complete': True, 'attempts_without_usage': 0}
    assert report['cost_usd'] == pytest.approx(0.00011)


@pytest.mark.parametrize('choice,code', [
    ({'message': {'content': None, 'refusal': 'Sensitive refusal'}}, 'provider_refusal'),
    ({'message': {'content': '{}'}, 'finish_reason': 'length'}, 'incomplete_answer'),
    ({'message': {'content': ''}}, 'chat_schema'),
    ({'message': {'content': '```json\n{}\n```'}}, 'chat_json'),
    ({'message': {'content': '[]'}}, 'chat_json'),
])
def test_invalid_or_incomplete_chat_is_rejected(choice, code):
    provider, client = make_provider(lambda _: httpx.Response(200, json={'choices': [choice]}))
    with client, pytest.raises(ModelError) as failure:
        provider.chat_json(SETTINGS, '', [])
    assert failure.value.code == code


def test_missing_price_and_missing_usage_are_explicit():
    metrics = Metrics({})
    metrics.record_request(kind='chat', model='chat', elapsed_ms=10, attempt=1,
                           usage={'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15})
    report = metrics.as_dict()
    assert report['cost_usd'] is None and report['token_usage']['complete']
    assert report['unknown_cost_reasons'] == ['price_missing:chat_input', 'price_missing:chat_output']
    metrics.record_request(kind='embedding', model='embed', elapsed_ms=2, attempt=1)
    assert metrics.as_dict()['token_usage']['complete'] is False


@pytest.mark.parametrize('usage', [
    {'prompt_tokens': True, 'completion_tokens': 1},
    {'prompt_tokens': -1, 'completion_tokens': 1},
    {'prompt_tokens': 2, 'completion_tokens': 1, 'total_tokens': 100},
    {'prompt_tokens': '2', 'completion_tokens': 1},
])
def test_invalid_usage_is_not_misreported_as_known_cost(usage):
    metrics = Metrics(PRICES)
    metrics.record_request(kind='chat', model='chat', elapsed_ms=1, attempt=1, usage=usage)
    assert metrics.as_dict()['unknown_cost_reasons'] == ['provider_usage_invalid']
    assert metrics.as_dict()['cost_usd'] is None


def test_prices_are_explicit_and_validated():
    assert set(configured_prices({})) == {'embedding', 'chat_input', 'chat_output', 'verifier_input', 'verifier_output', 'judge_input', 'judge_output'}
    assert all(value is None for value in configured_prices({}).values())
    assert configured_prices({'RAG_EMBEDDING_USD_PER_MILLION_TOKENS': '0'})['embedding'] == 0
    with pytest.raises(ValueError):
        configured_prices({'RAG_CHAT_OUTPUT_USD_PER_MILLION_TOKENS': 'nan'})
    with pytest.raises(ValueError):
        Metrics({'embedding': -1})
