from ..services import cargotype_service as svc

async def add_cargotype(name: str, price: float, description: str = None):
    result, err = await svc.add_cargotype(name, price, description)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Cargo type added", "data": result }

async def update_cargotype(cargotype_id: int, name: str, price: float, description: str = None):
    result, err = await svc.update_cargotype(cargotype_id, name, price, description)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Cargo type updated", "data": result }

async def get_all_cargotypes():
    result, err = await svc.get_all_cargotypes()
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Cargo types retrieved", "data": result }

async def get_cargotype(cargotype_id: int):
    result, err = await svc.get_cargotype(cargotype_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Cargo type retrieved", "data": result }

async def delete_cargotype(cargotype_id: int):
    result, err = await svc.delete_cargotype(cargotype_id)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Cargo type deleted", "data": result }