import io
import json
import sqlite3
import threading

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from backend import rag
from backend.providers import OpenAICompatibleProvider
from backend.config import ROOT, Settings
from backend.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / 'knowledge', database_url='')) as test_client:
        yield test_client


def upload(client, content=None, name='员工手册.pdf'):
    content = content if content is not None else (ROOT / 'samples' / 'employee-handbook.pdf').read_bytes()
    response = client.post('/api/documents', files={'file': (name, content, 'application/pdf')})
    assert response.status_code == 202, response.text
    client.app.state.knowledge.wait_for_jobs()
    return response.json()['id']


def ask(client, question='员工年假如何申请？', **extra):
    response = client.post('/api/chat', json={'question': question, **extra})
    assert response.status_code == 200, response.text
    return response.json()


def english_pdf(text):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(60, 750, text)
    pdf.save()
    return buffer.getvalue()


def test_empty_library_refuses_and_blank_query_rejected(client):
    result = ask(client)
    assert result['refused'] and not result['sources']
    assert client.post('/api/chat', json={'question': '   '}).status_code == 422


def test_chinese_pdf_upload_retrieval_and_physical_page_citation(client):
    doc_id = upload(client)
    doc = client.get('/api/documents').json()['documents'][0]
    assert doc['status'] == 'ready' and doc['pages'] == 3
    result = ask(client)
    assert result['mode'] == 'local' and not result['refused']
    source = result['sources'][0]
    assert source['document_id'] == doc_id and source['page'] == 2
    assert '3 个工作日' in source['text'] and '直属经理' in source['text']
    response = client.get(source['url'].split('#')[0])
    assert response.content.startswith(b'%PDF-')
    assert response.headers['content-type'] == 'application/pdf'
    assert '#page=2' in source['url']


def test_duplicate_does_not_double_index(client):
    assert upload(client) == upload(client, name='改名后.pdf')
    docs = client.get('/api/documents').json()['documents']
    assert len(docs) == 1
    assert len(client.get(f"/api/documents/{docs[0]['id']}/chunks").json()['chunks']) == docs[0]['chunk_count']


def test_irrelevant_question_and_document_scope(client):
    upload(client)
    unrelated = upload(client, english_pdf('Office plants are watered every Friday.'), 'plants.pdf')
    assert ask(client, '量子隧穿实验温度多少')['refused']
    assert ask(client, document_ids=[unrelated])['refused']
    response = client.post('/api/chat', json={'question': '年假如何申请', 'document_ids': ['missing']})
    assert response.status_code == 409


@pytest.mark.parametrize('kind', ['broken', 'encrypted', 'scan'])
def test_failed_pdf_is_explicit_and_does_not_pollute_index(client, kind):
    if kind == 'broken':
        content = b'%PDF-1.7\nbroken data'
    else:
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        if kind == 'encrypted':
            writer.encrypt('private-test')
        buffer = io.BytesIO()
        writer.write(buffer)
        content = buffer.getvalue()
    doc_id = upload(client, content, kind + '.pdf')
    doc = client.get('/api/documents').json()['documents'][0]
    assert doc['status'] == 'error' and doc['error']
    assert not client.get(f'/api/documents/{doc_id}/chunks').json()['chunks']
    assert ask(client)['refused']


def test_delete_removes_index_and_file(client):
    doc_id = upload(client)
    assert client.delete(f'/api/documents/{doc_id}').status_code == 200
    assert client.get(f'/api/documents/{doc_id}/file').status_code == 404
    assert ask(client)['refused']
    with client.app.state.knowledge.store.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0] == 0


def test_restart_retains_ready_documents_and_marks_interrupted_jobs(tmp_path):
    folder = tmp_path / 'restart'
    first_app = create_app(folder, database_url='')
    with TestClient(first_app) as first:
        doc_id = upload(first)
    with TestClient(create_app(folder, database_url='')) as second:
        assert ask(second)['sources'][0]['document_id'] == doc_id
        second.app.state.knowledge.store.update(doc_id, status='embedding')
    with TestClient(create_app(folder, database_url='')) as third:
        doc = third.get('/api/documents').json()['documents'][0]
        assert doc['status'] == 'error' and '中断' in doc['error']
        assert third.post(f'/api/documents/{doc_id}/retry').status_code == 202
        third.app.state.knowledge.wait_for_jobs()
        assert ask(third)['sources']


def mock_provider(monkeypatch, answer_text='年假应提前 3 个工作日在 OA 提交，直属经理批准后生效。[1]'):
    calls = []

    def fake_request(self, settings, api_key, endpoint, payload, metrics=None, **options):
        calls.append((endpoint, payload))
        if endpoint == '/embeddings':
            # Deliberately reversed order exercises the provider index contract.
            return {'data': [{'index': i, 'embedding': rag.local_vector(text)} for i, text in reversed(list(enumerate(payload['input'])))]}
        if 'verifier' in payload['messages'][0]['content']:
            request = json.loads(payload['messages'][1]['content'])
            content = json.dumps({'verdicts': [{'claim_index': i, 'supported': True, 'reason': 'Supported by test evidence.'} for i in range(1, len(request['claims'])+1)]})
        elif answer_text == '年假应提前 3 个工作日在 OA 提交，直属经理批准后生效。[1]':
            request = json.loads(payload['messages'][1]['content'])
            content = json.dumps({'status': 'answered', 'claims': [{'text': answer_text.replace('[1]', ''), 'evidence': [{'source_id': 1, 'quote': request['sources'][0]['text']}]}]}, ensure_ascii=False)
        else:
            content = answer_text
        return {'choices': [{'message': {'content': content}}]}

    monkeypatch.setattr(OpenAICompatibleProvider, 'request', fake_request)
    return calls


def configure_api(client, **extra):
    settings = Settings(mode='api', min_score=0.06).model_dump()
    settings.update(extra)
    response = client.put('/api/settings', json=settings)
    assert response.status_code == 200, response.text
    return response.json()


def test_compatible_api_embedding_generation_and_citation_mapping(client, monkeypatch):
    calls = mock_provider(monkeypatch)
    configure_api(client, api_key='test-only-secret')
    doc_id = upload(client)
    result = ask(client)
    assert result['mode'] == 'api' and not result['refused']
    assert result['sources'][0]['page'] == 2
    assert result['sources'][0]['document_id'] == doc_id
    assert '[1]' in result['answer']
    assert [endpoint for endpoint, _ in calls] == ['/embeddings', '/embeddings', '/chat/completions', '/chat/completions']


@pytest.mark.parametrize('answer_text', ['伪造答案。[99]', '没有引用的答案', 'NO_EVIDENCE'])
def test_invalid_or_missing_citations_are_not_displayed(client, monkeypatch, answer_text):
    mock_provider(monkeypatch, answer_text)
    configure_api(client)
    upload(client)
    result = ask(client)
    assert result['refused'] and not result['sources']
    assert result['answer'] != answer_text


def test_embedding_model_change_isolated_even_at_same_dimensions(client, monkeypatch):
    mock_provider(monkeypatch)
    configure_api(client)
    upload(client)
    configure_api(client, embedding_model='different-model-with-same-dimension')
    assert client.get('/api/documents').json()['documents'][0]['needs_reindex']
    assert ask(client)['refused']
    assert client.post('/api/documents/reindex').json()['queued'] == 1
    client.app.state.knowledge.wait_for_jobs()
    assert not client.get('/api/documents').json()['documents'][0]['needs_reindex']
    assert ask(client)['sources']


def test_failed_embedding_batch_never_commits_partial_index(client, monkeypatch):
    configure_api(client)
    def broken(*args, **kwargs):
        raise rag.ModelError('模型服务超时')
    monkeypatch.setattr(OpenAICompatibleProvider, 'request', broken)
    doc_id = upload(client)
    assert client.get('/api/documents').json()['documents'][0]['status'] == 'error'
    assert not client.get(f'/api/documents/{doc_id}/chunks').json()['chunks']
    mock_provider(monkeypatch)
    assert client.post(f'/api/documents/{doc_id}/retry').status_code == 202
    client.app.state.knowledge.wait_for_jobs()
    assert ask(client)['sources']


def test_credentials_are_not_returned_or_persisted_and_do_not_follow_new_host(client):
    public = configure_api(client, api_key='never-persist-this-key')
    assert public['has_key'] and 'api_key' not in public
    with client.app.state.knowledge.store.connect() as db:
        assert 'never-persist-this-key' not in db.execute('SELECT value FROM settings').fetchone()[0]
    assert not configure_api(client, base_url='https://example.com/v1')['has_key']
    assert 'never-persist-this-key' not in client.get('/api/settings').text


def test_untrusted_origins_and_non_pdf_files_rejected(client):
    assert client.post('/api/documents/sample', headers={'Origin':'https://untrusted.example'}).status_code == 403
    assert client.get('/api/health', headers={'Host':'evil.example'}).status_code == 400
    assert client.post('/api/documents', files={'file':('wrong.pdf', b'not a PDF')}).status_code == 400
    assert client.put('/api/settings', json=Settings().model_dump() | {'base_url':'http://remote.example/v1'}).status_code == 422


@pytest.mark.parametrize('rows', [[], [{'index':0,'embedding':[0,0]}], [{'index':0,'embedding':[float('nan'),1]}], [{'index':9,'embedding':[1,0]}]])
def test_invalid_provider_vectors_fail_closed(monkeypatch, rows):
    monkeypatch.setattr(OpenAICompatibleProvider, 'request', lambda *args, **kwargs: {'data': rows})
    with pytest.raises(rag.ModelError):
        with OpenAICompatibleProvider() as provider:
            rag.embed(['test'], Settings(mode='api'), '', provider=provider)


def test_chunks_keep_page_boundaries_and_overlap():
    chunks = rag.chunks_from_pages([{'page':2,'text':'年假申请。'*400}, {'page':3,'text':'差旅报销不得超过每日限额。'}])
    assert all('差旅' not in chunk['text'] for chunk in chunks if chunk['page'] == 2)
    assert chunks[-1]['page'] == 3 and '不得' in chunks[-1]['text']
    assert len(chunks) > 2 and len(chunks[0]['text']) <= 900


def test_japanese_kana_and_kanji_are_searchable_and_refusal_is_japanese(client):
    service = client.app.state.knowledge
    doc_id = 'japanese-demo'
    text = '有給休暇の申請は、取得日の三日前までに社内システムで行ってください。'
    with service.store.connect() as db:
        db.execute('INSERT INTO documents(id,name,sha256,size,status,pages,chunk_count,profile,dimensions,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                   (doc_id, '日本語サンプル.pdf', 'jp-digest', 1, 'ready', 1, 1, Settings().profile, 2048, '2026-01-01T00:00:00Z'))
        db.execute('INSERT INTO chunks(id,document_id,page,ordinal,text,vector) VALUES(?,?,?,?,?,?)',
                   ('japanese-chunk', doc_id, 1, 0, text, json.dumps(rag.local_vector(text))))
    result = ask(client, '有給休暇はいつまでに申請すればよいですか？')
    assert not result['refused'] and result['sources'][0]['page'] == 1
    assert result['answer'].startswith('以下の関連する原文が見つかりました。')
    kanji_only = ask(client, '有給休暇申請', language='ja')
    assert kanji_only['answer'].startswith('以下の関連する原文が見つかりました。')
    refused = ask(client, '宇宙旅行の料金はいくらですか？')
    assert refused['refused'] and '十分な根拠' in refused['answer']


def test_api_answer_language_follows_japanese_question(client, monkeypatch):
    calls = []
    def japanese_provider(self, settings, api_key, endpoint, payload, metrics=None, **options):
        calls.append((endpoint, payload))
        if endpoint == '/embeddings':
            return {'data': [{'index': i, 'embedding': [1.0, 0.0]} for i, _ in enumerate(payload['input'])]}
        data = json.loads(payload['messages'][1]['content'])
        if 'verifier' in payload['messages'][0]['content']:
            content = {'verdicts': [{'claim_index': 1, 'supported': True, 'reason': 'Test verifier.'}]}
        else:
            content = {'status': 'answered', 'claims': [{'text': '有給休暇は三日前までに申請します。', 'evidence': [{'source_id': 1, 'quote': data['sources'][0]['text']}]}]}
        return {'choices': [{'message': {'content': json.dumps(content, ensure_ascii=False)}}]}
    monkeypatch.setattr(OpenAICompatibleProvider, 'request', japanese_provider)
    configure_api(client)
    upload(client)
    result = ask(client, '有給休暇はどのように申請しますか？')
    assert result['answer'].startswith('有給休暇')
    chat_payload = next(payload for endpoint, payload in calls if endpoint == '/chat/completions')
    assert '日语' in chat_payload['messages'][0]['content']


def test_streamed_upload_is_limited_without_content_length(client, monkeypatch):
    monkeypatch.setattr('backend.main.MAX_BYTES', 512)
    def stream():
        yield b'x' * (512 * 1024)
        yield b'x' * (512 * 1024 + 1024)
    response = client.post('/api/documents', content=stream(), headers={'Content-Type':'multipart/form-data; boundary=test'})
    assert response.status_code == 413
    assert client.get('/api/health').json()['documents'] == 0


def test_upload_queue_does_not_block_health(client, monkeypatch):
    release = threading.Event()
    def slow_process(doc_id):
        assert release.wait(10)
    monkeypatch.setattr(client.app.state.knowledge, 'process', slow_process)
    try:
        response = client.post('/api/documents/sample')
        assert response.status_code == 202
        assert client.get('/api/health').status_code == 200
        assert client.get('/api/documents').json()['documents'][0]['status'] == 'queued'
    finally:
        release.set()
        client.app.state.knowledge.wait_for_jobs()


def test_endpoint_dimension_change_marks_old_index_stale(client, monkeypatch):
    mock_provider(monkeypatch)
    configure_api(client)
    doc_id = upload(client)
    monkeypatch.setattr(OpenAICompatibleProvider, 'request', lambda *args, **kwargs: {'data':[{'index':0,'embedding':[1,0,0]}]})
    assert ask(client)['refused']
    doc = client.get('/api/documents').json()['documents'][0]
    assert doc['status'] == 'stale' and doc['needs_reindex']
    mock_provider(monkeypatch)
    assert client.post(f'/api/documents/{doc_id}/retry').status_code == 202
    client.app.state.knowledge.wait_for_jobs()
    assert ask(client)['sources']


def test_provider_http_contract(monkeypatch):
    import httpx
    original_client = httpx.Client
    seen=[]
    def handler(request):
        seen.append(request)
        assert request.headers['authorization'] == 'Bearer test-token'
        assert request.url.path == '/v1/embeddings'
        assert json.loads(request.content)['input'] == ['hello']
        return httpx.Response(200,json={'data':[{'index':0,'embedding':[3,4]}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs))
    with OpenAICompatibleProvider() as provider:
        assert rag.embed(['hello'],Settings(mode='api'),'test-token',provider=provider) == [[0.6,0.8]]
    assert len(seen)==1
