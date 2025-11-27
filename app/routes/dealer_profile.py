from fastapi import APIRouter, Depends, Body, HTTPException
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
    "/profile",
    summary="Get Dealer Profile",
    description="Bayi profil bilgilerini getirir. Token'dan bayi ID'si alınır.",
    response_model=Union[DealerProfileResponse, dict]
)
async def get_profile(
    claims: dict = Depends(require_roles(["Dealer", "Admin"]))
):
    """Bayi profil görüntüleme - Token'dan bayi ID'si alınır"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    return await ctrl.get_dealer_profile(UUID(dealer_id))


@router.put(
    "/profile",
    summary="Update Dealer Profile",
    description="Bayi profil bilgilerini günceller. Token'dan bayi ID'si alınır."
)
async def update_profile(
    req: DealerProfileUpdateReq,
    claims: dict = Depends(require_roles(["Dealer", "Admin"]))
):
    """Bayi profil güncelleme - Token'dan bayi ID'si alınır"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    return await ctrl.update_dealer_profile(UUID(dealer_id), req)

