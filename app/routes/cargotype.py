from fastapi import APIRouter
from ..models.cargotype_model import CargoTypeReq
from ..controllers import cargotype_controller

router = APIRouter(prefix="/api/CargoTypes")

@router.get("")
async def get_all_cargotypes():
    return await cargotype_controller.get_all_cargotypes()

@router.post("")
async def add_cargotype(req: CargoTypeReq):
    return await cargotype_controller.add_cargotype(req.name, req.price, req.description)

@router.put("/{cargotype_id}")
async def update_cargotype(cargotype_id: int, req: CargoTypeReq):
    return await cargotype_controller.update_cargotype(cargotype_id, req.name, req.price, req.description)

@router.get("/{cargotype_id}")
async def get_cargotype(cargotype_id: int):
    return await cargotype_controller.get_cargotype(cargotype_id)

@router.delete("/{cargotype_id}")
async def delete_cargotype(cargotype_id: int):
    return await cargotype_controller.delete_cargotype(cargotype_id)
