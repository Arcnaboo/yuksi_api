from uuid import UUID
from pydantic import BaseModel

class PoolPushReq(BaseModel):
    order_id: UUID
    message: str | None = None

class PoolOrderRes(BaseModel):
    order_id: UUID
    message: str | None = None