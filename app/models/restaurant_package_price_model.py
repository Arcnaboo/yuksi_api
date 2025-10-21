from pydantic import BaseModel

class RestaurantPackagePriceBase(BaseModel):
    restaurant_id: str
    unit_price: float
    min_package: int | None = None
    max_package: int | None = None
    note: str | None = None

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
