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
