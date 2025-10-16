from fastapi import UploadFile, HTTPException
from app.services.filestack_service import FilestackService
from ..utils.database import db_cursor
from .filestack_service import FilestackService

async def handle_upload(user_id: str, file: UploadFile) -> dict:
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    fs = FilestackService()
    meta = fs.upload_bytes(
        data=data,
        filename=file.filename,
        mimetype=file.content_type or "application/octet-stream",
    )

        # DB insert with plain SQL (no ORM)
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO files (user_id, image_url, size, mime_type, filename, key)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user_id,
                meta["url"],
                meta.get("size"),
                meta.get("type"),
                meta.get("filename"),
                meta.get("key"),
            ),
        )
        new_id = cur.fetchone()[0]

    return {"id": str(new_id)}

def get_public_url(file_id: str) -> str:
    """
    Public CDN URL üretir. Eğer gerçek CDN varsa base_url'i ona göre değiştir.
    """
    BASE_URL = "https://cdn.yuksi.com/files"
    return f"{BASE_URL}/{file_id}"
