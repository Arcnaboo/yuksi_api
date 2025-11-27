from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class CorporateUserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email adresi")
    password: str = Field(..., min_length=5, description="Şifre")
    phone: str = Field(..., min_length=7, description="Telefon numarası")
    first_name: str = Field(..., min_length=1, description="Ad")
    last_name: str = Field(..., min_length=1, description="Soyad")
    commissionRate: Optional[float] = Field(None, ge=0, le=100, description="Komisyon oranı (yüzde, 0-100 arası)")
    countryId: Optional[int] = Field(None, ge=1, description="Ülke ID")
    stateId: Optional[int] = Field(None, ge=1, description="İl ID")
    cityId: Optional[int] = Field(None, ge=1, description="İlçe ID")
    addressLine1: Optional[str] = Field(None, description="Adres satırı 1")
    addressLine2: Optional[str] = Field(None, description="Adres satırı 2")
    fullAddress: Optional[str] = Field(None, description="Tam adres (addressLine1/2 yerine)")
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CorporateUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    commissionRate: Optional[float] = Field(None, ge=0, le=100, description="Komisyon oranı (yüzde, 0-100 arası)")
    countryId: Optional[int] = Field(None, ge=1, description="Ülke ID")
    stateId: Optional[int] = Field(None, ge=1, description="İl ID")
    cityId: Optional[int] = Field(None, ge=1, description="İlçe ID")
    addressLine1: Optional[str] = Field(None, description="Adres satırı 1")
    addressLine2: Optional[str] = Field(None, description="Adres satırı 2")
    fullAddress: Optional[str] = Field(None, alias="fullAddress", description="Tam adres (addressLine1/2 yerine)")
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CorporateUserResponse(BaseModel):
    id: str
    email: str
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    commissionRate: Optional[float] = Field(None, description="Komisyon oranı (yüzde)")
    countryId: Optional[int] = Field(None, description="Ülke ID")
    stateId: Optional[int] = Field(None, description="İl ID")
    cityId: Optional[int] = Field(None, description="İlçe ID")
    addressLine1: Optional[str] = Field(None, description="Adres satırı 1")
    addressLine2: Optional[str] = Field(None, description="Adres satırı 2")
    created_at: str


class CommissionRateSet(BaseModel):
    """Admin tarafından kullanıcıya (Corporate veya Dealer) komisyon oranı belirleme/güncelleme modeli"""
    commissionRate: float = Field(..., ge=0, le=100, description="Komisyon oranı (yüzde, 0-100 arası)")
    description: Optional[str] = Field(None, description="Komisyon oranı açıklaması")
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CorporateProfileResponse(BaseModel):
    """Kurumsal kullanıcı profil görüntüleme modeli"""
    email: str
    phone: Optional[str]
    firstName: str
    lastName: str
    fullAddress: Optional[str] = Field(None, description="Tam adres (addressLine1 + addressLine2)")
    countryId: Optional[int] = Field(None, description="Ülke ID")
    stateId: Optional[int] = Field(None, description="İl ID")
    cityId: Optional[int] = Field(None, description="İlçe ID")
    commissionRate: Optional[float] = Field(None, description="Komisyon oranı (yüzde)")
    commissionDescription: Optional[str] = Field(None, description="Komisyon oranı açıklaması")
    latitude: Optional[float] = Field(None, description="Enlem")
    longitude: Optional[float] = Field(None, description="Boylam")


class CorporateProfileUpdateReq(BaseModel):
    """Kurumsal kullanıcı profil güncelleme modeli"""
    email: Optional[EmailStr] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    firstName: Optional[str] = Field(None, description="Ad")
    lastName: Optional[str] = Field(None, description="Soyad")
    fullAddress: Optional[str] = Field(None, alias="fullAddress", description="Tam adres (addressLine1/2 yerine)")
    countryId: Optional[int] = Field(None, ge=1, description="Ülke ID")
    stateId: Optional[int] = Field(None, ge=1, description="İl ID")
    cityId: Optional[int] = Field(None, ge=1, description="İlçe ID")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Enlem (-90 ile 90 arası)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Boylam (-180 ile 180 arası)")
    
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "corporate@example.com",
                "phone": "+905551234567",
                "firstName": "Ahmet",
                "lastName": "Yılmaz",
                "fullAddress": "FSM Bulv. No:10, Kat:2 Daire:5",
                "countryId": 225,
                "stateId": 101,
                "cityId": 6,
                "latitude": 39.9200,
                "longitude": 32.8550
            }
        }
    )

