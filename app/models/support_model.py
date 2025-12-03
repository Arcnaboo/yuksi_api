from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class SupportUserCreate(BaseModel):
    """Çağrı merkezi üyesi oluşturma modeli (Admin tarafından)"""
    first_name: str = Field(..., min_length=2, max_length=200, description="Ad")
    last_name: str = Field(..., min_length=2, max_length=200, description="Soyad")
    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(..., min_length=6, max_length=128, description="Şifre")
    phone: str = Field(..., min_length=7, max_length=20, description="Telefon numarası")
    access: List[int] = Field(default=[], description="Erişim modülleri (1-7 arası): 1=Kuryeler, 2=Yükler, 3=Restoranlar, 4=Ödemeler, 5=Taşıyıcılar, 6=Siparişler, 7=Ticari")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Ahmet",
                "last_name": "Yılmaz",
                "email": "ahmet@yuksi.com",
                "password": "Sifre123!",
                "phone": "+905551234567",
                "access": [1, 6]
            }
        }
    }

class SupportUserUpdate(BaseModel):
    """Çağrı merkezi üyesi güncelleme modeli (Admin tarafından)"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Ad")
    last_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Soyad")
    email: Optional[EmailStr] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    is_active: Optional[bool] = Field(None, description="Aktif durumu")
    access: Optional[List[int]] = Field(None, description="Erişim modülleri (1-7 arası): 1=Kuryeler, 2=Yükler, 3=Restoranlar, 4=Ödemeler, 5=Taşıyıcılar, 6=Siparişler, 7=Ticari")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Ahmet",
                "last_name": "Yılmaz",
                "email": "ahmet@yuksi.com",
                "phone": "+905551234567",
                "is_active": True,
                "access": [1, 3, 6]
            }
        }
    }

class SupportPermissionUpdate(BaseModel):
    """Çağrı merkezi üyesi yetki güncelleme modeli (Admin tarafından)"""
    access: List[int] = Field(..., description="Erişim modülleri (1-7 arası): 1=Kuryeler, 2=Yükler, 3=Restoranlar, 4=Ödemeler, 5=Taşıyıcılar, 6=Siparişler, 7=Ticari")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access": [1, 3, 6]
            }
        }
    }

