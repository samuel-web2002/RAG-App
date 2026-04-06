"""Documents API router — GET/DELETE /api/documents."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.schemas import DeleteResponse, DocumentInfo, DocumentListResponse
from app.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/documents", tags=["documents"])
logger = structlog.get_logger(__name__)


def get_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.pipeline  # type: ignore[no-any-return]


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> DocumentListResponse:
    """List all ingested documents."""
    docs = pipeline.list_documents()
    return DocumentListResponse(
        documents=[DocumentInfo(**d) for d in docs],
        total=len(docs),
    )


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(
    doc_id: str,
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> DeleteResponse:
    """Delete all chunks for a specific document."""
    try:
        deleted = pipeline.delete_document(doc_id)
    except Exception as exc:
        logger.error("Delete error", doc_id=doc_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {exc}",
        ) from exc

    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{doc_id}' not found.",
        )

    return DeleteResponse(status="success", deleted_chunks=deleted)
