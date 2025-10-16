from ..services import package_service as svc

async def create_package(carrier: str, days: int, price: float):
    result, err = await svc.create_package(carrier, days, price)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Package created", "data": result}

async def get_all_packages():
    result, err = await svc.get_all_packages()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Packages retrieved", "data": result}

async def update_package(pkg_id: str, fields: dict):
    err = await svc.update_package(pkg_id, fields)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Package updated", "data": {}}

async def delete_package(pkg_id: str):
    err = await svc.delete_package(pkg_id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Package deleted", "data": {}}
