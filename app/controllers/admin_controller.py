from typing import Any, Dict
from app.services import admin_service as svc

async def register_admin(first_name: str,last_name: str, email: str, password: str) -> Dict[str, Any]:
    result, err = await svc.register_admin(first_name,last_name, email, password)
    if err:
        return { "success": False, "message": err, "data": {} }
    return { "success": True, "message": "Admin oluşturuldu", "data": result }
