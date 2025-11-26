from app.services import file_service as svc
from fastapi import UploadFile
from typing import Dict

async def handle_upload(user_id: str, file: UploadFile) -> Dict[str, str]:
    return await svc.handle_upload(user_id=user_id, file=file)

async def get_file(file_id: str) -> Dict:
    return await svc.get_file_by_id(file_id)