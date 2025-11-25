from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from uuid import UUID
from enum import Enum


class VehicleTemplate(str, Enum):
    MOTORCYCLE = "motorcycle"
    MINIVAN = "minivan"
    PANELVAN = "panelvan"
    KAMYONET = "kamyonet"
    KAMYON = "kamyon"


class VehicleFeature(str, Enum):
    COOLING = "cooling"
    WITH_SEATS = "withSeats"
    WITHOUT_SEATS = "withoutSeats"


class CapacityOption(BaseModel):
    """Kapasite baremi modeli"""
    minWeight: float = Field(..., ge=0, description="Minimum ağırlık (kg)")
    maxWeight: float = Field(..., ge=0, description="Maksimum ağırlık (kg)")
    label: str = Field(..., min_length=1, description="Görünen etiket (örn: '1-5 kg')")

    @model_validator(mode='after')
    def validate_weight_range(self):
        if self.minWeight >= self.maxWeight:
            raise ValueError("minWeight, maxWeight'den küçük olmalıdır")
        return self


class VehicleProductCreate(BaseModel):
    """Yeni araç ürünü oluşturma modeli"""
    productName: str = Field(..., min_length=1, description="Ürün adı (örn: 'Koltuksuz Minivan')")
    # productCode otomatik oluşturulur, manuel girilmez
    productTemplate: Literal["motorcycle", "minivan", "panelvan", "kamyonet", "kamyon"] = Field(
        ..., 
        description="Araç kalıbı"
    )
    capacityOptions: List[CapacityOption] = Field(
        ..., 
        min_length=1, 
        description="Kapasite baremleri (en az 1 adet)"
    )
    vehicleFeatures: List[Literal["cooling", "withSeats", "withoutSeats"]] = Field(
        default_factory=list,
        description="Araç özellikleri"
    )

    @model_validator(mode='after')
    def validate_capacity_overlaps(self):
        """Kapasite baremlerinin çakışmamasını kontrol et"""
        ranges = [(opt.minWeight, opt.maxWeight) for opt in self.capacityOptions]
        
        for i, (min1, max1) in enumerate(ranges):
            for j, (min2, max2) in enumerate(ranges):
                if i != j:
                    # Çakışma kontrolü: iki aralık kesişiyor mu?
                    if not (max1 <= min2 or max2 <= min1):
                        raise ValueError(
                            f"Kapasite baremleri çakışıyor: "
                            f"({min1}-{max1} kg) ve ({min2}-{max2} kg)"
                        )
        return self


class VehicleProductUpdate(BaseModel):
    """Araç ürünü güncelleme modeli"""
    productName: Optional[str] = Field(None, min_length=1)
    # productCode otomatik oluşturulduğu için güncelleme yapılamaz
    productTemplate: Optional[Literal["motorcycle", "minivan", "panelvan", "kamyonet", "kamyon"]] = None
    capacityOptions: Optional[List[CapacityOption]] = None
    vehicleFeatures: Optional[List[Literal["cooling", "withSeats", "withoutSeats"]]] = None
    isActive: Optional[bool] = None


class CapacityOptionResponse(BaseModel):
    """Kapasite baremi response modeli"""
    id: UUID
    minWeight: float
    maxWeight: float
    label: str


class VehicleProductResponse(BaseModel):
    """Araç ürünü response modeli"""
    id: UUID
    productName: str
    productCode: str
    productTemplate: str
    vehicleFeatures: List[str]
    capacityOptions: List[CapacityOptionResponse]
    isActive: bool
    createdAt: str
    updatedAt: str


class VehicleProductListResponse(BaseModel):
    """Araç ürünü liste response modeli"""
    id: UUID
    productName: str
    productCode: str
    productTemplate: str
    vehicleFeatures: List[str]
    isActive: bool
    capacityCount: int  # Kaç tane kapasite seçeneği var
    createdAt: str

