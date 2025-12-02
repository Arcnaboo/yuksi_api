from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegisterReq(BaseModel):
    email: EmailStr
    password: str
    phone: str
    first_name: str
    last_name: str

class UserLoginReq(BaseModel):
    email: EmailStr
    password: str

class UserProfileResponse(BaseModel):
    """Bireysel kullanıcı profil görüntüleme modeli"""
    email: str
    phone: Optional[str]
    firstName: str
    lastName: str

class UserProfileUpdateReq(BaseModel):
    """Bireysel kullanıcı profil güncelleme modeli"""
    email: Optional[EmailStr] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    firstName: Optional[str] = Field(None, description="Ad")
    lastName: Optional[str] = Field(None, description="Soyad")
    
    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "phone": "+905551234567",
                "firstName": "Ahmet",
                "lastName": "Yılmaz"
            }
        }
    }

