# app/models/model.py  (Pydantic v2 uyumlu)
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import List, Optional
from enum import Enum
from uuid import UUID

from .order_model import OrderStatus

class CourierRegisterStep1Req(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20, description="E164 veya yerel numara")
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirmPassword: str
    confirmContract: bool
    countryId: int = Field(..., ge=1)

    # Ekstra alanları reddet
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "phone": "5551112233",
                    "firstName": "Ahmet",
                    "lastName": "Yüksel",
                    "email": "ahmet@yuksi.com",
                    "password": "secret123",
                    "confirmPassword": "secret123",
                    "confirmContract": True,
                    "countryId": 90,
                }
            ]
        },
    )

    @model_validator(mode="after")
    def _passwords_and_contract(self):
        # password == confirmPassword
        if self.password != self.confirmPassword:
            raise ValueError("Passwords do not match")
        # sözleşme onayı
        if not self.confirmContract:
            raise ValueError("Contract must be confirmed")
        return self


class CourierRegisterStep2Req(BaseModel):
    workingType: int = Field(..., ge=0, description="0=unknown, 1=full-time, 2=part-time vs.")
    model_config = ConfigDict(extra="forbid")

class DocType(str, Enum):
    VergiLevhasi = "VergiLevhasi"
    EhliyetOn = "EhliyetOn"
    EhliyetArka = "EhliyetArka"
    RuhsatOn = "RuhsatOn"
    RuhsatArka = "RuhsatArka"
    KimlikOn = "KimlikOn"
    KimlikArka = "KimlikArka"

class DocumentItem(BaseModel):
    docType: DocType = Field(..., description="Belge tipi")
    fileId: UUID = Field(..., description="/file/upload sonucunda dönen dosya UUID'si")

class CourierRegisterStep3Req(BaseModel):
    vehicleType: int = Field(..., ge=0)
    vehicleCapacity: int = Field(..., ge=0)
    stateId: int = Field(..., ge=1)
    vehicleYear: int = Field(..., ge=1900)
    documents: List[DocumentItem] = Field(default_factory=list)
    dealer_id: Optional[UUID] = Field(None, description="Opsiyonel bayi ID'si")
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "vehicleType": 0,
                    "vehicleCapacity": 100,
                    "stateId": 34,
                    "dealer_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "vehicleYear": 2020,
                    "documents": [
                        {"docType": "VergiLevhasi", "fileId": "c9c9e6f4-9db9-4b1a-8f90-7c0f1fb2a4cd"},
                        {"docType": "EhliyetOn",  "fileId": "5b2b1f16-6e87-4f2b-9d9e-1e0b0d0a1f22"},
                        {"docType": "EhliyetArka","fileId": "3a1a2b3c-4d5e-6f70-8g90-1h2i3j4k5l6m"},
                        {"docType": "RuhsatOn",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "RuhsatArka",  "fileId": "7n8o9p0q-1r2s-3t4u-5v6w-7x8y9z0a1b2c"},
                        {"docType": "KimlikOn","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                        {"docType": "KimlikArka","fileId": "d3e4f5g6-h7i8-j9k0-l1m2-n3o4p5q6r7s8"},
                    ]
                }
            ]
        },
    )


class CourierProfileUpdateReq(BaseModel):
    firstName: Optional[str] = Field(None, min_length=1)
    lastName:  Optional[str] = Field(None, min_length=1)
    email:     Optional[EmailStr] = None
    phone:     Optional[str] = Field(None, min_length=7, max_length=20)
    countryId: Optional[int] = Field(None, ge=1)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _at_least_one_field(self):
        if not any([self.firstName, self.lastName, self.email, self.phone, self.countryId]):
            raise ValueError("En az bir alan güncellenmelidir")
        return self

class CourierHistory(BaseModel):
    order_id: UUID
    price: float
    date: str
    status: OrderStatus
    payment_status: str
    from_address: str
    to_address: str

class CourierHistoryRes(BaseModel):
    success: bool
    message: str
    data: List[CourierHistory] = Field(default_factory=list)