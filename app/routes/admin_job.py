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
    req: AdminJobCreate = Body(
        ...,
        example={
            "deliveryType": "immediate",
            "carrierType": "courier",
            "vehicleType": "motorcycle",
            "pickupAddress": "Bursa OSB, Nilüfer",
            "pickupCoordinates": [40.192, 29.067],
            "dropoffAddress": "Gözede, 16450 Kestel/Bursa",
            "dropoffCoordinates": [40.198, 29.071],
            "specialNotes": "Paketin sıcak gitmesi gerekiyor.",
            "campaignCode": "YUKSI2025",
            "extraServices": [
                {"serviceId": 1, "name": "Durak Ekleme", "price": 100}
            ],
            "extraServicesTotal": 100,
            "totalPrice": 580,
            "paymentMethod": "cash",
            "imageFileIds": [
                "9fa1e430-9b2e-4a57-b321-9c0b7264b213",
                "acff2e7f-df31-44ce-a8c5-7e31b9810a72"
            ]
        },
    ),
):
    """
    Admin tarafından manuel yük oluşturma endpoint'i.
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]`
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
