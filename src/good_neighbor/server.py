"""FastAPI server for Good Neighbor homepage manager."""

import logging
import time
from datetime import datetime, timezone
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

# Track server start time for uptime calculation
SERVER_START_TIME = time.time()

# Get base path from environment for reverse proxy support
import os
BASE_PATH = os.getenv("BASE_PATH", "")

# Create FastAPI app
app = FastAPI(
    title="Good Neighbor",
    description="Customizable homepage widget manager",
    version="0.1.0",
    root_path=BASE_PATH,  # Support reverse proxy with base path
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

    Returns comprehensive health status including:
    - Service status
    - Version
    - Uptime
    - Current timestamp
    - Storage backend status

    Returns:
        dict: Health status information
    """
    # Calculate uptime
    uptime_seconds = time.time() - SERVER_START_TIME
    uptime_hours = uptime_seconds / 3600
    uptime_days = uptime_hours / 24

    # Check storage backend
    storage_status = "unknown"
    try:
        from good_neighbor.storage.yaml_storage import YamlStorage

        storage = YamlStorage()
        # Try to list homepages as a simple health check
        _ = storage.list_homepages()
        storage_status = "healthy"
    except Exception as e:
        logger.warning("Storage health check failed: %s", e)
        storage_status = "unhealthy"

    return {
        "status": "healthy",
        "service": "good-neighbor",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": {
            "seconds": round(uptime_seconds, 2),
            "hours": round(uptime_hours, 2),
            "days": round(uptime_days, 2),
        },
        "storage": {
            "status": storage_status,
        },
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

    # Use port 3001 for development (production uses 3000, default dev was 8000)
    uvicorn.run(
        "good_neighbor.server:app",
        host="0.0.0.0",  # noqa: S104
        port=3001,
        reload=True,
        log_level="info",
    )
