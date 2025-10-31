from typing import Dict, Any, Optional
from app.services import restaurant_job_service as svc

async def restaurant_create_job(data: Dict[str, Any], restaurant_id: Optional[str]) -> Dict[str, Any]:
    success, result = await svc.restaurant_create_job(data, restaurant_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}

async def restaurant_get_jobs(limit: int, offset: int, delivery_type: str | None, restaurant_id: Optional[str]) -> Dict[str, Any]:
    success, result = await svc.restaurant_get_jobs(limit, offset, delivery_type, restaurant_id)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}

async def restaurant_update_job(job_id: str, fields: Dict[str, Any], restaurant_id: Optional[str]) -> Dict[str, Any]:
    success, error = await svc.restaurant_update_job(job_id, fields, restaurant_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}

async def restaurant_delete_job(job_id: str, restaurant_id: Optional[str]) -> Dict[str, Any]:
    success, error = await svc.restaurant_delete_job(job_id, restaurant_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}

