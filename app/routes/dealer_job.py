from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from typing import Any
from app.controllers import dealer_job_controller as ctrl
from app.models.admin_job_model import AdminJobCreate, AdminJobUpdateReq
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/dealer/jobs", tags=["Dealer Jobs"])

# === CREATE ===
@router.post(
    "",
    summary="Yeni Yük Oluştur (Bayi)",
    description="Bayi tarafından manuel olarak yeni bir yük kaydı oluşturulur.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def create_dealer_job(
    req: AdminJobCreate = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """
    Bayi tarafından manuel yük oluşturma endpoint'i.
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]`
    """
    # Token'dan dealer_id al
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_create_job(req.model_dump(), str(dealer_id))

# === GET ===
@router.get(
    "",
    summary="Yük Listesi (Bayi)",
    description="Bayi tarafından oluşturulan tüm yükleri listeler (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_dealer_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    # Token'dan dealer_id al
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_jobs(str(dealer_id), limit, offset, deliveryType)

# === UPDATE ===
@router.put(
    "/{job_id}",
    summary="Yük Güncelle (Bayi)",
    description="Bayi tarafından bir yük kaydı güncellenir (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def update_dealer_job(
    job_id: str = Path(..., description="Yük ID"),
    req: AdminJobUpdateReq = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    # Token'dan dealer_id al
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_update_job(job_id, str(dealer_id), req.model_dump(exclude_none=True))


# === DELETE ===
@router.delete(
    "/{job_id}",
    summary="Yük Sil (Bayi)",
    description="Bayi tarafından bir yük kaydı silinir (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def delete_dealer_job(
    job_id: str = Path(..., description="Yük ID"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    # Token'dan dealer_id al
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_delete_job(job_id, str(dealer_id))

