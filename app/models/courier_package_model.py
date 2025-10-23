from pydantic import BaseModel, condecimal, constr
from typing import Optional

# ✅ CREATE
class CourierPackageCreate(BaseModel):
    package_name: constr(strip_whitespace=True, min_length=2)
    description: Optional[str] = None
    price: condecimal(gt=0)
    duration_days: int

    class Config:
        json_schema_extra = {
            "example": {
                "package_name": "Weekly Package",
                "description": "Work anytime for 7 days and catch opportunities!",
                "price": 1500.00,
                "duration_days": 7
            }
        }

# ✅ UPDATE
class CourierPackageUpdate(BaseModel):
    package_name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    duration_days: Optional[int]
