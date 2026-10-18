import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import router as api_router
from app.utils.logger import get_logger

logger = get_logger("resumeiq.main")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Explainable ATS Resume Analyzer API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")

# Static frontend serving (for single-service production deployment)
frontend_dist_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist_path.exists() and (frontend_dist_path / "index.html").exists():
    logger.info(f"Serving static frontend build from {frontend_dist_path}")
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_path / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        
        file_target = frontend_dist_path / full_path
        if file_target.is_file():
            return FileResponse(file_target)
        return FileResponse(frontend_dist_path / "index.html")
else:
    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "message": "API is active. Frontend is running in dev mode or not yet built."
        }
