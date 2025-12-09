from typing import List
from uuid import UUID
from pydantic import BaseModel

class VehicleRequest(BaseModel):
    year: int
    model: str
    make: str
    plate: str
    type: str
    features: List[str]
    driver_id: str | None

class VehicleResponse(BaseModel):
    id: str
    year: int
    model: str
    make: str
    plate: str
    driver_id: str
    type: str
    features: List[str]

class VehicleTypeRequest(BaseModel):
    type: str
    description: str

class VehicleTypeResponse(BaseModel):
    id: str
    type: str
    description: str
    created_at: str

class VehicleFeatureRequest(BaseModel):
    feature: str
    description: str

class VehicleFeatureResponse(BaseModel):
    id: str
    feature: str
    description: str
    created_at: str