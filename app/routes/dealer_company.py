from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query, Body, HTTPException
from app.controllers import dealer_company_controller as ctrl
from app.models.dealer_company_model import DealerCreateCompanyReq
from app.models.company_model import CompanyUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/dealer/companies", tags=["Dealer Companies"])


# ✅ POST: Bayi için yeni şirket oluştur ve bağla
@router.post(
    "",
    summary="Yeni Şirket Oluştur ve Bağla",
    description="Bayi için yeni şirket oluşturur ve bayisine otomatik olarak bağlar.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def create_and_link_company(
    body: DealerCreateCompanyReq = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayi için yeni şirket oluştur ve bağla endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_create_and_link_company(str(dealer_id), body.model_dump())


# ✅ POST: Mevcut şirketi bayisine bağla (company_id path parametresi ile)
@router.post(
    "/{company_id}",
    summary="Mevcut Şirketi Bağla",
    description="Mevcut bir şirketi ID ile bayisine bağlar. Şirket başka bir bayide ise hata verir.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def link_existing_company(
    company_id: UUID = Path(..., description="Bağlanacak şirketin ID'si"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Mevcut şirketi bayisine bağla endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_link_existing_company(str(dealer_id), str(company_id))


# ✅ GET: Bayinin şirketlerini listele
@router.get(
    "",
    summary="Bayinin Şirketlerini Listele",
    description="Bayinin bağlı olduğu tüm şirketleri listeler.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_companies(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin şirketlerini listele endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_companies(str(dealer_id), limit, offset)


# ✅ GET: Bayinin belirli bir şirketinin detayını getir
@router.get(
    "/{company_id}",
    summary="Şirket Detayı",
    description="Bayinin belirli bir şirketinin detaylı bilgilerini getirir.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_company_detail(
    company_id: UUID = Path(..., description="Şirket ID'si"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin belirli bir şirketinin detayını getir endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_company_detail(str(dealer_id), str(company_id))


# ✅ PUT: Bayinin belirli bir şirketini güncelle
@router.put(
    "/{company_id}",
    summary="Şirket Güncelle",
    description="Bayinin kendisine bağlı bir şirketin bilgilerini günceller. Tüm alanlar opsiyoneldir, sadece gönderilen alanlar güncellenir.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def update_company(
    company_id: UUID = Path(..., description="Şirket ID'si"),
    body: CompanyUpdate = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin belirli bir şirketini güncelle endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    # None olmayan alanları filtrele
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Güncellenecek alan bulunamadı")
    
    return await ctrl.dealer_update_company(str(dealer_id), str(company_id), update_data)

