from pydantic import BaseModel, condecimal, constr
from typing import Optional, Union


class CourierPackageSubscriptionCreate(BaseModel):
    courier_id: constr(strip_whitespace=True, min_length=1) 
    package_id: constr(strip_whitespace=True, min_length=1) 

    class Config:
        json_schema_extra = {
            "example": {
                "courier_id": "550e8400-e29b-41d4-a716-446655440000",
                "package_id": "63e90954-2339-4c53-a7e6-f1e23b52e9cc"
               
            }
        }

class CourierPackageSubscriptionUpdate(BaseModel):
    is_active: Optional[bool]

    class Config:
        json_schema_extra = {
            "example": {
                "is_active": False
            }
        }