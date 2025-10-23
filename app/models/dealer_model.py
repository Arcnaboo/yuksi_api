from pydantic import BaseModel, constr
from typing import Optional, Literal

AccountType = Literal["bireysel", "kurumsal"]
DealerStatus = Literal["pendingApproval", "active", "inactive"]


# ✅ CREATE
class DealerCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    surname: constr(strip_whitespace=True, min_length=1)
    address: str
    account_type: AccountType
    country_id: int
    city_id: int
    state_id: int
    tax_office: Optional[str] = None
    phone: Optional[str] = None
    tax_number: Optional[str] = None
    iban: Optional[str] = None
    resume: Optional[str] = None
    status: DealerStatus = "pendingApproval"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mehmet",
                "surname": "Yılmaz",
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
        }


# ✅ UPDATE
class DealerUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    address: Optional[str]
    account_type: Optional[AccountType]
    country_id: Optional[int]
    city_id: Optional[int]
    state_id: Optional[int]
    tax_office: Optional[str]
    phone: Optional[str]
    tax_number: Optional[str]
    iban: Optional[str]
    resume: Optional[str]
    status: Optional[DealerStatus]


# ✅ STATUS UPDATE
class DealerStatusUpdate(BaseModel):
    status: DealerStatus
