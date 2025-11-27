from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Union
from app.controllers.auth_controller import require_roles
from app.controllers import corporate_user_controller as ctrl
from app.models.corporate_user_model import (
    CorporateProfileResponse,
    CorporateProfileUpdateReq
)

router = APIRouter(prefix="/api/corporate", tags=["Corporate Profile"])


@router.get(
    "/profile",
    summary="Get Corporate Profile",
    description="Kurumsal kullanıcı profil bilgilerini getirir. Token'dan kullanıcı ID'si alınır.",
    response_model=Union[CorporateProfileResponse, dict]
)
async def get_profile(
    claims: dict = Depends(require_roles(["Corporate", "Admin"]))
):
    """Kurumsal kullanıcı profil görüntüleme - Token'dan kullanıcı ID'si alınır"""
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Token'da kullanıcı ID bulunamadı")
    return await ctrl.get_corporate_profile(str(user_id))


@router.put(
    "/profile",
    summary="Update Corporate Profile",
    description="Kurumsal kullanıcı profil bilgilerini günceller. Token'dan kullanıcı ID'si alınır."
)
async def update_profile(
    req: CorporateProfileUpdateReq,
    claims: dict = Depends(require_roles(["Corporate", "Admin"]))
):
    """Kurumsal kullanıcı profil güncelleme - Token'dan kullanıcı ID'si alınır"""
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Token'da kullanıcı ID bulunamadı")
    return await ctrl.update_corporate_profile(str(user_id), req)

