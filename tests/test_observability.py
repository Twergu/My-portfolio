import json

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import create_app
from backend.providers import OpenAICompatibleProvider


@pytest.mark.parametrize('endpoint', ['/api/chat', '/api/settings/test'])
def test_failed_model_call_keeps_usage_latency_and_unknown_cost(tmp_path, endpoint):
    def transport(request):
        if request.url.path.endswith('/embeddings'):
            return httpx.Response(200, json={'data': [{'index': 0, 'embedding': [1., 0.]}],
                                             'usage': {'prompt_tokens': 7, 'total_tokens': 7}})
        return httpx.Response(401, json={'error': {'message': 'sensitive upstream body must not be logged'}})

    with httpx.Client(transport=httpx.MockTransport(transport)) as http:
        provider = OpenAICompatibleProvider(http, max_attempts=1)
        with TestClient(create_app(tmp_path, database_url='', provider=provider)) as client:
            config = Settings(mode='api', min_score=0)
            assert client.put('/api/settings', json=config.model_dump()).status_code == 200
            store = client.app.state.knowledge.store
            store.register_document({'id': 'fixture', 'name': 'fixture.pdf', 'sha256': 'fixture', 'size': 1,
                                     'status': 'queued', 'created_at': '2026-01-01'})
            store.commit_chunks('fixture', [{'page': 1, 'ordinal': 0, 'text': 'Annual leave requires manager approval.'}],
                                [[1., 0.]], config.profile)
            body = {'question': 'How is annual leave approved?'} if endpoint == '/api/chat' else config.model_dump()
            response = client.post(endpoint, json=body)
            assert response.status_code == 502
            record = client.get('/api/metrics').json()['operations'][-1]
            assert record['status'] == 'error'
            assert record['metrics']['token_usage']['embedding_tokens'] == 7
            assert record['metrics']['attempt_count'] == 2
            assert record['metrics']['cost_usd'] is None
            assert record['metrics']['elapsed_ms'] > 0
            assert 'sensitive upstream' not in json.dumps(record)


def test_pdf_parser_failure_logs_original_library_traceback(tmp_path):
    with TestClient(create_app(tmp_path, database_url='')) as client:
        response = client.post('/api/documents', files={'file': ('corrupt.pdf', b'%PDF-1.7\nnot a PDF', 'application/pdf')})
        assert response.status_code == 202
        service = client.app.state.knowledge
        service.wait_for_jobs()
        service.log_handler.flush()
        contents = (tmp_path / 'logs' / 'service.log').read_text(encoding='utf-8')
        assert 'PDF parser traceback' in contents
        assert 'Traceback (most recent call last)' in contents
        assert 'PdfStreamError' in contents or 'PdfReadError' in contents
        assert response.json()['id'] in contents


def test_api_evaluation_records_failed_indexing_without_fake_scores():
    from scripts.evaluate import evaluate_dataset, load_dataset, markdown
    dataset = load_dataset()
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(401, json={'error': 'invalid'}))) as http:
        provider = OpenAICompatibleProvider(http, max_attempts=1)
        report = evaluate_dataset(dataset, Settings(mode='api'), api_key='fixture-only', provider=provider)
    assert report['status'] == 'failed'
    assert report['summary']['query_count'] == 0
    assert report['indexing']['metrics']['attempt_count'] == 1
    assert report['indexing']['metrics']['cost_usd'] is None
    assert report['run_cost_usd'] is None
    assert 'N/A' in markdown(report)
