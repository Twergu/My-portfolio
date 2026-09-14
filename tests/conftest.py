"""Unit/contract tests never inherit a user's paid API credentials."""
import os

import httpx
import pytest

# Set these before test-module imports cause config.py to load .env. dotenv
# does not override an existing variable, including the intentionally empty key.
os.environ['RAG_API_KEY'] = ''
os.environ['RAG_MODE'] = 'local'
os.environ['RAG_BASE_URL'] = 'https://api.openai.com/v1'
os.environ['RAG_CHAT_MODEL'] = 'gpt-4o-mini'
os.environ['RAG_VERIFIER_MODEL'] = ''
os.environ['RAG_VERIFICATION_MODE'] = 'strict'
os.environ['RAG_DATABASE_URL'] = ''
os.environ['RAG_DATABASE_PASSWORD_FILE'] = ''


@pytest.fixture(autouse=True)
def prevent_paid_http_calls(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError('Tests must inject MockTransport; real HTTP calls are forbidden.')
    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', deny)
