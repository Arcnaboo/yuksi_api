from fastapi import APIRouter, Query, Path, Body, Depends, UploadFile, File
from typing import Any
from app.controllers import user_job_controller as ctrl
from app.models.user_job_model import UserJobUpdateReq, UserJobCreate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/User/jobs", tags=["User Jobs"])

# === CREATE ===
@router.post(
    "",
    summary="Yeni Yük Oluştur (Bireysel Kullanıcı)",
    description="Bireysel kullanıcı tarafından yeni bir yük kaydı oluşturulur.",
)
async def create_user_job(
    req: UserJobCreate = Body(...),
    claims: dict = Depends(require_roles(["Default"]))
):
    """
    Bireysel kullanıcı tarafından yük oluşturma endpoint'i.
    
    **Araç Seçimi (3 Yöntem):**
    1. **vehicleProductId** (Önerilen): Direkt araç ürün ID'si kullanın
    2. **vehicleTemplate + vehicleFeatures + capacityOptionId**: Araç tipi, özellikler ve kapasite seçimi
    3. **vehicleType** (Eski sistem): String olarak araç tipi (backward compatibility)
    
    **Notlar:**
    - Dosyalar `/api/file/upload` endpoint'inden alınıp `imageFileIds` alanına gönderilmelidir.
    - `deliveryType`: `immediate` veya `scheduled`
    - `pickupCoordinates` ve `dropoffCoordinates`: `[lat, long]` formatında
    - `totalPrice` opsiyonel: Gönderilmezse backend otomatik hesaplar
    - Araç ürünlerini görmek için: `GET /api/admin/vehicles` (Admin yetkisi gerekir)
    """
    user_id = claims.get("userId") or claims.get("sub")
    return await ctrl.user_create_job(req.model_dump(), str(user_id))

# === GET (liste) ===
@router.get(
    "",
    summary="Yük Listesi (Bireysel Kullanıcı)",
    description="Bireysel kullanıcının oluşturduğu tüm yükleri listeler.",
)
async def get_user_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None),
    claims: dict = Depends(require_roles(["Default"]))
):
    user_id = claims.get("userId") or claims.get("sub")
    return await ctrl.user_get_jobs(str(user_id), limit, offset, deliveryType)

# === CARGO SCAN (Yük Tarat - Araç Tipi Öner) ===
@router.post(
    "/cargo-scan",
    summary="Yük Tarat - Araç Tipi Öner (Bireysel Kullanıcı)",
    description="Yük fotoğrafını analiz eder ve uygun araç tipini önerir. Fotoğraf sisteme kaydedilmez, sadece analiz için kullanılır.",
)
async def cargo_scan(
    file: UploadFile = File(..., description="Yük fotoğrafı"),
    claims: dict = Depends(require_roles(["Default"]))
):
    """
    Yük fotoğrafını AI ile analiz eder ve uygun araç tipini önerir.
    
    **Kullanım:**
    1. Kullanıcı fotoğraf yükler
    2. AI analiz eder ve araç tipi önerir (örnek: "panelvan")
    3. Frontend job formunda `vehicleTemplate` alanını otomatik doldurur
    4. Kullanıcı isterse değiştirebilir
    
    **Response:**
    - `vehicleTemplate`: Önerilen araç tipi (motorcycle, minivan, panelvan, kamyonet, kamyon)
    - `confidence`: Güven seviyesi (0-100)
    - `reason`: Öneri nedeni
    """
    return await ctrl.user_cargo_scan(file)

# === GET (tek kayıt) ===
@router.get(
    "/{job_id}",
    summary="Yük Detayı (Bireysel Kullanıcı)",
    description="Bireysel kullanıcının belirli bir yükünün detaylarını getirir.",
)
async def get_user_job(
    job_id: str = Path(..., description="Yük ID"),
    claims: dict = Depends(require_roles(["Default"]))
):
    user_id = claims.get("userId") or claims.get("sub")
    return await ctrl.user_get_job(job_id, str(user_id))

# === UPDATE ===
@router.put(
    "/{job_id}",
    summary="Yük Güncelle (Bireysel Kullanıcı)",
    description="Bireysel kullanıcı tarafından bir yük kaydı güncellenir.",
)
async def update_user_job(
    job_id: str = Path(..., description="Yük ID"),
    req: UserJobUpdateReq = Body(...),
    claims: dict = Depends(require_roles(["Default"]))
):
    user_id = claims.get("userId") or claims.get("sub")
    return await ctrl.user_update_job(job_id, str(user_id), req.model_dump(exclude_none=True))

# === DELETE ===
@router.delete(
    "/{job_id}",
    summary="Yük Sil (Bireysel Kullanıcı)",
    description="Bireysel kullanıcı tarafından bir yük kaydı silinir.",
)
async def delete_user_job(
    job_id: str = Path(..., description="Yük ID"),
    claims: dict = Depends(require_roles(["Default"]))
):
    user_id = claims.get("userId") or claims.get("sub")
    return await ctrl.user_delete_job(job_id, str(user_id))

