from pydantic import BaseModel, EmailStr

class UserRegisterReq(BaseModel):
    email: EmailStr
    password: str
    phone: str
    first_name: str
    last_name: str

class UserLoginReq(BaseModel):
    email: EmailStr
    password: str

