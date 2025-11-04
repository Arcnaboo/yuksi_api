from fastapi import APIRouter, Depends
from app.controllers.extra_service_controller import *
from app.models.extra_service_model import ExtraServiceCreate, ExtraServiceUpdate
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/company-extra-services", tags=["Extra Services"])

@router.get("", dependencies=[Depends(require_roles(["Admin", "Dealer","Restaurant"]))])
async def list_route():
    return await list_services()

@router.post("", dependencies=[Depends(require_roles(["Admin", "Dealer"]))])
async def create_route(body: ExtraServiceCreate):
    return await create_service(body.model_dump())

@router.get("/{service_id}", dependencies=[Depends(require_roles(["Admin", "Dealer","Restaurant"]))])
async def get_route(service_id: str):
    return await get_service(service_id)

@router.put("/{service_id}", dependencies=[Depends(require_roles(["Admin", "Dealer"]))])
async def update_route(service_id: str, body: ExtraServiceUpdate):
    return await update_service(service_id, body.model_dump(exclude_unset=True))

@router.delete("/{service_id}", dependencies=[Depends(require_roles(["Admin", "Dealer"]))])
async def delete_route(service_id: str):
    return await delete_service(service_id)
