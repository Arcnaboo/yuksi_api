from app.services import city_price_service as service

async def create_city_price(data):
    new_id, err = await service.create_city_price(data)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price created", "data": {"id": new_id}}

async def list_city_prices():
    data, err = await service.list_city_prices()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "City prices fetched", "data": data}

async def update_city_price(id: int, data):
    err = await service.update_city_price(id, data)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price updated", "data": {}}

async def delete_city_price(id: int):
    err = await service.delete_city_price(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price deleted", "data": {}}
