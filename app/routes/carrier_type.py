from fastapi import APIRouter, Depends
from app.controllers import carrier_type_controller as ctrl
from app.models.carrier_type_model import CarrierTypeCreate
from app.controllers.auth_controller import require_roles
from app.models.carrier_type_model import CarrierTypeUpdate

router = APIRouter(prefix="/api/CarrierType", tags=["CarrierType"])

@router.post("/create", dependencies=[Depends(require_roles(["Admin"]))])
async def create_carrier(data: CarrierTypeCreate):
    return await ctrl.create(data)

@router.get("/list", dependencies=[Depends(require_roles(["Admin"]))])
async def list_carriers():
    return await ctrl.get_all()

@router.delete("/delete/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_carrier(id: str):
    return await ctrl.delete(id)



@router.patch("/update/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_carrier(id: str, data: CarrierTypeUpdate):
    return await ctrl.update(id, data)
