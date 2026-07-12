from fastapi import HTTPException, status

from app.core.config import get_settings


def validate_upload_text(raw_content: str) -> None:
    if not raw_content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Evidence content is empty")
    max_bytes = get_settings().max_upload_bytes
    if len(raw_content.encode("utf-8")) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Evidence exceeds size limit")

