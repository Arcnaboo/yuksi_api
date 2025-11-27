from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional


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
    """Admin tarafından kullanıcıya (Corporate veya Dealer) komisyon oranı belirleme modeli"""
    commissionRate: float = Field(..., ge=0, le=100, description="Komisyon oranı (yüzde, 0-100 arası)")
    description: Optional[str] = Field(None, description="Komisyon oranı açıklaması")
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

