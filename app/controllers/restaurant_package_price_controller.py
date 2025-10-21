from app.services import restaurant_package_price_service as service

async def create_or_update_price(data):
    ok, result = await service.create_or_update_price(data)
    if not ok:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Price saved", "data": result}

async def list_prices():
    ok, data = await service.list_prices()
    if not ok:
        return {"success": False, "message": data, "data": []}
    return {"success": True, "message": "Prices fetched", "data": data}
