from pydantic import BaseModel, Field
from decimal import Decimal

class ExtraServiceCreate(BaseModel):
    service_name: str = Field(..., alias="serviceName")
    carrier_type: str = Field(..., alias="carrierType")
    price: Decimal

class ExtraServiceUpdate(BaseModel):
    service_name: str | None = None
    price: float | None = None
