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
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid")


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
    
    @field_validator('commissionRate')
    @classmethod
    def validate_commission_rate(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Komisyon oranı 0-100 arasında olmalıdır')
        return v
    
    model_config = ConfigDict(extra="forbid")


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
    created_at: str

