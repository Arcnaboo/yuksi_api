from pydantic import BaseModel

class PoolPushReq(BaseModel):
    order_id: str
    message: str | None = None

class PoolOrderModel(BaseModel):
    id: str
    order_id: str
    restaurant_id: str
    created_at: str