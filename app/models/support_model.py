from pydantic import BaseModel, EmailStr, Field

class SupportUserCreate(BaseModel):
    """Çağrı merkezi üyesi oluşturma modeli (Admin tarafından)"""
    first_name: str = Field(..., min_length=2, max_length=200, description="Ad")
    last_name: str = Field(..., min_length=2, max_length=200, description="Soyad")
    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(..., min_length=6, max_length=128, description="Şifre")
    phone: str = Field(..., min_length=7, max_length=20, description="Telefon numarası")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Ahmet",
                "last_name": "Yılmaz",
                "email": "ahmet@yuksi.com",
                "password": "Sifre123!",
                "phone": "+905551234567"
            }
        }
    }

