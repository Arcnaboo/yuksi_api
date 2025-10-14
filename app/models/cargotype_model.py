from ast import List
from pydantic import BaseModel

class CargoTypeReq(BaseModel):
    name: str
    price: float
    description: str = None

class CargoTypeDataElement(BaseModel):
    id: int
    name: str
    price: float
    description: str = None    

class CargoTypeRes(BaseModel):
    success: bool
    message: str = None
    data: CargoTypeDataElement = None

class CargoTypeListRes(BaseModel):
    success: bool
    message: str = None
    data: list[CargoTypeDataElement] = None        