from fastapi import APIRouter, Depends, Query, Path, Body
from uuid import UUID
from typing import Optional
from app.controllers import vehicle_product_controller as ctrl
from app.models.vehicle_product_model import (
    VehicleProductCreate,
    VehicleProductUpdate,
    VehicleProductResponse,
    VehicleProductListResponse
)
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/vehicles", tags=["Vehicle Products"])


@router.post(
    "",
    summary="Yeni Araç Ürünü Ekle",
    description="Admin tarafından yeni bir araç ürünü oluşturulur (araç tipi + özellikler + kapasite baremleri)",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=dict
)
async def create_vehicle_product(
    req: VehicleProductCreate = Body(...)
):
    """Yeni araç ürünü oluşturma endpoint'i"""
    return await ctrl.create_vehicle_product(req.model_dump())


@router.get(
    "",
    summary="Araç Ürünleri Listesi",
    description="Tüm araç ürünlerini listeler (filtreleme seçenekleri ile)",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=dict
)
async def list_vehicle_products(
    template: Optional[str] = Query(
        None,
        description="Araç tipi filtresi: motorcycle, minivan, panelvan, kamyonet, kamyon"
    ),
    isActive: Optional[bool] = Query(
        None,
        description="Aktif/pasif filtresi"
    )
):
    """Araç ürünleri listesi endpoint'i"""
    return await ctrl.list_vehicle_products(template, isActive)


@router.get(
    "/{product_id}",
    summary="Araç Ürünü Detayı",
    description="Belirli bir araç ürününün detaylarını getirir (kapasite seçenekleri dahil)",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=dict
)
async def get_vehicle_product(
    product_id: UUID = Path(..., description="Araç ürünü ID'si")
):
    """Araç ürünü detay endpoint'i"""
    return await ctrl.get_vehicle_product(product_id)


@router.patch(
    "/{product_id}",
    summary="Araç Ürününü Güncelle",
    description="Mevcut araç ürününü günceller (kapasite baremleri dahil)",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=dict
)
async def update_vehicle_product(
    product_id: UUID = Path(..., description="Araç ürünü ID'si"),
    req: VehicleProductUpdate = Body(...)
):
    """Araç ürünü güncelleme endpoint'i"""
    return await ctrl.update_vehicle_product(product_id, req.model_dump(exclude_unset=True))


@router.delete(
    "/{product_id}",
    summary="Araç Ürününü Sil",
    description="Araç ürününü siler (aktif yüklerde kullanılıyorsa silinemez)",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=dict
)
async def delete_vehicle_product(
    product_id: UUID = Path(..., description="Araç ürünü ID'si")
):
    """Araç ürünü silme endpoint'i"""
    return await ctrl.delete_vehicle_product(product_id)

