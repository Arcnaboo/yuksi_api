from typing import Dict, Any
from app.services import admin_job_service as svc

async def admin_create_job(data: Dict[str, Any]) -> Dict[str, Any]:
    success, result = await svc.admin_create_job(data)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}

async def admin_get_jobs(limit: int, offset: int, delivery_type: str | None) -> Dict[str, Any]:
    success, result = await svc.admin_get_jobs(limit, offset, delivery_type)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}

async def admin_get_restaurant_jobs(
    limit: int, 
    offset: int, 
    delivery_type: str | None, 
    restaurant_id: str | None
) -> Dict[str, Any]:
    success, result = await svc.admin_get_restaurant_jobs(limit, offset, delivery_type, restaurant_id)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Restaurant yük listesi getirildi.", "data": result}

# --- UPDATE ---
async def admin_update_job(job_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    success, error = await svc.admin_update_job(job_id, fields)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}


# --- DELETE ---
async def admin_delete_job(job_id: str) -> Dict[str, Any]:
    success, error = await svc.admin_delete_job(job_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}