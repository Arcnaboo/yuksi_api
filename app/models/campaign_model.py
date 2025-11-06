from pydantic import BaseModel
from typing import Optional

class CampaignCreate(BaseModel):
    title: str
    discount_rate: float
    rule: Optional[str] = None
    content: Optional[str] = None


class CampaignUpdate(BaseModel):
    title: Optional[str]
    discount_rate: Optional[float]
    rule: Optional[str]
    content: Optional[str]

