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

from pydantic import BaseModel
from typing import Optional

# ENUM'u burada kaldırıyoruz — integer kabul etsin
class SubSectionCreate(BaseModel):
    title: str
    content_type: int  # ✅ Artık INT kabul edecek
    show_in_menu: bool
    show_in_footer: bool
    content: str

class SubSectionUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content_type: Optional[int] = None  # ✅ INT opsiyonel
    show_in_menu: Optional[bool] = None
    show_in_footer: Optional[bool] = None
    content: Optional[str] = None
