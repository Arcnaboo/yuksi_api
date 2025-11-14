from fastapi import APIRouter
from app.models.user_model import UserRegisterReq, UserLoginReq
from app.controllers import user_controller

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

