from typing import Any, Dict, Literal, Optional
from app.services import admin_service as svc

async def register_admin(first_name: str,last_name: str, email: str, password: str) -> Dict[str, Any]:
    result, err = await svc.register_admin(first_name,last_name, email, password)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Admin oluşturuldu", "data": result }

async def get_all_jobs(limit: int = 50, offset: int = 0, delivery_type: str | None = None, job_type: Literal["User", "Restaurant", "Dealer", "Corporate"] | None = None) -> Dict[str, Any]:
    result, err = await svc.get_all_jobs(limit, offset, delivery_type, job_type)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Tüm işler getirildi", "data": result }