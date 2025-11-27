from fastapi import APIRouter, Depends, Path, Body, HTTPException
from uuid import UUID
from typing import Union
from app.controllers.auth_controller import require_roles
from app.controllers import dealer_controller as ctrl
from app.models.dealer_model import (
    DealerProfileResponse,
    DealerProfileUpdateReq
)

router = APIRouter(prefix="/api/dealer", tags=["Dealer Profile"])


@router.get(
    "/{dealer_id}/profile",
    summary="Get Dealer Profile",
    description="Bayi profil bilgilerini getirir.",
    response_model=Union[DealerProfileResponse, dict]
)
async def get_profile(
    dealer_id: str,
    claims: dict = Depends(require_roles(["Dealer", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != dealer_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view this dealer profile")
    """Bayi profil görüntüleme"""
    return await ctrl.get_dealer_profile(UUID(dealer_id))


@router.put(
    "/{dealer_id}/profile",
    summary="Update Dealer Profile",
    description="Bayi profil bilgilerini günceller."
)
async def update_profile(
    dealer_id: str,
    req: DealerProfileUpdateReq,
    claims: dict = Depends(require_roles(["Dealer", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != dealer_id:
            raise HTTPException(status_code=403, detail="Unauthorized to update this dealer profile")
    """Bayi profil güncelleme"""
    return await ctrl.update_dealer_profile(UUID(dealer_id), req)

