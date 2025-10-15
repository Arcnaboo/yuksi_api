from pydantic import BaseModel, EmailStr

class RegisterReq(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class RefreshReq(BaseModel):
    refreshToken: str

class LogoutReq(BaseModel):
    refreshToken: str