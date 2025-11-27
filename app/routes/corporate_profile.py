from fastapi import APIRouter, Depends, Path, Body, HTTPException
from uuid import UUID
from typing import Union
from app.controllers.auth_controller import require_roles
from app.controllers import corporate_user_controller as ctrl
from app.models.corporate_user_model import (
    CorporateProfileResponse,
    CorporateProfileUpdateReq
)

router = APIRouter(prefix="/api/corporate", tags=["Corporate Profile"])


@router.get(
    "/{user_id}/profile",
    summary="Get Corporate Profile",
    description="Kurumsal kullanıcı profil bilgilerini getirir.",
    response_model=Union[CorporateProfileResponse, dict]
)
async def get_profile(
    user_id: str,
    claims: dict = Depends(require_roles(["Corporate", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view this corporate profile")
    """Kurumsal kullanıcı profil görüntüleme"""
    return await ctrl.get_corporate_profile(user_id)


@router.put(
    "/{user_id}/profile",
    summary="Update Corporate Profile",
    description="Kurumsal kullanıcı profil bilgilerini günceller."
)
async def update_profile(
    user_id: str,
    req: CorporateProfileUpdateReq,
    claims: dict = Depends(require_roles(["Corporate", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to update this corporate profile")
    """Kurumsal kullanıcı profil güncelleme"""
    return await ctrl.update_corporate_profile(user_id, req)

