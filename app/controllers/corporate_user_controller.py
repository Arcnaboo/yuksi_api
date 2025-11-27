from typing import Dict, Any
from app.services import corporate_user_service as svc


async def create_corporate_user(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Admin tarafından Corporate kullanıcı oluştur
    """
    ok, res = await svc.create_corporate_user(data)
    if not ok:
        error_msg = res if isinstance(res, str) else "Kurumsal kullanıcı oluşturulamadı"
        # Hata mesajlarını Türkçe'ye çevir
        if "Email already registered" in error_msg or "Bu email adresi zaten kayıtlı" in error_msg:
            error_msg = "Bu email adresi zaten kayıtlı"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Kurumsal kullanıcı başarıyla oluşturuldu",
        "data": res
    }


async def list_corporate_users(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Tüm Corporate kullanıcıları listele
    """
    ok, res = await svc.list_corporate_users(limit, offset)
    if not ok:
        return {
            "success": False,
            "message": res if isinstance(res, str) else "Kurumsal kullanıcılar listelenemedi",
            "data": []
        }
    return {
        "success": True,
        "message": "Kurumsal kullanıcılar listelendi",
        "data": res
    }


async def get_corporate_user(user_id: str) -> Dict[str, Any]:
    """
    Bir Corporate kullanıcıyı getir
    """
    ok, res = await svc.get_corporate_user(user_id)
    if not ok:
        error_msg = res if isinstance(res, str) else "Kurumsal kullanıcı bulunamadı"
        if "Corporate user not found" in error_msg:
            error_msg = "Kurumsal kullanıcı bulunamadı"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Kurumsal kullanıcı bilgileri",
        "data": res
    }


async def update_corporate_user(user_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Corporate kullanıcıyı güncelle
    """
    ok, err = await svc.update_corporate_user(user_id, fields)
    if not ok:
        error_msg = err if err else "Kurumsal kullanıcı güncellenemedi"
        if "No fields to update" in error_msg:
            error_msg = "Güncellenecek alan bulunamadı"
        elif "No valid fields to update" in error_msg:
            error_msg = "Geçerli güncellenecek alan bulunamadı"
        elif "Corporate user not found" in error_msg:
            error_msg = "Kurumsal kullanıcı bulunamadı"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Kurumsal kullanıcı başarıyla güncellendi",
        "data": {}
    }


async def delete_corporate_user(user_id: str) -> Dict[str, Any]:
    """
    Corporate kullanıcıyı sil
    """
    ok, err = await svc.delete_corporate_user(user_id)
    if not ok:
        error_msg = err if err else "Kurumsal kullanıcı silinemedi"
        if "Corporate user not found" in error_msg:
            error_msg = "Kurumsal kullanıcı bulunamadı"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Kurumsal kullanıcı başarıyla silindi",
        "data": {}
    }


async def get_corporate_profile(user_id: str) -> Dict[str, Any]:
    """Kurumsal kullanıcı profil görüntüleme controller"""
    profile = await svc.get_corporate_profile(user_id)
    if not profile:
        return {"error": "Kurumsal kullanıcı bulunamadı"}, 404
    return profile


async def update_corporate_profile(user_id: str, req) -> Dict[str, Any]:
    """Kurumsal kullanıcı profil güncelleme controller"""
    # fullAddress geldiyse addressLine1/2'ye böl
    full_addr = getattr(req, "fullAddress", None) or getattr(req, "full_address", None)
    
    ok, err = await svc.update_corporate_profile(
        user_id,
        email=getattr(req, "email", None),
        phone=getattr(req, "phone", None),
        first_name=getattr(req, "firstName", None),
        last_name=getattr(req, "lastName", None),
        full_address=full_addr,
        country_id=getattr(req, "countryId", None),
        state_id=getattr(req, "stateId", None),
        city_id=getattr(req, "cityId", None),
    )
    
    if not ok:
        error_msg = err if err else "Profil güncellenemedi"
        return {
            "success": False,
            "message": error_msg,
            "data": {}
        }
    return {
        "success": True,
        "message": "Profil başarıyla güncellendi",
        "data": {}
    }
