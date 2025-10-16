from pydantic import BaseModel
from typing import Optional

class GeneralSettingCreate(BaseModel):
    app_name: str
    app_title: str
    keywords: str
    email: str
    whatsapp: str
    address: str
    map_embed_code: str
    logo_path: Optional[str]  # ✅ file_id gelecek

class GeneralSettingUpdate(BaseModel):
    id: str
    app_name: Optional[str] = None
    app_title: Optional[str] = None
    keywords: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    address: Optional[str] = None
    map_embed_code: Optional[str] = None
    logo_path: Optional[str] = None  # ✅ file_id
