from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import feedback, missing_persons, sightings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_base_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict:
    return {"status": "healthy"}


app.include_router(missing_persons.router)
app.include_router(sightings.router)
app.include_router(feedback.router)


# Serve built frontend (single-port deployment)
repo_root = Path(__file__).resolve().parents[2]
dist_dir = repo_root / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")


@app.get("/{full_path:path}")
def spa_fallback(full_path: str):
    """Return frontend's index.html for any unknown route (SPA fallback)."""
    index_file = dist_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")
