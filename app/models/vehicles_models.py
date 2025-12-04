from uuid import UUID
from pydantic import BaseModel

class VehicleRequest(BaseModel):
    year: int
    model: str
    licance_plate: str
    color: str | None
    driver_id: str | None
    vehicle_volume: str
    weight_capacity: str
    is_shared: bool
    vehicle_type: str
    alias: str | None
    files: dict[str, str]
    features: list[str]

class VehicleResponse(BaseModel):
    id: str
    year: int
    model: str
    licance_plate: str
    color: str | None
    driver_id: str | None
    vehicle_volume: str
    weight_capacity: str
    is_shared: bool
    vehicle_type: str
    alias: str | None
    files: dict[str, str]
    features: list[str]

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
    vehicle_types: list[str] | None

class VehicleFeatureResponse(BaseModel):
    id: str
    feature: str
    description: str
    vehicle_types: list[str] | None
    created_at: str