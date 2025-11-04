from pydantic import BaseModel

class CreateMenuReq(BaseModel):
    name: str
    info: str
    price: float
    image_url: str
    restourant_id: str

class UpdateMenuReq(CreateMenuReq):
    id: str

class MenuResponse(CreateMenuReq):
    id: str