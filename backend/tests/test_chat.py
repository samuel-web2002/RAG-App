"""Tests for the /api/chat endpoint."""
from fastapi.testclient import TestClient


def test_chat_returns_answer(client: TestClient) -> None:
    response = client.post("/api/chat", json={"message": "Hello!", "session_id": "test-1"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["session_id"] == "test-1"
    assert isinstance(data["sources"], list)


def test_chat_empty_message_rejected(client: TestClient) -> None:
    response = client.post("/api/chat", json={"message": "", "session_id": "test-1"})
    assert response.status_code == 422


def test_chat_requires_auth(unauthed_client: TestClient) -> None:
    response = unauthed_client.post("/api/chat", json={"message": "Hi", "session_id": "s1"})
    assert response.status_code == 401


def test_chat_uses_default_session(client: TestClient) -> None:
    response = client.post("/api/chat", json={"message": "test"})
    assert response.status_code == 200
    assert response.json()["session_id"] == "default"
