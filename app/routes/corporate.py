from fastapi import APIRouter, Depends, Query, Path, Body
from uuid import UUID
from app.controllers.auth_controller import require_roles
from app.controllers import corporate_user_controller as ctrl
from app.models.corporate_user_model import (
    CorporateUserCreate,
    CorporateUserUpdate
)

router = APIRouter(prefix="/api/admin/corporate", tags=["Corporate Users"])

# CREATE
@router.post(
    "",
    summary="Kurumsal Kullanıcı Oluştur",
    description="Admin tarafından kurumsal kullanıcı (Corporate rolü) oluşturulur",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def create_corporate_user(req: CorporateUserCreate = Body(...)):
    return await ctrl.create_corporate_user(req.model_dump())

# LIST
@router.get(
    "",
    summary="Kurumsal Kullanıcıları Listele",
    description="Tüm kurumsal kullanıcıları listeler",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def list_corporate_users(
    limit: int = Query(50, ge=1, le=200, description="Sayfa başına kayıt sayısı"),
    offset: int = Query(0, ge=0, description="Sayfa offset")
):
    return await ctrl.list_corporate_users(limit, offset)

# GET BY ID
@router.get(
    "/{user_id}",
    summary="Kurumsal Kullanıcı Detayı",
    description="Belirli bir kurumsal kullanıcının detaylarını getirir",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def get_corporate_user(user_id: UUID = Path(..., description="Kullanıcı UUID'si")):
    return await ctrl.get_corporate_user(str(user_id))

# UPDATE (PUT)
@router.put(
    "/{user_id}",
    summary="Kurumsal Kullanıcı Güncelle",
    description="Kurumsal kullanıcı bilgilerini günceller",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def update_corporate_user(
    user_id: UUID = Path(..., description="Kullanıcı UUID'si"),
    req: CorporateUserUpdate = Body(...)
):
    return await ctrl.update_corporate_user(str(user_id), req.model_dump(exclude_none=True))

# DELETE
@router.delete(
    "/{user_id}",
    summary="Kurumsal Kullanıcı Sil",
    description="Kurumsal kullanıcıyı siler (soft delete)",
    dependencies=[Depends(require_roles(["Admin"]))]
)
async def delete_corporate_user(user_id: UUID = Path(..., description="Kullanıcı UUID'si")):
    return await ctrl.delete_corporate_user(str(user_id))

