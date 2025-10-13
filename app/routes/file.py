from fastapi import APIRouter, UploadFile, File, Form
from app.controllers.file_controller import handle_upload

router = APIRouter(prefix="/file", tags=["File"]) 

@router.post("/upload")
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    # Tüm iş mantığı controller'da
    return await handle_upload(user_id=user_id, file=file)