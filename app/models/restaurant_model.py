from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID


class RestaurantRegisterReq(BaseModel):
    """Restaurant kayıt request modeli"""
    email: EmailStr
    password: str = Field(..., min_length=5)
    phone: str = Field(..., min_length=7, max_length=20)
    countryId: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    contactPerson: str
    taxNumber: str
    addresLine1: str
    addressLine2: Optional[str] = ""
    cityId: int = Field(..., ge=1)
    stateId: int = Field(..., ge=1)

    model_config = ConfigDict(extra="forbid")


class RestaurantRegisterResponse(BaseModel):
    """Restaurant kayıt response modeli"""
    id: UUID
    email: str
    name: str
    contactPerson: str
    taxNumber: str
    phone: str
    fullAddress: str


class RestaurantListItem(BaseModel):
    """Restaurant liste item modeli"""
    id: UUID
    email: str
    name: str
    contactPerson: str
    taxNumber: str
    phone: str
    fullAddress: str


class RestaurantProfileResponse(BaseModel):
    """Restaurant profil görüntüleme modeli"""
    email: str
    phone: str
    contactPerson: str
    addressLine1: str
    addressLine2: Optional[str] = ""
    openingHour: Optional[str] = None
    closingHour: Optional[str] = None

class RestaurantProfileUpdateReq(BaseModel):
    """Restaurant profil güncelleme modeli"""
    email: Optional[str] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    contactPerson: Optional[str] = Field(None, description="İletişim kişisi")
    addressLine1: Optional[str] = Field(None, description="Adres satır 1")
    addressLine2: Optional[str] = Field(None, description="Adres satır 2")
    openingHour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Açılış saati (HH:MM)")
    closingHour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Kapanış saati (HH:MM)")
    model_config = ConfigDict(extra="forbid")

