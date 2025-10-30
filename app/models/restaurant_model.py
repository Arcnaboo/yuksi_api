from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional

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
    latitude: float = Field(..., ge=-90, le=90, description="Restoran enlem")
    longitude: float = Field(..., ge=-180, le=180, description="Restoran boylam")

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
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    openingHour: Optional[str] = None
    closingHour: Optional[str] = None


class RestaurantProfileResponse(BaseModel):
    """Restaurant profil görüntüleme modeli"""
    email: str
    phone: str
    contactPerson: str
    addressLine1: str
    addressLine2: Optional[str] = ""
    openingHour: Optional[str] = None
    closingHour: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RestaurantProfileUpdateReq(BaseModel):
    """Restaurant profil güncelleme modeli"""
    email: Optional[str] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    contactPerson: Optional[str] = Field(None, description="İletişim kişisi")
    addressLine1: Optional[str] = Field(None, description="Adres satır 1", exclude=True)
    addressLine2: Optional[str] = Field(None, description="Adres satır 2", exclude=True)
    full_address: Optional[str] = Field(None, alias="fullAddress", description="Tam adres (addressLine1/2 yerine)")
    openingHour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Açılış saati (HH:MM)")
    closingHour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Kapanış saati (HH:MM)")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "info@sofradan.com",
                "phone": "+905551234567",
                "contactPerson": "Ali Kaya",
                "fullAddress": "FSM Bulv. No:10, Kat:2 Daire:5",
                "openingHour": "09:00",
                "closingHour": "23:00",
                "latitude": 40.195123,
                "longitude": 29.060456
            }
        }
    )



class RestaurantAdminUpdateReq(BaseModel):
    """Admin tarafından restoran güncelleme modeli (tablo yapısına birebir uyumlu)"""
    email: Optional[EmailStr] = Field(None, description="Restoran e-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    country_id: Optional[int] = Field(None, ge=1, description="Ülke ID")
    name: Optional[str] = Field(None, description="Restoran adı")
    contact_person: Optional[str] = Field(None, description="İletişim kişisi")
    tax_number: Optional[str] = Field(None, description="Vergi numarası")
    address_line1: Optional[str] = Field(None, description="Adres satırı 1", exclude=True)
    address_line2: Optional[str] = Field(None, description="Adres satırı 2", exclude=True)
    # Tek alanla tam adres girişi için alias desteği
    full_address: Optional[str] = Field(None, alias="fullAddress", description="Tam adres (address_line1/2 yerine)")
    state_id: Optional[int] = Field(None, ge=1, description="İlçe ID")
    city_id: Optional[int] = Field(None, ge=1, description="Şehir ID")
    opening_hour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Açılış saati (HH:MM)")
    closing_hour: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$", description="Kapanış saati (HH:MM)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Restoran enlem")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Restoran boylam")

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "info@sofradan.com",
                "phone": "+905551234567",
                "country_id": 225,
                "name": "Sofradan Bursa Şubesi",
                "contact_person": "Ali Kaya",
                "tax_number": "1234567890",
                "fullAddress": "Yeni Mahalle 45. Sokak No:12, Kat:1 Daire:3",
                "state_id": 101,
                "city_id": 6,
                "opening_hour": "09:00",
                "closing_hour": "23:00",
                "latitude": 40.195123,
                "longitude": 29.060456
            }
        }
    )