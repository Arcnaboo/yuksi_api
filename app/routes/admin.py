from fastapi import APIRouter, Query, Depends, HTTPException, Path, Body
from typing import Optional
from uuid import UUID
from app.models.admin_model import AdminRegisterReq
from app.models.corporate_user_model import CommissionRateSet
from app.controllers import admin_controller, admin_user_controller
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/register")
async def admin_register(req: AdminRegisterReq):
    return await admin_controller.register_admin(req.first_name,req.last_name, req.email, req.password)

@router.get(
    "/users/all",
    summary="Tüm Kullanıcıları Getir (Admin)",
    description="Admin tarafından tüm kullanıcı tiplerini (Courier, Restaurant, Admin, Dealer) getirir. Type ve search parametreleri ile filtreleme yapılabilir. SADECE ADMIN ERİŞEBİLİR.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_all_users(
    type: Optional[str] = Query(None, description="Filtreleme: 'courier', 'restaurant', 'admin', 'dealer', 'all' (varsayılan: 'all')"),
    search: Optional[str] = Query(None, description="Arama: Email, name, phone üzerinde arama yapar"),
    limit: int = Query(50, ge=1, le=200, description="Her tip için maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Her tip için offset"),
    claims: dict = Depends(require_roles(["Admin"]))
):
    """
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    """
    # Ekstra güvenlik kontrolü - sadece Admin rolü
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    
    if "Admin" not in roles:
        raise HTTPException(status_code=403, detail="Bu endpoint'e sadece Admin erişebilir")
    
    return await admin_user_controller.get_all_users(
        user_type=type,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get(
    "/users/commission",
    summary="Kullanıcı Komisyon Oranı Getir",
    description="Kullanıcının komisyon oranı getirilir. Token'dan kullanıcı ID'si alınır. Admin herhangi bir kullanıcının komisyon oranını görebilir. Corporate ve Dealer kullanıcıları sadece kendi komisyon oranlarını görebilir. ID'ye göre otomatik olarak Kurumsal kullanıcı veya Bayi tespit edilir.",
    dependencies=[Depends(require_roles(["Admin", "Corporate", "Dealer"]))],
)
async def get_user_commission_rate(
    claims: dict = Depends(require_roles(["Admin", "Corporate", "Dealer"]))
):
    """
    Kullanıcının komisyon oranını getirir.
    Token'dan kullanıcı ID'si alınır.
    ID'ye göre otomatik olarak kurumsal kullanıcı mı bayi mi olduğu tespit edilir.
    Corporate ve Dealer kullanıcıları sadece kendi komisyon oranlarını görebilir.
    """
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token'da kullanıcı ID bulunamadı")
    return await admin_user_controller.get_user_commission_rate(str(user_id), claims)


@router.post(
    "/users/{user_id}/commission",
    summary="Kullanıcı Komisyon Oranı Belirle",
    description="Admin tarafından kullanıcıya komisyon oranı belirlenir. ID'ye göre otomatik olarak Kurumsal kullanıcı veya Bayi tespit edilir. Bu oran, kullanıcının oluşturduğu yüklerde otomatik olarak görünecektir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def set_user_commission_rate(
    user_id: UUID = Path(..., description="Kullanıcı UUID'si (Corporate veya Dealer)"),
    req: CommissionRateSet = Body(...)
):
    """
    Komisyon oranı belirleme endpoint'i (POST).
    ID'ye göre otomatik olarak kurumsal kullanıcı mı bayi mi olduğu tespit edilir.
    İleride başka roller için de genişletilebilir.
    """
    return await admin_user_controller.set_user_commission_rate(
        str(user_id),
        req.commissionRate,
        req.description
    )


@router.put(
    "/users/{user_id}/commission",
    summary="Kullanıcı Komisyon Oranı Güncelle",
    description="Admin tarafından kullanıcının komisyon oranı güncellenir. ID'ye göre otomatik olarak Kurumsal kullanıcı veya Bayi tespit edilir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_user_commission_rate(
    user_id: UUID = Path(..., description="Kullanıcı UUID'si (Corporate veya Dealer)"),
    req: CommissionRateSet = Body(...)
):
    """
    Komisyon oranı güncelleme endpoint'i (PUT).
    ID'ye göre otomatik olarak kurumsal kullanıcı mı bayi mi olduğu tespit edilir.
    İleride başka roller için de genişletilebilir.
    """
    return await admin_user_controller.set_user_commission_rate(
        str(user_id),
        req.commissionRate,
        req.description
    )


@router.get(
    "/users/commissions",
    summary="Tüm Kullanıcıların Komisyon Oranları",
    description="Admin tarafından tüm Corporate ve Dealer kullanıcılarının komisyon oranları listelenir. user_type parametresi ile filtreleme yapılabilir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_all_users_commissions(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Offset değeri"),
    user_type: Optional[str] = Query(None, description="Filtreleme: 'corporate', 'dealer' veya None (hepsi)")
):
    """
    Tüm kullanıcıların komisyon oranlarını getirir.
    Corporate ve Dealer kullanıcılarının komisyon oranları listelenir.
    """
    return await admin_user_controller.get_all_users_commissions(
        limit=limit,
        offset=offset,
        user_type=user_type
    )

@router.get(
    "/all-jobs",
    summary="Tüm İşleri Getir (Admin)",
    description="Admin tarafından tüm işleri getirir. İş durumu ve arama parametreleri ile filtreleme yapılabilir. SADECE ADMIN ERİŞEBİLİR.",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def get_all_jobs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    deliveryType: str | None = Query(None)
):
    """
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    """
    return await admin_controller.get_all_jobs(
        limit=limit,
        offset=offset,
        delivery_type=deliveryType
    )