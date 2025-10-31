from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class CompanyPackageCreate(BaseModel):
    carrier_km: int = Field(gt=0)
    requested_km: int = Field(gt=0)
    price: float = Field(gt=0)

class CompanyPackageUpdate(BaseModel):
    carrier_km: Optional[int] = Field(None, gt=0)
    requested_km: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
