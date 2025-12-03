from typing import Dict, Any, List
from app.services import support_permission_service as svc

async def update_support_permissions(
    support_user_id: str,
    access: List[int]
) -> Dict[str, Any]:
    """
    Çağrı merkezi üyesi yetkilerini güncelleme controller'ı
    """
    success, result = await svc.update_support_permissions(
        support_user_id=support_user_id,
        access=access
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Support üyesi yetkileri başarıyla güncellendi.",
        "data": result
    }


async def get_support_permissions(
    support_user_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi üyesi yetkilerini getirme controller'ı
    """
    success, result = await svc.get_support_permissions(
        support_user_id=support_user_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Support üyesi yetkileri başarıyla getirildi.",
        "data": result
    }


async def get_all_support_permissions(
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Tüm çağrı merkezi üyelerinin yetkilerini getirme controller'ı
    """
    success, result = await svc.get_all_support_permissions(
        limit=limit,
        offset=offset
    )
    
    if not success:
        return {"success": False, "message": result, "data": []}
    
    return {
        "success": True,
        "message": "Tüm support üyelerinin yetkileri başarıyla getirildi.",
        "data": result
    }
