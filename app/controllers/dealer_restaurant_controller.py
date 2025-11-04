from typing import Dict, Any
from ..services import dealer_restaurant_service as svc


async def dealer_create_and_link_restaurant(dealer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Bayi için yeni restoran oluştur ve bağla controller"""
    success, restaurant_data, error = await svc.dealer_create_and_link_restaurant(
        dealer_id=dealer_id,
        email=data["email"],
        password=data["password"],
        phone=data["phone"],
        country_id=data["countryId"],
        name=data["name"],
        contact_person=data["contactPerson"],
        tax_number=data["taxNumber"],
        address_line1=data["addresLine1"],  # Typo'lu field name
        address_line2=data.get("addressLine2", ""),
        state_id=data["stateId"],
        city_id=data["cityId"],
        latitude=data["latitude"],
        longitude=data["longitude"],
    )
    
    if not success:
        return {
            "success": False,
            "message": error or "Restoran oluşturulamadı",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Restoran başarıyla oluşturuldu ve bayisine bağlandı",
        "data": restaurant_data
    }


async def dealer_link_existing_restaurant(dealer_id: str, restaurant_id: str) -> Dict[str, Any]:
    """Mevcut restoranı bayisine bağla controller"""
    success, error = await svc.dealer_link_existing_restaurant(dealer_id, restaurant_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Restoran bağlanamadı",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Restoran başarıyla bayisine bağlandı",
        "data": {"restaurant_id": restaurant_id}
    }


async def dealer_get_restaurants(dealer_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Bayinin restoranlarını listele controller"""
    success, result = await svc.dealer_get_restaurants(dealer_id, limit, offset)
    
    if not success:
        return {
            "success": False,
            "message": result if isinstance(result, str) else "Restoranlar getirilemedi",
            "data": []
        }
    
    return {
        "success": True,
        "message": "Restoranlar başarıyla getirildi",
        "data": result if isinstance(result, list) else []
    }


async def dealer_get_restaurant_profile(dealer_id: str, restaurant_id: str) -> Dict[str, Any]:
    """Bayinin belirli bir restoranının profilini getir controller"""
    success, profile, error = await svc.dealer_get_restaurant_profile(dealer_id, restaurant_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Restoran profili getirilemedi",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Restoran profili başarıyla getirildi",
        "data": profile
    }


async def dealer_remove_restaurant(dealer_id: str, restaurant_id: str) -> Dict[str, Any]:
    """Bayiden restoran bağlantısını kaldır controller"""
    success, error = await svc.dealer_remove_restaurant(dealer_id, restaurant_id)
    
    if not success:
        return {
            "success": False,
            "message": error or "Bağlantı kaldırılamadı",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Restoran bağlantısı başarıyla kaldırıldı",
        "data": {"restaurant_id": restaurant_id}
    }

