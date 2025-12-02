from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Union
from app.models.user_model import UserRegisterReq, UserLoginReq, UserProfileResponse, UserProfileUpdateReq
from app.controllers import user_controller
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/User", tags=["User"])


@router.post("/register")
async def register(req: UserRegisterReq):
    return await user_controller.register(
        req.email,
        req.password,
        req.phone,
        req.first_name,
        req.last_name
    )


@router.post("/login")
async def login(req: UserLoginReq):
    return await user_controller.login(req.email, req.password)


@router.get(
    "/profile",
    summary="Get User Profile",
    description="Bireysel kullanıcı profil bilgilerini getirir. Token'dan kullanıcı ID'si alınır.",
    response_model=Union[dict, UserProfileResponse]
)
async def get_profile(
    claims: dict = Depends(require_roles(["Default"]))
):
    """Bireysel kullanıcı profil görüntüleme - Token'dan kullanıcı ID'si alınır"""
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Token'da kullanıcı ID bulunamadı")
    return await user_controller.get_user_profile(str(user_id))


@router.put(
    "/profile",
    summary="Update User Profile",
    description="Bireysel kullanıcı profil bilgilerini günceller. Token'dan kullanıcı ID'si alınır."
)
async def update_profile(
    req: UserProfileUpdateReq = Body(...),
    claims: dict = Depends(require_roles(["Default"]))
):
    """Bireysel kullanıcı profil güncelleme - Token'dan kullanıcı ID'si alınır"""
    user_id = claims.get("userId") or claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Token'da kullanıcı ID bulunamadı")
    return await user_controller.update_user_profile(str(user_id), req)

