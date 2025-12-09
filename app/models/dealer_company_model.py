from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DealerCreateCompanyReq(BaseModel):
    """Bayi için yeni şirket oluşturma request modeli"""
    companyTrackingNo: str = Field(..., min_length=3, description="Şirket takip numarası (unique)")
    assignedKilometers: int = Field(..., ge=0, description="Atanan kilometre")
    specialCommissionRate: float = Field(..., ge=0, description="Özel komisyon oranı")
    isVisible: bool = Field(True, description="Görünür mü?")
    canReceivePayments: bool = Field(True, description="Ödeme alabilir mi?")
    cityId: int = Field(..., ge=1, description="Şehir ID")
    stateId: int = Field(..., ge=1, description="İl ID")
    location: str = Field(..., description="Konum")
    companyName: str = Field(..., description="Şirket adı")
    companyPhone: str = Field(..., description="Şirket telefonu")
    description: str = Field(..., description="Açıklama")
    
    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "companyTrackingNo": "COMP-2024-001",
            "assignedKilometers": 1000,
            "specialCommissionRate": 15.5,
            "isVisible": True,
            "canReceivePayments": True,
            "cityId": 341,
            "stateId": 34,
            "location": "İstanbul, Kadıköy",
            "companyName": "ABC Lojistik A.Ş.",
            "companyPhone": "+905551112233",
            "description": "Kargo ve lojistik hizmetleri"
        }
    })

