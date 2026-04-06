"""Chat API router — POST /api/chat."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.config import Settings, get_settings
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = structlog.get_logger(__name__)


def get_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.pipeline  # type: ignore[no-any-return]


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    pipeline: RAGPipeline = Depends(get_pipeline),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """Send a message and receive a RAG-grounded answer."""
    try:
        result = await pipeline.query(
            question=body.message,
            session_id=body.session_id,
        )
    except Exception as exc:
        logger.error("Chat error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {exc}",
        ) from exc

    sources = [
        SourceDocument(
            content=doc.page_content,
            metadata=doc.metadata,
        )
        for doc in result["source_documents"]
    ]

    return ChatResponse(
        answer=result["answer"],
        session_id=body.session_id,
        sources=sources,
    )
