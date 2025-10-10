# app/models/model.py  (Pydantic v2 uyumlu)
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

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


class CourierRegisterStep3Req(BaseModel):
    vehicleType: int = Field(..., ge=0)
    vehicleCapacity: int = Field(..., ge=0)
    stateId: int = Field(..., ge=1)
    vehicleYear: int = Field(..., ge=1900)
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {"vehicleType": 0, "vehicleCapacity": 100, "stateId": 34, "vehicleYear": 2020}
            ]
        },
    )
