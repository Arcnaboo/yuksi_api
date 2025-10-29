from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, Literal
from uuid import UUID

CompanyStatus = Literal["active", "inactive"]

class CompanyCreate(BaseModel):
    companyTrackingNo: str = Field(..., min_length=3)
    assignedKilometers: int = Field(..., ge=0)
    specialCommissionRate: float = Field(..., ge=0)
    isVisible: bool = True
    canReceivePayments: bool = True
    cityId: int = Field(..., ge=1)
    stateId: int = Field(..., ge=1)
    location: str
    companyName: str
    companyPhone: str
    description: str

    model_config = ConfigDict(extra="forbid")



class CompanyUpdate(BaseModel):
    companyTrackingNo: Optional[str]
    assignedKilometers: Optional[int]
    consumedKilometers: Optional[int]
    specialCommissionRate: Optional[float]
    isVisible: Optional[bool]
    canReceivePayments: Optional[bool]
    cityId: Optional[int]
    stateId: Optional[int]
    location: Optional[str]
    companyName: Optional[str]
    companyPhone: Optional[str]
    description: Optional[str]
    status: Optional[CompanyStatus]

    model_config = ConfigDict(extra="forbid")


class CompanyListItem(BaseModel):
    id: UUID
    companyTrackingNo: str
    companyName: str
    companyPhone: str
    cityId: int
    stateId: int
    specialCommissionRate: float
    assignedKilometers: int
    consumedKilometers: int
    remainingKilometers: int
    status: CompanyStatus


class CompanyDetail(CompanyListItem):
    isVisible: bool
    canReceivePayments: bool
    location: str
    description: str


# Managers
class ManagerCreate(BaseModel):
    nameSurname: str
    email: EmailStr
    phone: str
    model_config = ConfigDict(extra="forbid")


class ManagerUpdate(BaseModel):
    nameSurname: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    model_config = ConfigDict(extra="forbid")
