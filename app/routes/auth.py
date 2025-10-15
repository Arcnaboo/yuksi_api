from fastapi import APIRouter
from pydantic import BaseModel
from ..models.auth_model import RegisterReq, LoginReq, RefreshReq, LogoutReq
from ..controllers import auth_controller

router = APIRouter(prefix="/api/Auth", tags=["Auth"])



@router.post("/register")
def register(req: RegisterReq):
    return auth_controller.register(req.first_name,req.last_name, req.email, req.phone, req.password)

@router.post("/login")
def login(req: LoginReq):
    return auth_controller.login(req.email, req.password)

@router.post("/logout")
def logout(req: LogoutReq):
    return auth_controller.logout(req.refreshToken)

@router.get("/me")
def me(driver=auth_controller.get_current_driver):
    return {"success": True, "message": "Driver info", "data": driver}

@router.post("/refresh")
def refresh(req: RefreshReq):
    return auth_controller.refresh(req.refreshToken)
