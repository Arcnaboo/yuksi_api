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

