from fastapi import APIRouter
from app.models.admin_model import AdminRegisterReq
from app.controllers import admin_controller

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/register")
async def admin_register(req: AdminRegisterReq):
    return await admin_controller.register_admin(req.first_name,req.last_name, req.email, req.password)
