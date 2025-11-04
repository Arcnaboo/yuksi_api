from pydantic import BaseModel

class ExtraServiceCreate(BaseModel):
    service_name: str
    price: float

class ExtraServiceUpdate(BaseModel):
    service_name: str | None = None
    price: float | None = None
