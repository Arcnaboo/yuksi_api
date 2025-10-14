from pydantic import BaseModel
from typing import Optional

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
