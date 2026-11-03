"""FastAPI application example for the template.

This is a minimal, production-ready FastAPI app that:
- Responds to HTTP requests
- Provides Kubernetes health check endpoints
- Includes structured logging
- Follows best practices for deployment

To use this:
1. Uncomment FastAPI in pyproject.toml
2. Replace src/template/main.py with this file (or import from here)
3. Run: uv run fastapi dev src/template/app.py
4. Visit: http://localhost:8000/docs
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """Handle app startup and shutdown."""
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Data Engineering Template API",
    description="A minimal FastAPI template for data engineering projects",
    version="0.1.0",
    lifespan=lifespan,
)


# Kubernetes health check endpoints
@app.get("/health", tags=["health"])
async def health() -> JSONResponse:
    """Liveness probe: is the app running."""
    return JSONResponse({"status": "healthy"}, status_code=200)


@app.get("/ready", tags=["health"])
async def ready() -> JSONResponse:
    """Readiness probe: is the app ready to serve traffic."""
    return JSONResponse({"status": "ready"}, status_code=200)


# Example API endpoint
@app.get("/api/v1/hello", tags=["example"])
async def hello(name: str = "World") -> JSONResponse:
    """Return a greeting."""
    logger.info("Hello endpoint called with name: %s", name)
    return JSONResponse(
        {
            "message": f"Hello, {name}!",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> JSONResponse:
    """Define API root endpoint."""
    return JSONResponse(
        {
            "app": "Data Engineering Template API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
        }
    )


if __name__ == "__main__":
    import uvicorn

    # Run with: python -m src.template.app
    # Or: uv run fastapi dev src/template/app.py
    uvicorn.run(
        "src.template.app:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )
