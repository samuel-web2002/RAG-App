"""Shared pytest fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import create_app
from app.rag.pipeline import RAGPipeline


@pytest.fixture
def mock_pipeline() -> MagicMock:
    pipeline = MagicMock(spec=RAGPipeline)
    pipeline.query = AsyncMock(
        return_value={
            "answer": "This is a mocked answer.",
            "source_documents": [],
        }
    )
    pipeline.ingest = MagicMock(return_value=5)
    pipeline.list_documents = MagicMock(return_value=[])
    pipeline.delete_document = MagicMock(return_value=3)
    return pipeline


@pytest.fixture
def client(mock_pipeline: MagicMock) -> TestClient:
    app = create_app()
    app.state.pipeline = mock_pipeline
    return TestClient(app, headers={"X-API-Key": "dev-secret-change-me"})


@pytest.fixture
def unauthed_client(mock_pipeline: MagicMock) -> TestClient:
    app = create_app()
    app.state.pipeline = mock_pipeline
    return TestClient(app)
