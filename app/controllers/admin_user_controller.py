from typing import Dict, Any, Optional
from app.services import admin_user_service


async def get_all_users(
    user_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Admin tarafından tüm kullanıcıları getirir
    """
    success, result = await admin_user_service.get_all_users(
        user_type=user_type,
        search=search,
        limit=limit,
        offset=offset
    )
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Failed to fetch users",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Users fetched successfully",
        "data": result
    }


async def set_user_commission_rate(user_id: str, commission_rate: float, description: str | None = None) -> Dict[str, Any]:
    """
    Admin tarafından kullanıcıya komisyon oranı belirleme (ID'ye göre otomatik tespit - tüm tablolara bakar)
    """
    ok, res = await admin_user_service.set_user_commission_rate(user_id, commission_rate, description)
    if not ok:
        error_msg = res if isinstance(res, str) else "Komisyon oranı belirlenemedi"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Komisyon oranı başarıyla belirlendi",
        "data": res
    }
