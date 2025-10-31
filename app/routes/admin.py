from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from app.models.admin_model import AdminRegisterReq
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
