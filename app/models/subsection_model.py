from pydantic import BaseModel
from typing import Optional
from enum import Enum

# ENUM Pydantic uyumlu
class ContentTypeEnum(str, Enum):
    Destek = "Destek"
    Hakkimizda = "Hakkimizda"
    Iletisim = "Iletisim"
    GizlilikPolitikasi = "GizlilikPolitikasi"
    KullanimKosullari = "KullanimKosullari"
    KuryeGizlilikSözlesmesi = "KuryeGizlilikSözlesmesi"
    KuryeTasiyiciSözlesmesi = "KuryeTasiyiciSözlesmesi"

# Create DTO
class SubSectionCreate(BaseModel):
    title: str
    content_type: ContentTypeEnum
    show_in_menu: bool = False
    show_in_footer: bool = False
    content: str

# Update DTO (ID zorunlu)
class SubSectionUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content_type: Optional[ContentTypeEnum] = None
    show_in_menu: Optional[bool] = None
    show_in_footer: Optional[bool] = None
    content: Optional[str] = None
