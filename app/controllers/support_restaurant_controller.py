from typing import Dict, Any, Optional
from app.services import support_restaurant_service as svc


async def get_support_restaurants(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Çağrı merkezi için restoran listesi controller'ı
    """
    success, result = await svc.get_support_restaurants(
        limit=limit,
        offset=offset,
        search=search
    )
    
    if not success:
        return {"success": False, "message": result, "data": []}
    
    return {
        "success": True,
        "message": "Restoran listesi başarıyla getirildi.",
        "data": result
    }


async def get_support_restaurant_detail(
    restaurant_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi için restoran detayı controller'ı
    """
    success, result = await svc.get_support_restaurant_detail(
        restaurant_id=restaurant_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Restoran detayı başarıyla getirildi.",
        "data": result
    }


async def update_support_restaurant(
    restaurant_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    contact_person: Optional[str] = None,
    tax_number: Optional[str] = None,
    address_line1: Optional[str] = None,
    address_line2: Optional[str] = None,
    opening_hour: Optional[str] = None,
    closing_hour: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Çağrı merkezi için restoran güncelleme controller'ı
    """
    success, error = await svc.update_support_restaurant(
        restaurant_id=restaurant_id,
        email=email,
        phone=phone,
        name=name,
        contact_person=contact_person,
        tax_number=tax_number,
        address_line1=address_line1,
        address_line2=address_line2,
        opening_hour=opening_hour,
        closing_hour=closing_hour,
        latitude=latitude,
        longitude=longitude,
    )
    
    if not success:
        return {"success": False, "message": error, "data": {}}
    
    return {
        "success": True,
        "message": "Restoran başarıyla güncellendi.",
        "data": {}
    }


async def get_support_restaurant_package(
    restaurant_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi için restoran paket durumu controller'ı
    """
    success, result = await svc.get_support_restaurant_package(
        restaurant_id=restaurant_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Restoran paket durumu başarıyla getirildi.",
        "data": result
    }

