from app.services import company_package_service as service

# ✅ List
async def list_packages():
    rows, err = await service.list_company_packages()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Packages fetched", "data": rows}


# ✅ Get by ID
async def get_package(id: str):
    row, err = await service.get_company_package(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Package fetched", "data": row}


# ✅ Create
async def create_package(data: dict):
    row, err = await service.create_company_package(
        data["carrier_km"],
        data["requested_km"],
        data["price"]
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Package created", "data": row}


# ✅ Update
async def update_package(id: str, data: dict):
    ok, err = await service.update_company_package(
        id,
        data.get("requested_km"),
        data.get("price")
    )
    if err:
        return {"success": False, "message": err, "data": {}}

    return {"success": True, "message": "Package updated", "data": {"id": id}}


# ✅ Delete
async def delete_package(id: str):
    ok, err = await service.delete_company_package(id)
    if err:
        return {"success": False, "message": err, "data": {}}

    return {"success": True, "message": "Package deleted", "data": {"id": id}}
