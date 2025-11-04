from pydantic import BaseModel
from typing import Optional

class CreateMenuReq(BaseModel):
    name: str
    info: str
    price: float
    image_url: str

class UpdateMenuReq(CreateMenuReq):
    name: str
    info: str
    price: float
    image_url: str

class MenuResponse(BaseModel):
    id: str
    name: str
    info: str
    price: float
    image_url: str
    restaurant_id: str