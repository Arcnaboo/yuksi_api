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

