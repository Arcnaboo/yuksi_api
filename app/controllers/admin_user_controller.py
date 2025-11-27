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


async def get_user_commission_rate(user_id: str, claims: dict) -> Dict[str, Any]:
    """
    Kullanıcının komisyon oranını getirir.
    Admin herhangi bir kullanıcının komisyon oranını görebilir.
    Corporate ve Dealer kullanıcıları sadece kendi komisyon oranlarını görebilir.
    """
    # Rol kontrolü
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    
    # Kullanıcı ID'sini al
    current_user_id = claims.get("userId") or claims.get("sub")
    
    # Eğer Admin değilse, sadece kendi ID'sini sorgulayabilir
    if "Admin" not in roles:
        if current_user_id != user_id:
            return {
                "success": False,
                "message": "Sadece kendi komisyon oranınızı görebilirsiniz.",
                "data": {}
            }
    
    success, result = await admin_user_service.get_user_commission_rate(user_id)
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Failed to fetch commission rate",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Komisyon oranı başarıyla getirildi.",
        "data": result
    }


async def set_user_commission_rate(user_id: str, commission_rate: float, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Admin tarafından kullanıcıya komisyon oranı belirler (POST ve PUT için)
    """
    success, result = await admin_user_service.set_user_commission_rate(user_id, commission_rate, description)
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Failed to set commission rate",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Komisyon oranı başarıyla belirlendi.",
        "data": result
    }


async def get_all_users_commissions(
    limit: int = 50,
    offset: int = 0,
    user_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Admin tarafından tüm kullanıcıların (Corporate ve Dealer) komisyon oranlarını getirir
    """
    success, result = await admin_user_service.get_all_users_commissions(
        limit=limit,
        offset=offset,
        user_type=user_type
    )
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Failed to fetch commission rates",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Komisyon oranları başarıyla getirildi.",
        "data": result
    }

