from app.services import campaign_service as svc

async def list_campaigns():
    rows, err = await svc.list_campaigns()
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Campaigns listed", "data": rows}

async def get_campaign(id: str):
    row, err = await svc.get_campaign(id)
    if err or not row:
        return {"success": False, "message": "Not found", "data": {}}
    return {"success": True, "message": "Campaign fetched", "data": row}

async def create_campaign(data: dict):
    row, err = await svc.create_campaign(
        data.get("title"),
        data.get("discount_rate"),
        data.get("rule"),
        data.get("content"),
        data.get("file_id")
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Campaign created", "data": row}

async def update_campaign(id: str, data: dict):
    ok, err = await svc.update_campaign(id, data)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Updated", "data": {"id": id}}

async def delete_campaign(id: str):
    ok, err = await svc.delete_campaign(id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Deleted", "data": {"id": id}}
