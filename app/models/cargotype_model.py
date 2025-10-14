from pydantic import BaseModel

class CargoTypeReq(BaseModel):
    name: str
    price: float
    description: str = None

