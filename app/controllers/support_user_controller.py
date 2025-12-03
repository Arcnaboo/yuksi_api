from typing import Dict, Any, List, Optional
from app.services import support_user_service as svc

async def create_support_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: str,
    access: List[int] = None
) -> Dict[str, Any]:
    """
    Çağrı merkezi üyesi oluşturma controller'ı
    """
    success, result = await svc.create_support_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        phone=phone,
        access=access or []
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Support üyesi başarıyla oluşturuldu.",
        "data": result
    }


async def delete_support_user(
    support_user_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi üyesi silme controller'ı (soft delete)
    """
    success, error = await svc.delete_support_user(
        support_user_id=support_user_id
    )
    
    if not success:
        return {"success": False, "message": error, "data": {}}
    
    return {
        "success": True,
        "message": "Support üyesi başarıyla silindi.",
        "data": {}
    }


async def update_support_user(
    support_user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    is_active: Optional[bool] = None,
    access: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Çağrı merkezi üyesi güncelleme controller'ı
    """
    success, result = await svc.update_support_user(
        support_user_id=support_user_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        is_active=is_active,
        access=access
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Support üyesi başarıyla güncellendi.",
        "data": result
    }

