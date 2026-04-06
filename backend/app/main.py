"""FastAPI application factory with lifespan context."""
import structlog
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents, ingest
from app.config import get_settings
from app.middleware.auth import APIKeyMiddleware
from app.models.schemas import HealthResponse
from app.rag.pipeline import RAGPipeline

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise resources at startup; clean up on shutdown."""
    settings = get_settings()
    logger.info("Starting RAG Chatbot API", version=settings.app_version)

    app.state.pipeline = RAGPipeline(settings)
    logger.info("RAGPipeline ready")

    yield

    logger.info("Shutting down RAG Chatbot API")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production RAG Chatbot API — upload documents and chat with them using GPT-4o."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auth (after CORS so preflight OPTIONS bypass auth)
    app.add_middleware(APIKeyMiddleware)

    # Routers
    app.include_router(chat.router)
    app.include_router(ingest.router)
    app.include_router(documents.router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", version=settings.app_version)

    return app


app = create_app()
