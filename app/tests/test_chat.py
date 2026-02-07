from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post(
        "/api/v1/chat",
        json={"message": "Hello, how are you?"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_empty_message():
    response = client.post(
        "/api/v1/chat",
        json={"message": ""}
    )
    assert response.status_code == 422  # Validation error 