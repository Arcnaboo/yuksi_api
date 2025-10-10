from typing import Optional
from pydantic import BaseModel, ConfigDict


class CountryOut(BaseModel):
    id: int
    name: str
    iso2: Optional[str] = None
    iso3: Optional[str] = None
    phonecode: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 215,
                "name": "Türkiye",
                "iso2": "TR",
                "iso3": "TUR",
                "phonecode": "90",
            }
        }
    )


class StateOut(BaseModel):
    id: int
    name: str
    country_id: int
    country_code: Optional[str] = None
    iso2: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1234,
                "name": "İstanbul",
                "country_id": 215,
                "country_code": "TR",
                "iso2": "34",
            }
        }
    )


class CityOut(BaseModel):
    id: int
    name: str
    state_id: int
    state_code: Optional[str] = None
    country_id: int
    country_code: Optional[str] = None
    timezone: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 98765,
                "name": "Kadıköy",
                "state_id": 1234,
                "state_code": "34",
                "country_id": 215,
                "country_code": "TR",
                "timezone": "Europe/Istanbul",
            }
        }
    )