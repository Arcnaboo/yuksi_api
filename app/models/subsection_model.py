from pydantic import BaseModel
from typing import Optional
import enum
class SubSection(BaseModel):
    id: int
    title: str
    contentType: int
    showInMenu: bool
    showInFooter: bool
    content: str
    isActive: bool
    isDeleted: bool

class CreateSubSectionRequest(BaseModel):
    title: str
    contentType: int
    showInMenu: bool
    showInFooter: bool
    content: str

class UpdateSubSectionRequest(CreateSubSectionRequest):
    id: Optional[int] = None



class ContentType(enum.Enum):
    Destek = 1
    Hakkimizda = 2
    Iletisim = 3
    GizlilikPolitikasi = 4
    KullanimKosullari = 5
    KuryeGizlilikSozlesmesi = 6
    KuryeTasiyiciSozlesmesi = 7

    @classmethod
    def labels(cls) -> dict[int, str]:
        """Returns a mapping of enum values to their human-readable labels."""
        return {member.value: member.name for member in cls}

    @classmethod
    def choices(cls) -> list[dict[str, str | int]]:
        """Returns the list in the same structure as the original TS array."""
        return [{"value": m.value, "label": m.name} for m in cls]

