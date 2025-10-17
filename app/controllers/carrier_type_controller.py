from app.services import carrier_type_service as service

async def create(data):
    id = await service.create_carrier_type(data)
    return {"success": True, "message": "Carrier type created", "data": {"id": id}}

async def get_all():
    data = await service.list_carrier_types()
    return {"success": True, "message": "Carrier types fetched", "data": data}

async def delete(id):
    await service.delete_carrier_type(id)
    return {"success": True, "message": "Carrier type deleted", "data": {}}

async def update(id, data):
    error = await service.update_carrier_type(id, data)
    if error:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Carrier type updated", "data": {}}
