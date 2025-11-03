from typing import Dict, Any
from app.services import dealer_job_service as svc

async def dealer_create_job(data: Dict[str, Any], dealer_id: str) -> Dict[str, Any]:
    success, result = await svc.dealer_create_job(data, dealer_id)
    if not success:
        return {"success": False, "message": result, "data": {}}
    return {"success": True, "message": "Yük başarıyla oluşturuldu.", "data": {"jobId": result}}

async def dealer_get_jobs(dealer_id: str, limit: int, offset: int, delivery_type: str | None) -> Dict[str, Any]:
    success, result = await svc.dealer_get_jobs(dealer_id, limit, offset, delivery_type)
    if not success:
        return {"success": False, "message": result, "data": []}
    return {"success": True, "message": "Yük listesi getirildi.", "data": result}

# --- UPDATE ---
async def dealer_update_job(job_id: str, dealer_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    success, error = await svc.dealer_update_job(job_id, dealer_id, fields)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla güncellendi.", "data": {}}


# --- DELETE ---
async def dealer_delete_job(job_id: str, dealer_id: str) -> Dict[str, Any]:
    success, error = await svc.dealer_delete_job(job_id, dealer_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Yük başarıyla silindi.", "data": {}}

