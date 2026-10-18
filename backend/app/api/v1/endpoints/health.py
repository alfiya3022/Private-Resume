import shutil
import httpx
from fastapi import APIRouter, status
from app.core.config import settings
from app.core.database import check_db_connection

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint verifying core subsystem statuses."""
    db_connected = check_db_connection()

    
    # Check Ollama connectivity
    ollama_status = "unavailable"
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/version")
            if resp.status_code == 200:
                ollama_status = "connected"
    except Exception:
        ollama_status = "unreachable"

    # Check LaTeX pdflatex availability
    pdflatex_path = shutil.which("pdflatex")
    latex_status = "available" if pdflatex_path else "not_installed"

    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "subsystems": {
            "database": "connected" if db_connected else "disconnected",
            "ollama": ollama_status,
            "latex": latex_status,
        }
    }
