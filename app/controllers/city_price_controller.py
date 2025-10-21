from app.services import city_price_service as service

async def list_prices():
    rows, err = await service.list_city_prices()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "City prices listed", "data": rows}


async def get_price(id: int):
    row, err = await service.get_city_price(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price fetched", "data": row}


async def create_price(data: dict):
    row, err = await service.create_city_price(
        data["route_name"], data["country_id"], data["state_id"], data["city_id"],
        data["courier_price"], data["minivan_price"], data["panelvan_price"],
        data["kamyonet_price"], data["kamyon_price"]
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price created", "data": row}


async def update_price(id: int, data: dict):
    ok, err = await service.update_city_price(
        id, data["route_name"], data["country_id"], data["state_id"], data["city_id"],
        data["courier_price"], data["minivan_price"], data["panelvan_price"],
        data["kamyonet_price"], data["kamyon_price"]
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price updated", "data": {}}

async def delete_price(id: int):
    ok, err = await service.delete_city_price(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price deleted", "data": {"id": id}}    