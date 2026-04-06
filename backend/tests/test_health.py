"""Tests for the /health endpoint."""
from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_health_no_auth_required(unauthed_client: TestClient) -> None:
    response = unauthed_client.get("/health")
    assert response.status_code == 200
