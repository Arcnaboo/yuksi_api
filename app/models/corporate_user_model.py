from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class CorporateUserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email adresi")
    password: str = Field(..., min_length=5, description="Şifre")
    phone: str = Field(..., min_length=7, description="Telefon numarası")
    first_name: str = Field(..., min_length=1, description="Ad")
    last_name: str = Field(..., min_length=1, description="Soyad")
    
    model_config = ConfigDict(extra="forbid")


class CorporateUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(extra="forbid")


class CorporateUserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: str

