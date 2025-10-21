
# app/models/courier_rating_model.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ==================== KURYE ATAMA MODELLERI ====================

class OrderAssignCourierReq(BaseModel):
    courier_id: UUID = Field(..., description="Atanacak kurye ID'si")

# ==================== KURYE PUANLAMA MODELLERI ====================

class CourierRatingCreateReq(BaseModel):
    order_id: UUID = Field(..., description="Sipariş ID'si")
    rating: int = Field(..., ge=1, le=5, description="Puan (1-5 arası)")
    comment: Optional[str] = Field(None, max_length=500, description="Yorum (opsiyonel)")

class CourierRatingUpdateReq(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Puan (1-5 arası)")
    comment: Optional[str] = Field(None, max_length=500, description="Yorum (opsiyonel)")

class CourierRatingResponse(BaseModel):
    id: UUID
    restaurant_id: UUID
    courier_id: UUID
    order_id: UUID
    rating: int
    comment: Optional[str]
    created_at: datetime
    updated_at: datetime

class CourierRatingSummary(BaseModel):
    courier_id: UUID
    courier_name: str
    average_rating: float
    total_ratings: int
    recent_ratings: List[CourierRatingResponse]

class CourierListItem(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    average_rating: Optional[float] = None
    total_ratings: int = 0
