from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class DealerCreateRestaurantReq(BaseModel):
    """Bayi için yeni restoran oluşturma request modeli"""
    email: EmailStr
    password: str = Field(..., min_length=5)
    phone: str
    countryId: int
    name: str
    contactPerson: str
    taxNumber: str
    addresLine1: str  # Typo'lu field name (frontend'den gelen gibi)
    addressLine2: Optional[str] = None
    stateId: int
    cityId: int
    latitude: float
    longitude: float
    
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "email": "restoran@example.com",
            "password": "Sifre123!",
            "phone": "+905551112233",
            "countryId": 225,
            "name": "Lezzet Restoranı",
            "contactPerson": "Ahmet Yılmaz",
            "taxNumber": "1234567890",
            "addresLine1": "Kadıköy",
            "addressLine2": "Sokak No:1",
            "stateId": 34,
            "cityId": 341,
            "latitude": 40.9877,
            "longitude": 29.0264
        }
    })


class DealerLinkRestaurantReq(BaseModel):
    """Mevcut restoranı bayisine bağlama request modeli"""
    restaurant_id: str = Field(..., description="Bağlanacak restoranın UUID'si")
    
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "restaurant_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    })

