from fastapi import APIRouter, Query, Depends, Path, Body, HTTPException
from typing import Optional
from uuid import UUID
from app.models.support_model import SupportUserCreate, SupportUserUpdate
from app.controllers import support_user_controller, support_permission_controller
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/support", tags=["Support"])

@router.post(
    "",
    summary="Çağrı Merkezi Üyesi Oluştur (Admin)",
    description="Admin tarafından çağrı merkezi için yeni bir üye oluşturulur. Bu üye daha sonra login yapabilir ve 'Support' rolü ile sisteme erişebilir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def create_support_user(
    req: SupportUserCreate = Body(...),
    claims: dict = Depends(require_roles(["Admin"]))
):
    """
    Çağrı merkezi üyesi oluşturma endpoint'i.
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    
    **Oluşturulan üye:**
    - Email ve şifre ile login yapabilir
    - Rolü: "Support" olacak
    - Sadece çağrı merkezi yetkileri olacak
    """
    return await support_user_controller.create_support_user(
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        password=req.password,
        phone=req.phone,
        access=req.access
    )

@router.get(
    "",
    summary="Tüm Çağrı Merkezi Üyelerini Getir (Admin)",
    description="Admin tarafından tüm çağrı merkezi üyelerini listeler.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def get_all_support_users(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    claims: dict = Depends(require_roles(["Admin"]))
):
    """
    Tüm çağrı merkezi üyelerini getirir.
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    """
    return await support_permission_controller.get_all_support_permissions(
        limit=limit,
        offset=offset
    )

@router.get(
    "/me",
    summary="Support Üyesi Getir",
    description="Token'dan kullanıcı ID'si alınarak support kullanıcısının bilgilerini getirir.",
    dependencies=[Depends(require_roles(["Admin", "Support"]))],
)
async def get_support_user(
    claims: dict = Depends(require_roles(["Admin", "Support"]))
):
    """
    Support kullanıcısının bilgilerini getirir.
    Token'dan kullanıcı ID'si otomatik olarak alınır.
    Admin veya Support rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    """
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Token'da kullanıcı ID bulunamadı")
    return await support_permission_controller.get_support_permissions(str(user_id))

@router.put(
    "/{user_id}",
    summary="Support Üyesi Güncelle (Admin)",
    description="Admin tarafından support kullanıcısının bilgileri güncellenir. Tüm alanlar opsiyoneldir, sadece gönderilen alanlar güncellenir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def update_support_user(
    user_id: UUID = Path(..., description="Support kullanıcı ID'si"),
    req: SupportUserUpdate = Body(...),
    claims: dict = Depends(require_roles(["Admin"]))
):
    """
    Support kullanıcısının bilgilerini günceller.
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    
    **Güncellenebilir Alanlar:**
    - first_name: Ad
    - last_name: Soyad
    - email: E-posta adresi (unique kontrolü yapılır)
    - phone: Telefon numarası
    - is_active: Aktif durumu
    - access: Erişim modülleri (1-7 arası)
    
    **Not:** Tüm alanlar opsiyoneldir. Sadece gönderilen alanlar güncellenir.
    """
    return await support_user_controller.update_support_user(
        support_user_id=str(user_id),
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        phone=req.phone,
        is_active=req.is_active,
        access=req.access
    )

@router.delete(
    "/{user_id}",
    summary="Support Üyesi Sil (Admin)",
    description="Admin tarafından support kullanıcısı silinir.",
    dependencies=[Depends(require_roles(["Admin"]))],
)
async def delete_support_user(
    user_id: UUID = Path(..., description="Support kullanıcı ID'si"),
    claims: dict = Depends(require_roles(["Admin"]))
):
    """
    Support kullanıcısını siler.
    Sadece Admin rolüne sahip kullanıcılar bu endpoint'e erişebilir.
    """
    return await support_user_controller.delete_support_user(str(user_id))

