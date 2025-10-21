from typing import Any, Union
from fastapi import APIRouter
from ..models.cargotype_model import CargoTypeReq, CargoTypeRes, CargoTypeListRes
from ..controllers import cargotype_controller

router = APIRouter(prefix="/api/CargoType", tags=["CargoTypes"])

@router.get("",
            response_model= Union[CargoTypeListRes, Any])
async def get_all_cargotypes():
    return await cargotype_controller.get_all_cargotypes()

@router.post("",
             response_model= Union[CargoTypeRes, Any])
async def add_cargotype(req: CargoTypeReq):
    return await cargotype_controller.add_cargotype(req.name, req.price, req.description)

@router.get("/{cargotype_id}",
             response_model= Union[CargoTypeRes, Any])
async def get_cargotype(cargotype_id: int):
    return await cargotype_controller.get_cargotype(cargotype_id)

@router.put("/{cargotype_id}",
             response_model= Union[CargoTypeRes, Any])
async def update_cargotype(cargotype_id: int, req: CargoTypeReq):
    return await cargotype_controller.update_cargotype(cargotype_id, req.name, req.price, req.description)

@router.delete("/{cargotype_id}")
async def delete_cargotype(cargotype_id: int):
    return await cargotype_controller.delete_cargotype(cargotype_id)
