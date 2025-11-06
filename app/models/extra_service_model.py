from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class ExtraServiceCreate(BaseModel):
    service_name: str = Field(..., alias="serviceName")
    carrier_type: str = Field(..., alias="carrierType")
    price: Decimal

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "serviceName": "Ekstra Paket Taşıma",
                "carrierType": "courier",
                "price": 12.5
            }
        }

class ExtraServiceUpdate(BaseModel):
    service_name: Optional[str] = Field(None, alias="serviceName")
    carrier_type: Optional[str] = Field(None, alias="carrierType")
    price: Optional[Decimal]

    class Config:
        populate_by_name = True


class ExtraServiceResponse(BaseModel):
    id: str
    serviceName: str = Field(..., alias="service_name")
    carrierType: str = Field(..., alias="carrier_type")
    price: Decimal
