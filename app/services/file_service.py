import uuid
from fastapi import UploadFile, HTTPException
from app.services.filestack_service import FilestackService
from app.utils.database_async import fetch_one
from typing import Dict

# === HANDLE UPLOAD ===
async def handle_upload(user_id: str, file: UploadFile) -> Dict[str, str]:
    try :
        uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")    
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    # Filestack upload
    fs = FilestackService()
    meta = fs.upload_bytes(
        data=data,
        filename=file.filename,
        mimetype=file.content_type or "application/octet-stream",
    )

    # DB kayıt
    query = """
        INSERT INTO files (user_id, image_url, size, mime_type, filename, key)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id;
    """
    row = await fetch_one(
        query,
        user_id,
        meta["url"],
        meta.get("size"),
        meta.get("type"),
        meta.get("filename"),
        meta.get("key"),
    )
    if not row:
        raise HTTPException(status_code=500, detail="File insert failed")

    return {"id": str(row["id"])}


# === GET FILE BY ID ===
async def get_file_by_id(file_id: str) -> Dict:
    """
    File ID ile dosya bilgilerini getirir
    """
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file_id")
    
    query = """
        SELECT 
            id,
            user_id,
            image_url,
            size,
            mime_type,
            filename,
            key,
            uploaded_at,
            is_deleted
        FROM files
        WHERE id = $1::uuid
    """
    
    row = await fetch_one(query, file_id)
    
    if not row:
        raise HTTPException(status_code=404, detail="File not found")
    
    if row.get("is_deleted") is True:
        raise HTTPException(status_code=404, detail="File has been deleted")
    
    return {
        "id": str(row["id"]),
        "user_id": str(row["user_id"]),
        "image_url": row["image_url"],
        "size": row.get("size"),
        "mime_type": row.get("mime_type"),
        "filename": row.get("filename"),
        "key": row.get("key"),
        "uploaded_at": row.get("uploaded_at").isoformat() if row.get("uploaded_at") else None
    }


# === GET PUBLIC URL ===
def get_public_url(file_id: str) -> str:
    """
    Public CDN URL üretir. Gerçek CDN varsa base_url değiştirilebilir.
    """
    BASE_URL = "https://cdn.yuksi.com/files"
    return f"{BASE_URL}/{file_id}"
