"""FastAPI server for Good Neighbor homepage manager."""

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
# Check if dist directory exists
dist_path = Path(__file__).parent.parent.parent / "dist"
if dist_path.exists():
    logger.info("Serving static files from %s", dist_path)

    # Mount static files
    app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")

    @app.get("/{full_path:path}")  # type: ignore[misc]
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve the SPA for all non-API routes.

        Args:
            full_path: The requested path

        Returns:
            FileResponse: The index.html or requested file
        """
        # If file exists in dist, serve it
        file_path = dist_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for SPA routing
        return FileResponse(dist_path / "index.html")
else:
    logger.warning("dist directory not found at %s - static file serving disabled", dist_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "good_neighbor.server:app",
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=True,
        log_level="info",
    )
