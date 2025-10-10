from fastapi import APIRouter
from ..models.auth_model import RegisterReq, LoginReq
from ..controllers import auth_controller

router = APIRouter()

@router.post("/register")
def register(req: RegisterReq):
    return auth_controller.register(req.first_name,req.last_name, req.email, req.phone, req.password)

@router.post("/login")
def login(req: LoginReq):
    return auth_controller.login(req.email, req.password)

@router.get("/me")
def me(driver=auth_controller.get_current_driver):
    return {"success": True, "message": "Driver info", "data": driver}
