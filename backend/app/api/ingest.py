"""Ingest API router — POST /api/ingest."""
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status

from app.models.schemas import IngestResponse
from app.rag.pipeline import RAGPipeline

router = APIRouter(prefix="/api/ingest", tags=["ingest"])
logger = structlog.get_logger(__name__)

MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


def get_pipeline(request: Request) -> RAGPipeline:
    return request.app.state.pipeline  # type: ignore[no-any-return]


@router.post("", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    file: UploadFile,
    pipeline: RAGPipeline = Depends(get_pipeline),
) -> IngestResponse:
    """Upload a document (PDF / TXT / MD) to the vector store."""
    filename = file.filename or "upload"

    # Extension validation
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' not supported. Use: {ALLOWED_EXTENSIONS}",
        )

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({size_mb:.1f} MB). Max size: {MAX_FILE_SIZE_MB} MB",
        )

    try:
        chunks = pipeline.ingest(file_bytes, filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Ingestion error", filename=filename, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        ) from exc

    return IngestResponse(
        status="success",
        filename=filename,
        chunks_created=chunks,
        message=f"Successfully ingested '{filename}' into {chunks} chunks.",
    )
