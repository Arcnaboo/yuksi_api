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
