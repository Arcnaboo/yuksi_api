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


@router.post(
    "/users/{user_id}/commission",
    summary="Kullanıcı Komisyon Oranı Belirle (Genel)",
    description="Admin tarafından kullanıcıya komisyon oranı belirlenir. ID'ye göre otomatik olarak tüm kullanıcı tabloları kontrol edilir ve kullanıcı tipi tespit edilir. Sadece Corporate ve Dealer kullanıcıları için komisyon oranı belirlenebilir. Bu oran, kullanıcının oluşturduğu yüklerde otomatik olarak görünecektir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def set_user_commission_rate(
    user_id: UUID = Path(..., description="Kullanıcı UUID'si (Tüm kullanıcı tipleri kontrol edilir)"),
    req: CommissionRateSet = Body(...)
):
    """
    Genel komisyon oranı belirleme endpoint'i.
    ID'ye göre otomatik olarak tüm kullanıcı tabloları kontrol edilir:
    - corporate_users
    - dealers
    - restaurants
    - drivers
    - system_admins
    - users
    
    Sadece Corporate ve Dealer kullanıcıları için komisyon oranı belirlenebilir.
    İleride başka roller için de genişletilebilir.
    """
    return await admin_user_controller.set_user_commission_rate(
        str(user_id),
        req.commissionRate,
        req.description
    )
