from app.services import company_package_service as service


async def list_packages():
    rows, err = await service.list_company_packages()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Company packages listed", "data": rows}


async def get_package(package_id: str):
    row, err = await service.get_company_package(package_id)
    if err or not row:
        return {"success": False, "message": err or "Package not found", "data": {}}
    return {"success": True, "message": "Company package fetched", "data": row}


async def create_package(data: dict):
    row, err = await service.create_company_package(
        data["carrier_km"],
        data["requested_km"],
        data["price"]
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Company package created", "data": row}


async def update_package(package_id: str, data: dict):
    ok, err = await service.update_company_package(
        package_id,
        data["carrier_km"],
        data["requested_km"],
        data["price"]
    )
    if err or not ok:
        return {"success": False, "message": err or "Package not found", "data": {}}
    return {"success": True, "message": "Company package updated", "data": {"id": package_id}}


async def delete_package(package_id: str):
    ok, err = await service.delete_company_package(package_id)
    if err or not ok:
        return {"success": False, "message": err or "Package not found", "data": {}}
    return {"success": True, "message": "Company package deleted", "data": {"id": package_id}}
