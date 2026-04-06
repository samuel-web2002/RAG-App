"""Pydantic schemas for request/response models."""
from typing import Literal
from pydantic import BaseModel, Field


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000, description="User message")
    session_id: str = Field(default="default", description="Conversation session identifier")


class SourceDocument(BaseModel):
    content: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[SourceDocument] = []


# ── Ingest ────────────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    status: Literal["success", "error"]
    filename: str
    chunks_created: int
    message: str


# ── Documents ─────────────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    id: str
    filename: str
    source: str
    chunk_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    status: Literal["success", "error"]
    deleted_chunks: int


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
