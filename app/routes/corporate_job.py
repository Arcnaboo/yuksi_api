from fastapi import APIRouter, Query, Path, Body, Depends, HTTPException
from typing import Any
from app.controllers import corporate_job_controller as ctrl
from app.models.admin_job_model import AdminJobCreate, AdminJobUpdateReq
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/corporate/jobs", tags=["Corporate Jobs"])

# === CREATE ===
@router.post(
    "",
    summary="Yeni Yük Oluştur (Kurumsal)",
    description="Kurumsal kullanıcı tarafından manuel olarak yeni bir yük kaydı oluşturulur.",
    dependencies=[Depends(require_roles(["Corporate"]))],
)
async def create_corporate_job(
    req: AdminJobCreate = Body(...),
    claims: dict = Depends(require_roles(["Corporate"]))
):
    """
    Kurumsal kullanıcı tarafından manuel yük oluşturma endpoint'i.
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]`
    """
    # Token'dan corporate_id al
    corporate_id = claims.get("userId") or claims.get("sub")
    if not corporate_id:
        raise HTTPException(status_code=403, detail="Token'da kurumsal kullanıcı ID bulunamadı")
    
    return await ctrl.corporate_create_job(req.model_dump(), str(corporate_id))

# === GET ===
@router.get(
    "",
    summary="Yük Listesi (Kurumsal)",
    description="Kurumsal kullanıcı tarafından oluşturulan tüm yükleri listeler (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Corporate"]))],
)
async def get_corporate_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None),
    claims: dict = Depends(require_roles(["Corporate"]))
):
    # Token'dan corporate_id al
    corporate_id = claims.get("userId") or claims.get("sub")
    if not corporate_id:
        raise HTTPException(status_code=403, detail="Token'da kurumsal kullanıcı ID bulunamadı")
    
    return await ctrl.corporate_get_jobs(str(corporate_id), limit, offset, deliveryType)

# === UPDATE ===
@router.put(
    "/{job_id}",
    summary="Yük Güncelle (Kurumsal)",
    description="Kurumsal kullanıcı tarafından bir yük kaydı güncellenir (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Corporate"]))],
)
async def update_corporate_job(
    job_id: str = Path(..., description="Yük ID"),
    req: AdminJobUpdateReq = Body(...),
    claims: dict = Depends(require_roles(["Corporate"]))
):
    # Token'dan corporate_id al
    corporate_id = claims.get("userId") or claims.get("sub")
    if not corporate_id:
        raise HTTPException(status_code=403, detail="Token'da kurumsal kullanıcı ID bulunamadı")
    
    return await ctrl.corporate_update_job(job_id, str(corporate_id), req.model_dump(exclude_none=True))


# === DELETE ===
@router.delete(
    "/{job_id}",
    summary="Yük Sil (Kurumsal)",
    description="Kurumsal kullanıcı tarafından bir yük kaydı silinir (sadece kendi yükleri).",
    dependencies=[Depends(require_roles(["Corporate"]))],
)
async def delete_corporate_job(
    job_id: str = Path(..., description="Yük ID"),
    claims: dict = Depends(require_roles(["Corporate"]))
):
    # Token'dan corporate_id al
    corporate_id = claims.get("userId") or claims.get("sub")
    if not corporate_id:
        raise HTTPException(status_code=403, detail="Token'da kurumsal kullanıcı ID bulunamadı")
    
    return await ctrl.corporate_delete_job(job_id, str(corporate_id))

