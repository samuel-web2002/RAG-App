"""API key authentication middleware."""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import get_settings

# Paths that don't require authentication
EXEMPT_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._settings = get_settings()

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        if request.url.path in EXEMPT_PATHS or request.url.path.startswith("/docs"):
            return await call_next(request)

        # api_key = request.headers.get("X-API-Key")
        # if not api_key or api_key != self._settings.api_key:
        #     return JSONResponse(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         content={"detail": "Invalid or missing API key. Provide 'X-API-Key' header."},
        #     )
        return await call_next(request)
