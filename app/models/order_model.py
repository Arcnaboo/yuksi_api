# app/models/order_model.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from enum import Enum
from datetime import datetime

class DeliveryType(str, Enum):
    YERINDE = "yerinde"
    PAKETSERVIS = "paket_servis"
    GEL_AL = "gel_al"

class OrderStatus(str, Enum):
    IPTAL = "iptal"
    HAZIRLANIYOR = "hazirlaniyor"
    SIPARIS_HAVUZA_ATILDI = "siparis_havuza_atildi"
    KURYEYE_ISTEK_ATILDI = "kuryeye_istek_atildi"
    KURYE_REDDETTI = "kurye_reddetti"
    KURYE_CAGRILDI = "kurye_cagrildi"
    KURYEYE_VERILDI = "kuryeye_verildi"
    YOLDA = "yolda"
    TESLIM_EDILDI = "teslim_edildi"

class OrderItemCreate(BaseModel):
    product_name: str = Field(..., min_length=1, description="Ürün adı")
    price: float = Field(..., gt=0, description="Ürün fiyatı")
    quantity: int = Field(..., gt=0, description="Ürün adedi")

class OrderItemResponse(BaseModel):
    id: UUID
    product_name: str
    price: float
    quantity: int
    total: float

class OrderCreateReq(BaseModel):
    customer: str = Field(..., min_length=1, description="Müşteri adı")
    phone: str = Field(..., min_length=7, description="Telefon numarası")
    address: str = Field(..., min_length=1, description="Gönderici adresi")
    delivery_address: str = Field(..., min_length=1, description="Teslimat adresi")
    pickup_lat: float = Field(..., ge=-90, le=90, description="Alış konumu enlem")
    pickup_lng: float = Field(..., ge=-180, le=180, description="Alış konumu boylam")
    dropoff_lat: float = Field(..., ge=-90, le=90, description="Teslim konumu enlem")
    dropoff_lng: float = Field(..., ge=-180, le=180, description="Teslim konumu boylam")
    type: DeliveryType = Field(..., description="Teslimat tipi")
    amount: float = Field(..., gt=0, description="Toplam tutar")
    carrier_type: str = Field(default="kurye", description="Taşıyıcı tipi")
    vehicle_type: str = Field(default="2_teker_motosiklet", description="Taşıyıcı aracı")
    cargo_type: Optional[str] = Field(None, description="Yük tipi")
    special_requests: Optional[str] = Field(None, description="Özel talepler")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Sipariş ürünleri")

class OrderUpdateReq(BaseModel):
    customer: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = Field(None, min_length=7)
    address: Optional[str] = Field(None, min_length=1)
    delivery_address: Optional[str] = Field(None, min_length=1)
    pickup_lat: Optional[float] = Field(None, ge=-90, le=90)
    pickup_lng: Optional[float] = Field(None, ge=-180, le=180)
    dropoff_lat: Optional[float] = Field(None, ge=-90, le=90)
    dropoff_lng: Optional[float] = Field(None, ge=-180, le=180)
    type: Optional[DeliveryType] = None
    status: Optional[OrderStatus] = None
    amount: Optional[float] = Field(None, gt=0)
    cargo_type: Optional[str] = None
    special_requests: Optional[str] = None
    items: Optional[List[OrderItemCreate]] = None

class OrderResponse(BaseModel):
    id: UUID
    code: str
    customer: str
    phone: str
    address: str
    delivery_address: str
    type: str
    status: str
    amount: float
    carrier_type: str
    vehicle_type: str
    cargo_type: Optional[str]
    special_requests: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

class OrderHistoryItem(BaseModel):
    id: str
    code: str
    customer: str
    phone: str
    address: str
    delivery_address: str
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    type: str
    amount: float
    status: str
    date: str  # ISO format

class OrderListResponse(BaseModel):
    orders: List[OrderHistoryItem]
    total_count: int
    total_amount: float
