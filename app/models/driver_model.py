from pydantic import BaseModel

class VehicleReq(BaseModel):
    make: str
    model: str
    year: int
    plate: str
