from fastapi.testclient import TestClient
import pytest

# Run tests from repo root with: cd app && python -m pytest (PYTHONPATH=src)
# or from app/src: python -m pytest ../tests (PYTHONPATH=.)
from main import app

client = TestClient(app)

API_PREFIX = "/api/v1"

def test_chat_endpoint():
    response = client.post(
        f"{API_PREFIX}/chat/",
        json={
            "session_id": "test-session",
            "model": "gpt-4o-mini",
            "model_provider": "openai",
            "message": "Hello, how are you?",
        },
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_empty_message():
    response = client.post(
        f"{API_PREFIX}/chat/",
        json={
            "session_id": "test-session",
            "model": "gpt-4o-mini",
            "model_provider": "openai",
            "message": "",
        },
    )
    assert response.status_code == 422  # Validation error