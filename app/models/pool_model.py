from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from decimal import Decimal

class PoolPushReq(BaseModel):
    order_id: UUID
    message: str | None = None

class PoolOrderRes(BaseModel):
    order_id: UUID
    message: str | None = None
    order_code: str
    order_status: str
    order_type: str
    order_created_at: datetime
    order_updated_at: datetime
    delivery_address: str | None = None
    pickup_lat: Decimal
    pickup_lng: Decimal
    dropoff_lat: Decimal
    dropoff_lng: Decimal
    customer_name: str | None = None
    customer_phone: str | None = None
    amount: Decimal
    restaurant_name: str
    restaurant_address: str
    restaurant_phone: str