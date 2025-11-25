from pydantic import BaseModel, Field, conlist, ConfigDict, model_validator
from typing import Optional, Literal, List, Dict, Any
from uuid import UUID




class ExtraService(BaseModel):
    """Ek hizmet modeli"""
    serviceId: int = Field(..., description="Ek hizmet ID")
    name: str = Field(..., description="Ek hizmet adı")
    price: float = Field(..., ge=0, description="Ek hizmet ücreti")


class AdminJobCreate(BaseModel):
    """Admin tarafından manuel yük oluşturma modeli (fileId destekli)"""
    deliveryType: Literal["immediate", "scheduled"] = Field(..., description="Teslimat tipi")
    carrierType: Literal["courier"] = Field(..., description="Taşıyıcı tipi (şimdilik sadece kurye)")
    
    # ✅ YENİ: Araç seçimi (3 farklı yöntem - en az biri dolu olmalı)
    vehicleProductId: Optional[UUID] = Field(
        None, 
        description="Araç ürün ID'si (yeni sistem - önerilen)"
    )
    vehicleTemplate: Optional[Literal["motorcycle", "minivan", "panelvan", "kamyonet", "kamyon"]] = Field(
        None,
        description="Araç kalıbı (template + features + capacity ile birlikte kullanılır)"
    )
    vehicleFeatures: Optional[List[Literal["cooling", "withSeats", "withoutSeats"]]] = Field(
        None,
        description="Araç özellikleri (vehicleTemplate ile birlikte kullanılır)"
    )
    capacityOptionId: Optional[UUID] = Field(
        None,
        description="Kapasite baremi ID'si (vehicleTemplate ile birlikte kullanılır)"
    )
    vehicleType: Optional[str] = Field(
        None,
        description="Araç türü (eski sistem - backward compatibility için)"
    )
    
    pickupAddress: str = Field(..., description="Gönderim başlangıç adresi")
    pickupCoordinates: conlist(float, min_length=2, max_length=2) = Field(..., description="[lat, long]")
    
    dropoffAddress: str = Field(..., description="Teslimat adresi")
    dropoffCoordinates: conlist(float, min_length=2, max_length=2) = Field(..., description="[lat, long]")
    
    specialNotes: Optional[str] = Field(None, description="Özel müşteri talepleri")
    campaignCode: Optional[str] = Field(None, description="Kampanya kodu")
    
    extraServices: Optional[List[ExtraService]] = Field(default_factory=list, description="Ekstra hizmet listesi")
    extraServicesTotal: Optional[float] = Field(0, description="Ekstra hizmet toplamı")
    totalPrice: Optional[float] = Field(None, description="Toplam fiyat (opsiyonel - backend hesaplayabilir)")
    
    paymentMethod: Literal["cash", "card", "transfer"] = Field(..., description="Ödeme yöntemi")
    imageFileIds: Optional[List[str]] = Field(default_factory=list, description="Yük görsellerinin fileId listesi")
    
    deliveryDate: Optional[str] = Field(None, description="Gönderi tarihi (DD.MM.YYYY formatında, örn: 31.10.2025)")
    deliveryTime: Optional[str] = Field(None, description="Gönderi saati (HH:MM formatında, örn: 11:52)")

    @model_validator(mode='after')
    def validate_vehicle_selection(self):
        """Araç seçimi validasyonu - en az bir yöntem kullanılmalı"""
        has_vehicle_product_id = self.vehicleProductId is not None
        has_template_selection = self.vehicleTemplate is not None
        has_old_vehicle_type = self.vehicleType is not None
        
        if not (has_vehicle_product_id or has_template_selection or has_old_vehicle_type):
            raise ValueError(
                "Araç seçimi yapılmalıdır: "
                "vehicleProductId, vehicleTemplate veya vehicleType alanlarından biri dolu olmalıdır"
            )
        
        # Eğer vehicleTemplate seçildiyse, capacityOptionId de olmalı
        if has_template_selection and not self.capacityOptionId:
            raise ValueError(
                "vehicleTemplate seçildiyse capacityOptionId de belirtilmelidir"
            )
        
        return self

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "deliveryType": "immediate",
                "carrierType": "courier",
                "vehicleProductId": "c939f94c-cf9a-49cf-930d-f5ea6c475b1d",
                "pickupAddress": "Bursa OSB, Nilüfer/Bursa",
                "pickupCoordinates": [40.192, 29.067],
                "dropoffAddress": "Gözede, 16450 Kestel/Bursa",
                "dropoffCoordinates": [40.198, 29.071],
                "specialNotes": "Soğuk zincir korunmalı",
                "campaignCode": "YUKSI2025",
                "extraServices": [
                    {"serviceId": 1, "name": "Durak Ekleme", "price": 100}
                ],
                "extraServicesTotal": 100,
                "totalPrice": 850,
                "paymentMethod": "cash",
                "imageFileIds": [
                    "f232f2b8-2e42-46f8-b3b5-d91a62f8b001",
                    "a93cf2a9-8fd1-45b3-982a-cb67a86c90e2"
                ]
            }
        }
    )
class AdminJobListFilter(BaseModel):
    """Admin job listeleme filtre modeli"""
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)
    deliveryType: Optional[Literal["immediate", "scheduled"]] = None
    carrierType: Optional[str] = None

class AdminJobUpdateReq(BaseModel):
    """Admin job güncelleme modeli"""
    deliveryType: Optional[Literal["immediate", "scheduled"]] =  None
    carrierType: Optional[str] = None
    vehicleType: Optional[str] = None
    pickupAddress: Optional[str] = None
    dropoffAddress: Optional[str] = None
    specialNotes: Optional[str] = None
    campaignCode: Optional[str] = None
    extraServices: Optional[List[Dict[str, Any]]] = None
    extraServicesTotal: Optional[float] = None
    totalPrice: Optional[float] = None
    paymentMethod: Optional[str] = None
    imageFileIds: Optional[List[str]] = None
    deliveryDate: Optional[str] = Field(None, description="Gönderi tarihi (DD.MM.YYYY formatında, örn: 31.10.2025)")
    deliveryTime: Optional[str] = Field(None, description="Gönderi saati (HH:MM formatında, örn: 11:52)")    