from pydantic import BaseModel, EmailStr, Field

class AdminRegisterReq(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=200)
    last_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
