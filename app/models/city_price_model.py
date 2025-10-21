from pydantic import BaseModel

class CityPriceCreate(BaseModel):
    route_name: str
    country_id: int
    state_id: int
    courier_price: float
    minivan_price: float
    panelvan_price: float
    kamyonet_price: float
    kamyon_price: float

class CityPriceUpdate(BaseModel):
    route_name: str | None = None
    country_id: int | None = None
    state_id: int | None = None
    courier_price: float | None = None
    minivan_price: float | None = None
    panelvan_price: float | None = None
    kamyonet_price: float | None = None
    kamyon_price: float | None = None
from pydantic import BaseModel

class CityPriceBase(BaseModel):
    route_name: str
    country_id: int
    state_id: int
    city_id: int
    courier_price: float
    minivan_price: float
    panelvan_price: float
    kamyonet_price: float
    kamyon_price: float

    class Config:
        json_schema_extra = {
            "example": {
                "route_name": "İstanbul - Ankara",
                "country_id": 1,
                "state_id": 34,
                "city_id": 6,
                "courier_price": 100,
                "minivan_price": 200,
                "panelvan_price": 300,
                "kamyonet_price": 400,
                "kamyon_price": 500
            }
        }
