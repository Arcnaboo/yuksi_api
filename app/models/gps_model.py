from pydantic import BaseModel, Field
from uuid import UUID

class GPSUpdateRequest(BaseModel):
    driver_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class GPSData(BaseModel):
    driver_id: str
    latitude: float
    longitude: float
    updated_at: str
