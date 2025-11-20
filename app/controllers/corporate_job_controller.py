from typing import Dict, Any
from app.services import corporate_job_service as svc

async def corporate_create_job(data: Dict[str, Any], corporate_id: str) -> Dict[str, Any]:
    success, result = await svc.corporate_create_job(data, corporate_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}

async def corporate_get_jobs(corporate_id: str, limit: int, offset: int, delivery_type: str | None) -> Dict[str, Any]:
    success, result = await svc.corporate_get_jobs(corporate_id, limit, offset, delivery_type)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}

# --- UPDATE ---
async def corporate_update_job(job_id: str, corporate_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    success, error = await svc.corporate_update_job(job_id, corporate_id, fields)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}


# --- DELETE ---
async def corporate_delete_job(job_id: str, corporate_id: str) -> Dict[str, Any]:
    success, error = await svc.corporate_delete_job(job_id, corporate_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}

