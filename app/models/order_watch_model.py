from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class OrderWatch(BaseModel):
    order_id: UUID
    restaurant_id: UUID
    avalible_drivers: list[UUID] | None = None
    rejected_drivers: list[UUID] | None = None
    last_check: datetime | None = None
    closed: bool = False
