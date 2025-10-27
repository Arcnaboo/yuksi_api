from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class RestaurantPackagePriceBase(BaseModel):
    id: Optional[UUID] = None  # ✅ artık UUID
    restaurant_id: UUID
    unit_price: float
    min_package: Optional[int] = None
    max_package: Optional[int] = None
    note: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "b8dc4894-3183-42f2-b4bc-6d3fd00df0b6",
                "unit_price": 80.0,
                "min_package": 10,
                "max_package": 300,
                "note": "Açılış promosyonu"
            }
        }
