from app.services import city_price_service as svc

async def list_prices():
    rows, err = await svc.list_city_prices()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "City prices fetched", "data": rows}


async def get_price(id: str):
    row, err = await svc.get_city_price(id)
    if err or not row:
        return {"success": False, "message": err or "Record not found", "data": {}}
    return {"success": True, "message": "City price fetched", "data": row}


async def create_price(data: dict):
    row, err = await svc.create_city_price(
        data.get("route_name"),
        data.get("country_id"),
        data.get("state_id"),
        data.get("city_id"),
        data.get("courier_price"),
        data.get("minivan_price"),
        data.get("panelvan_price"),
        data.get("kamyonet_price"),
        data.get("kamyon_price"),
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "City price created", "data": row}


async def update_price(id: str, data: dict):
    ok, err = await svc.update_city_price(
        id,
        data.get("route_name"),
        data.get("country_id"),
        data.get("state_id"),
        data.get("city_id"),
        data.get("courier_price"),
        data.get("minivan_price"),
        data.get("panelvan_price"),
        data.get("kamyonet_price"),
        data.get("kamyon_price"),
    )
    if err or not ok:
        return {"success": False, "message": err or "Record not found", "data": {}}
    return {"success": True, "message": "City price updated", "data": {"id": id}}


async def delete_price(id: str):
    ok, err = await svc.delete_city_price(id)
    if err or not ok:
        return {"success": False, "message": err or "Record not found", "data": {}}
    return {"success": True, "message": "City price deleted", "data": {"id": id}}
