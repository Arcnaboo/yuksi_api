from app.services.file_service import get_public_url
from app.services import general_setting_service as service

async def create(data):
    err = await service.create_general_setting(data)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "General setting created", "data": {}}

async def get():
    gs = await service.get_general_setting()
    if not gs:
        return {"success": False, "message": "Not found", "data": {}}

    if gs.get("logo_path"):
        gs["logo_url"] = get_public_url(gs["logo_path"])  # ✅ otomatik URL ekliyoruz

    return {"success": True, "message": "OK", "data": gs}

async def update(gs_id: str, fields: dict):
    err = await service.update_general_setting(gs_id, fields)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "General setting updated", "data": {}}
