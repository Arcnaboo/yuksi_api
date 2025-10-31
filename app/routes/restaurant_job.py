from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from typing import Any
from app.controllers import restaurant_job_controller as ctrl
from app.models.admin_job_model import AdminJobCreate, AdminJobUpdateReq
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/Restaurant", tags=["Restaurant Jobs"])

# === CREATE ===
@router.post(
    "/jobs",
    summary="Yeni Yük Oluştur (Restaurant)",
    description="Restaurant tarafından manuel olarak yeni bir yük kaydı oluşturulur.",
)
async def create_restaurant_job(
    req: AdminJobCreate = Body(...),
    claims: dict = Depends(require_roles(["Restaurant"]))
):
    """
    Restaurant tarafından manuel yük oluşturma endpoint'i.
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]`
    """
    restaurant_id = claims.get("userId")
    if not restaurant_id:
        raise HTTPException(status_code=403, detail="Restaurant ID not found in token")
    
    return await ctrl.restaurant_create_job(req.model_dump(), restaurant_id)

# === GET ===
@router.get(
    "/jobs",
    summary="Yük Listesi (Restaurant)",
    description="Restaurant tarafından oluşturulan tüm yükleri listeler.",
)
async def get_restaurant_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None),
    claims: dict = Depends(require_roles(["Restaurant"]))
):
    # Restaurant sadece kendi kayıtlarını görecek
    restaurant_id = claims.get("userId")
    if not restaurant_id:
        raise HTTPException(status_code=403, detail="Restaurant ID not found in token")
    
    return await ctrl.restaurant_get_jobs(limit, offset, deliveryType, restaurant_id)


# === UPDATE ===
@router.put(
    "/jobs/{job_id}",
    summary="Yük Güncelle (Restaurant)",
    description="Restaurant tarafından bir yük kaydı güncellenir.",
)
async def update_restaurant_job(
    job_id: str = Path(..., description="Yük ID"),
    req: AdminJobUpdateReq = Body(...),
    claims: dict = Depends(require_roles(["Restaurant"]))
):
    restaurant_id = claims.get("userId")
    if not restaurant_id:
        raise HTTPException(status_code=403, detail="Restaurant ID not found in token")
    
    return await ctrl.restaurant_update_job(job_id, req.model_dump(exclude_none=True), restaurant_id)


# === DELETE ===
@router.delete(
    "/jobs/{job_id}",
    summary="Yük Sil (Restaurant)",
    description="Restaurant tarafından bir yük kaydı silinir.",
)
async def delete_restaurant_job(
    job_id: str = Path(..., description="Yük ID"),
    claims: dict = Depends(require_roles(["Restaurant"]))
):
    restaurant_id = claims.get("userId")
    if not restaurant_id:
        raise HTTPException(status_code=403, detail="Restaurant ID not found in token")
    
    return await ctrl.restaurant_delete_job(job_id, restaurant_id)

