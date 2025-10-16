from pydantic import BaseModel
from typing import Optional


class PackageCreate(BaseModel):
    carrier:str
    days:int
    price:float

class PackageUpdate(BaseModel):
    id:str
    carrier: Optional[str]=None
    days:Optional[int]=None
    price:Optional[float]=None