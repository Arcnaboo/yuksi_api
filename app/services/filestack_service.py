# app/services/filestack_service.py
import io
from filestack import Client
from app.utils.config import get_filestack_api_key

class FilestackService:
    def __init__(self) -> None:
        self._client = Client(get_filestack_api_key())

    def upload_bytes(self, data: bytes, filename: str, mimetype: str) -> dict:
        handle = self._client.upload(
            file_obj=io.BytesIO(data)
        )
        # Normalize filestack handle -> dict
        url = getattr(handle, "url", None) or f"https://cdn.filestackcontent.com/{getattr(handle, 'handle', '')}"
        meta = {
            "url": url,
            "size": getattr(handle, "size", None),
            "type": mimetype,
            "filename": getattr(handle, "filename", None) or filename,
            "key": getattr(handle, "handle", None) or getattr(handle, "key", None),
        }
        if not meta["url"] or not meta["key"]:
            raise RuntimeError("Filestack did not return expected metadata")
        return meta