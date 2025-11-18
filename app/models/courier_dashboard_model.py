from pydantic import BaseModel
from typing import Optional


class CourierDashboardResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

