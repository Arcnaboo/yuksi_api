from app.services import file_service as svc
from fastapi import UploadFile
from typing import Dict

async def handle_upload(user_id: str, file: UploadFile) -> Dict[str, str]:
    return await svc.handle_upload(user_id=user_id, file=file)