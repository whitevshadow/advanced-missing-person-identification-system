from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from ..config import settings


def save_upload(upload: UploadFile, category: str) -> str:
    suffix = Path(upload.filename or "upload.jpg").suffix or ".jpg"
    target_dir = Path(settings.upload_dir) / category
    target_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid4().hex}{suffix.lower()}"
    target_path = target_dir / file_name

    with target_path.open("wb") as out_file:
        out_file.write(upload.file.read())

    return str(target_path).replace("\\", "/")
