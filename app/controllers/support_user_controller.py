from typing import Dict, Any, List
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

