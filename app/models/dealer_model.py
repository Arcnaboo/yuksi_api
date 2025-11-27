from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, constr

AccountType = Literal["bireysel", "kurumsal"]
DealerStatus = Literal["pendingApproval", "active", "inactive"]


class DealerCreate(BaseModel):
    # Zorunlu alanlar
    name: constr(strip_whitespace=True, min_length=1)
    surname: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    password: constr(min_length=5)  # DB'ye hash olarak yazılacak
    address: str
    account_type: AccountType
    country_id: int
    city_id: int
    state_id: int

    # Opsiyonel alanlar
    tax_office: Optional[str] = None
    phone: Optional[str] = None
    tax_number: Optional[str] = None
    iban: Optional[str] = None
    resume: Optional[str] = None
    status: DealerStatus = "pendingApproval"

    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "name": "Mehmet",
            "surname": "Yılmaz",
            "email": "mehmet@example.com",
            "password": "Sifre123!",
            "address": "Osmangazi / Bursa",
            "account_type": "kurumsal",
            "country_id": 225,
            "city_id": 6,
            "state_id": 101,
            "tax_office": "Osmangazi Vergi Dairesi",
            "phone": "+905551112233",
            "tax_number": "12345678901",
            "iban": "TR330006100519786457841326",
            "resume": "10 yıllık taşımacılık deneyimi",
            "status": "pendingApproval"
        }
    })


class DealerUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None  # email güncellenebilir (benzersizlik kontrolü yapılacak)
    address: Optional[str] = None
    account_type: Optional[AccountType] = None
    country_id: Optional[int] = None
    city_id: Optional[int] = None
    state_id: Optional[int] = None
    tax_office: Optional[str] = None
    phone: Optional[str] = None
    tax_number: Optional[str] = None
    iban: Optional[str] = None
    resume: Optional[str] = None
    status: Optional[DealerStatus] = None

    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "name": "Mehmet",
            "surname": "Yılmaz",
            "email": "mehmet.yilmaz@example.com",
            "address": "Nilüfer / Bursa",
            "status": "active"
        }
    })


class DealerStatusUpdate(BaseModel):
    status: DealerStatus

    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {"status": "active"}
    })


class DealerProfileResponse(BaseModel):
    """Bayi profil görüntüleme modeli"""
    email: str
    phone: Optional[str]
    name: str
    surname: str
    fullAddress: Optional[str] = Field(None, description="Tam adres")
    accountType: Optional[str] = Field(None, description="Hesap tipi (bireysel/kurumsal)")
    countryId: Optional[int] = Field(None, description="Ülke ID")
    stateId: Optional[int] = Field(None, description="İl ID")
    cityId: Optional[int] = Field(None, description="İlçe ID")
    taxOffice: Optional[str] = Field(None, description="Vergi dairesi")
    taxNumber: Optional[str] = Field(None, description="Vergi numarası")
    iban: Optional[str] = Field(None, description="IBAN")
    resume: Optional[str] = Field(None, description="Özgeçmiş")
    commissionRate: Optional[float] = Field(None, description="Komisyon oranı (yüzde)")
    commissionDescription: Optional[str] = Field(None, description="Komisyon oranı açıklaması")
    latitude: Optional[float] = Field(None, description="Enlem")
    longitude: Optional[float] = Field(None, description="Boylam")


class DealerProfileUpdateReq(BaseModel):
    """Bayi profil güncelleme modeli"""
    email: Optional[EmailStr] = Field(None, description="E-posta adresi")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Telefon numarası")
    name: Optional[str] = Field(None, description="Ad")
    surname: Optional[str] = Field(None, description="Soyad")
    fullAddress: Optional[str] = Field(None, alias="fullAddress", description="Tam adres")
    accountType: Optional[AccountType] = Field(None, description="Hesap tipi")
    countryId: Optional[int] = Field(None, ge=1, description="Ülke ID")
    stateId: Optional[int] = Field(None, ge=1, description="İl ID")
    cityId: Optional[int] = Field(None, ge=1, description="İlçe ID")
    taxOffice: Optional[str] = Field(None, description="Vergi dairesi")
    taxNumber: Optional[str] = Field(None, description="Vergi numarası")
    iban: Optional[str] = Field(None, description="IBAN")
    resume: Optional[str] = Field(None, description="Özgeçmiş")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Enlem (-90 ile 90 arası)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Boylam (-180 ile 180 arası)")
    
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "email": "dealer@example.com",
                "phone": "+905551234567",
                "name": "Mehmet",
                "surname": "Yılmaz",
                "fullAddress": "Osmangazi / Bursa",
                "accountType": "kurumsal",
                "countryId": 225,
                "stateId": 101,
                "cityId": 6,
                "taxOffice": "Osmangazi Vergi Dairesi",
                "taxNumber": "12345678901",
                "iban": "TR330006100519786457841326",
                "resume": "10 yıllık taşımacılık deneyimi"
            }
        }
    )