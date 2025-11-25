from typing import Dict, Any
from app.services import user_job_service as svc


async def user_create_job(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    success, result = await svc.user_create_job(data, user_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}


async def user_get_jobs(
    user_id: str,
    limit: int, 
    offset: int, 
    delivery_type: str | None
) -> Dict[str, Any]:
    success, result = await svc.user_get_jobs(user_id, limit, offset, delivery_type)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}


async def user_get_job(job_id: str, user_id: str) -> Dict[str, Any]:
    success, result = await svc.user_get_job(job_id, user_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük detayı getirildi.", "data": result}


async def user_update_job(
    job_id: str, 
    user_id: str,
    fields: Dict[str, Any]
) -> Dict[str, Any]:
    success, error = await svc.user_update_job(job_id, user_id, fields)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}


async def user_delete_job(job_id: str, user_id: str) -> Dict[str, Any]:
    success, error = await svc.user_delete_job(job_id, user_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}

