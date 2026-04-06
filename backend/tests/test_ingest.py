"""Tests for the /api/ingest endpoint."""
import io
from fastapi.testclient import TestClient


def test_ingest_txt_file(client: TestClient) -> None:
    content = b"This is a test document with some content."
    response = client.post(
        "/api/ingest",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["filename"] == "test.txt"
    assert data["chunks_created"] == 5  # mocked


def test_ingest_unsupported_type(client: TestClient) -> None:
    content = b"<html><body>Cannot ingest html</body></html>"
    response = client.post(
        "/api/ingest",
        files={"file": ("page.html", io.BytesIO(content), "text/html")},
    )
    assert response.status_code == 415


def test_ingest_requires_auth(unauthed_client: TestClient) -> None:
    content = b"hello"
    response = unauthed_client.post(
        "/api/ingest",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 401
