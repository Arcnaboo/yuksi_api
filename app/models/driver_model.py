from pydantic import BaseModel

class Driver(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str