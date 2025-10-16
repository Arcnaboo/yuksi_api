from fastapi import APIRouter, Depends
from app.models.package_model import PackageCreate, PackageUpdate
from app.controllers import package_controller as controller
from app.controllers import auth_controller

router = APIRouter(prefix="/api/Package", tags=["Package"])

@router.post("/create")
async def create_package(req: PackageCreate, _=Depends(auth_controller.require_roles(["Admin"]))):
    return await controller.create_package(req.carrier, req.days, req.price)

@router.get("/all")
async def get_all_packages(_=Depends(auth_controller.require_roles(["Admin"]))):
    return await controller.get_all_packages()

@router.patch("/update")
async def update_package(req: PackageUpdate, _=Depends(auth_controller.require_roles(["Admin"]))):
    fields = {k: v for k, v in req.dict().items() if v is not None and k != "id"}
    return await controller.update_package(req.id, fields)

@router.delete("/delete/{pkg_id}")
async def delete_package(pkg_id: str, _=Depends(auth_controller.require_roles(["Admin"]))):
    return await controller.delete_package(pkg_id)
