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
    companyTrackingNo: Optional[str] = None
    assignedKilometers: Optional[int] = None
    consumedKilometers: Optional[int] = None
    specialCommissionRate: Optional[float] = None
    isVisible: Optional[bool] = None
    canReceivePayments: Optional[bool] = None
    cityId: Optional[int] = None
    stateId: Optional[int] = None
    location: Optional[str] = None
    companyName: Optional[str] = None
    companyPhone: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CompanyStatus] = None

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
