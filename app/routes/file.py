from fastapi import APIRouter, UploadFile, File, Form, Path, Query
from app.controllers.file_controller import handle_upload, get_file, get_files_by_user
from uuid import UUID

router = APIRouter(prefix="/file", tags=["File"]) 

@router.post("/upload")
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    # Tüm iş mantığı controller'da
    return await handle_upload(user_id=user_id, file=file)

@router.post("/upload-multiple")
async def upload_multiple_files(
    user_id: str = Form(...),
    files: list[UploadFile] = File(...),
):
    results = []
    for file in files:
        result = await handle_upload(user_id=user_id, file=file)
        results.append(result)
    return results

@router.get("/{file_id}")
async def get_file_by_id(
    file_id: UUID = Path(..., description="File ID (UUID)")
):
    """
    File ID ile dosya bilgilerini getirir
    """
    return await get_file(str(file_id))

@router.get("/user/{user_id}")
async def get_files_by_user_id(
    user_id: UUID = Path(..., description="User ID (UUID)")
):
    """
    User ID'ye göre kullanıcının yüklediği tüm dosyaları getirir
    """
    return await get_files_by_user(str(user_id))