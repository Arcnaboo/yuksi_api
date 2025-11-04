from app.services import extra_service_service as svc


async def list_services():
    rows, err = await svc.list_services()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Services fetched", "data": rows}


async def get_service(id: str):
    row, err = await svc.get_service(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Service fetched", "data": row}


async def create_service(data: dict):
    row, err = await svc.create_service(     
        data.get("carrier_type"),
        data.get("service_name"),
        data.get("price")
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Service created", "data": row}


async def update_service(id: str, data: dict):
    ok, err = await svc.update_service(
        id,
        data.get("carrier_type"),
        data.get("service_name"),
        data.get("price")
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Service updated", "data": {"id": id}}


async def delete_service(id: str):
    ok, err = await svc.delete_service(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Service deleted", "data": {"id": id}}
