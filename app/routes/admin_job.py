from fastapi import APIRouter, Query, Path, Body, Depends
from typing import Any
from app.controllers import admin_job_controller as ctrl
from app.models.admin_job_model import AdminJobUpdateReq,AdminJobCreate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/jobs", tags=["Admin Jobs"])

# === CREATE ===
@router.post(
    "",
    summary="Yeni Yük Oluştur (Admin)",
    description="Admin tarafından manuel olarak yeni bir yük kaydı oluşturulur.",
    dependencies=[Depends(require_roles(["Admin", "Restaurant"]))],
)
async def create_admin_job(
    req: AdminJobCreate = Body(...),
):
    """
    Admin tarafından manuel yük oluşturma endpoint'i.
    
    **Araç Seçimi (3 Yöntem):**
    1. **vehicleProductId** (Önerilen): Direkt araç ürün ID'si kullanın
    2. **vehicleTemplate + vehicleFeatures + capacityOptionId**: Araç tipi, özellikler ve kapasite seçimi
    3. **vehicleType** (Eski sistem): String olarak araç tipi (backward compatibility)
    
    **Notlar:**
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]` formatında
    - `totalPrice` opsiyonel: Gönderilmezse backend otomatik hesaplar
    - Araç ürünlerini görmek için: `GET /api/admin/vehicles`
    """
    return await ctrl.admin_create_job(req.model_dump())

# === GET ===
@router.get(
    "",
    summary="Yük Listesi (Admin)",
    description="Admin tarafından oluşturulan tüm yükleri listeler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_admin_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None)
):
    return await ctrl.admin_get_jobs(limit, offset, deliveryType)

# === GET RESTAURANT JOBS ===
@router.get(
    "/restaurants",
    summary="Tüm Restaurant Yükleri (Admin)",
    description="Admin tarafından tüm restaurantların oluşturduğu yükleri listeler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_restaurant_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None),
    restaurantId: str | None = Query(None, description="Restaurant ID ile filtreleme (opsiyonel)")
):
    return await ctrl.admin_get_restaurant_jobs(limit, offset, deliveryType, restaurantId)


# === UPDATE ===
@router.put(
    "/{job_id}",
    summary="Yük Güncelle (Admin)",
    description="Admin tarafından bir yük kaydı güncellenir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_admin_job(
    job_id: str = Path(..., description="Yük ID"),
    req: AdminJobUpdateReq = Body(...)
):
    return await ctrl.admin_update_job(job_id, req.model_dump(exclude_none=True))


# === DELETE ===
@router.delete(
    "/{job_id}",
    summary="Yük Sil (Admin)",
    description="Admin tarafından bir yük kaydı silinir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_admin_job(
    job_id: str = Path(..., description="Yük ID")
):
    return await ctrl.admin_delete_job(job_id)
