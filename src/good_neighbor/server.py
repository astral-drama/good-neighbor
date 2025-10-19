"""FastAPI server for Good Neighbor homepage manager."""

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from good_neighbor.api.favicon import router as favicon_router
from good_neighbor.api.homepages import router as homepages_router
from good_neighbor.api.widgets import router as widgets_router

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Good Neighbor",
    description="Customizable homepage widget manager",
    version="0.1.0",
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (default port)
        "http://localhost:5174",  # Vite dev server (alternative port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(homepages_router)
app.include_router(widgets_router)
app.include_router(favicon_router)


@app.get("/api/health")  # type: ignore[misc]
async def health_check() -> dict[str, Any]:
    """Health check endpoint.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "good-neighbor",
        "version": "0.1.0",
    }


# Static file serving for production
# Define dist_path for use in routes
dist_path = Path(__file__).parent.parent.parent / "dist"

# Mount static assets if they exist
if dist_path.exists() and (dist_path / "assets").exists():
    logger.info("Mounting static assets from %s", dist_path / "assets")
    try:
        app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")
    except RuntimeError:
        logger.warning("Failed to mount assets directory")


# SPA fallback route - serve index.html for root
# Root route must be registered AFTER all API routers
@app.get("/", include_in_schema=False)  # type: ignore[misc]
async def serve_root() -> FileResponse:
    """Serve index.html for the root path.

    Returns:
        FileResponse: The index.html file

    Raises:
        HTTPException: If dist/index.html doesn't exist
    """
    index_path = dist_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    raise HTTPException(
        status_code=503,
        detail="index.html not found - run 'cd frontend && npm run build'",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "good_neighbor.server:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        log_level="info",
    )
