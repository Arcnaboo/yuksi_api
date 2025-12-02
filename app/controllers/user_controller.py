from typing import Dict, Any
from app.services import user_service


async def register(
    email: str,
    password: str,
    phone: str,
    first_name: str,
    last_name: str
) -> Dict[str, Any]:
    result = await user_service.register_user(
        email, password, phone, first_name, last_name
    )
    
    if not result:
        return {
            "success": False,
            "message": "Email already registered or Default role not found",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": result
    }


async def login(email: str, password: str) -> Dict[str, Any]:
    result = await user_service.login_user(email, password)
    
    if not result:
        return {
            "success": False,
            "message": "Wrong email or password",
            "data": {}
        }
    
    if result == "banned":
        return {
            "success": False,
            "message": "User is deleted or inactive",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Login successful",
        "data": result
    }


async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Bireysel kullanıcı profil görüntüleme controller"""
    profile = await user_service.get_user_profile(user_id)
    if not profile:
        return {
            "success": False,
            "message": "Kullanıcı bulunamadı",
            "data": {}
        }
    return {
        "success": True,
        "message": "Profil başarıyla getirildi",
        "data": profile
    }


async def update_user_profile(user_id: str, req) -> Dict[str, Any]:
    """Bireysel kullanıcı profil güncelleme controller"""
    ok, err = await user_service.update_user_profile(
        user_id,
        email=getattr(req, "email", None),
        phone=getattr(req, "phone", None),
        first_name=getattr(req, "firstName", None),
        last_name=getattr(req, "lastName", None),
    )
    
    if not ok:
        return {
            "success": False,
            "message": err or "Profil güncellenemedi",
            "data": {}
        }
    
    # Güncellenmiş profili getir
    updated_profile = await user_service.get_user_profile(user_id)
    return {
        "success": True,
        "message": "Profil başarıyla güncellendi",
        "data": updated_profile or {}
    }
