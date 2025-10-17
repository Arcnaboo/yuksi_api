from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CarrierTypeCreate(BaseModel):
    name: str
    start_km: int
    start_price: float
    km_price: float
    image_file_id: Optional[UUID] = None  # Resim yüklenirse file_id gelecek

class CarrierTypeResponse(BaseModel):
    id: UUID
    name: str
    start_km: int
    start_price: float
    km_price: float
    image_url: Optional[str] = None
    created_at: str

class CarrierTypeUpdate(BaseModel):
    name: Optional[str] = None
    start_km: Optional[int] = None
    start_price: Optional[float] = None
    km_price: Optional[float] = None
    image_file_id: Optional[UUID] = None
