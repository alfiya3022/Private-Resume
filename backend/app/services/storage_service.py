import os
import re
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit


class StorageService:
    def __init__(self, base_dir: str = settings.STORAGE_DIR):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_dir(self, user_id: int) -> Path:
        user_dir = (self.base_dir / "resumes" / str(user_id)).resolve()
        # Security: Prevent directory traversal outside base_dir
        if not str(user_dir).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid storage path access attempt",
            )
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def _sanitize_filename(self, filename: str) -> str:
        # Keep base name only
        clean = os.path.basename(filename)
        clean = re.sub(r"[^\w\.-]", "_", clean)
        return clean

    async def save_resume_file(self, user_id: int, file: UploadFile) -> tuple[str, int]:
        """Validates and saves a candidate PDF file to local storage."""
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files (.pdf) are supported for resume upload.",
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds maximum allowed limit (10MB).",
            )

        user_dir = self._get_user_dir(user_id)
        safe_name = f"{uuid.uuid4().hex[:8]}_{self._sanitize_filename(file.filename)}"
        target_path = user_dir / safe_name

        with open(target_path, "wb") as f:
            f.write(content)

        return str(target_path), file_size

    def delete_file(self, file_path: str) -> bool:
        """Safely removes a file from local storage."""
        try:
            path = Path(file_path).resolve()
            if str(path).startswith(str(self.base_dir)) and path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False


storage_service = StorageService()
