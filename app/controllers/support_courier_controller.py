from typing import Dict, Any, Optional
from app.services import support_courier_service as svc


async def get_support_couriers(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> Dict[str, Any]:
    """
    Çağrı merkezi için kurye listesi controller'ı
    """
    success, result = await svc.get_support_couriers(
        limit=limit,
        offset=offset,
        search=search
    )
    
    if not success:
        return {"success": False, "message": result, "data": []}
    
    return {
        "success": True,
        "message": "Kurye listesi başarıyla getirildi.",
        "data": result
    }


async def get_support_courier_detail(
    courier_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi için kurye detayı controller'ı
    """
    success, result = await svc.get_support_courier_detail(
        courier_id=courier_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Kurye detayı başarıyla getirildi.",
        "data": result
    }


async def get_support_courier_packages(
    courier_id: str,
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Çağrı merkezi için kurye paketleri controller'ı
    """
    success, result = await svc.get_support_courier_packages(
        courier_id=courier_id,
        limit=limit,
        offset=offset,
        status=status
    )
    
    if not success:
        return {"success": False, "message": result, "data": []}
    
    return {
        "success": True,
        "message": "Kurye paketleri başarıyla getirildi.",
        "data": result
    }


async def get_support_courier_location(
    courier_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi için kurye konumu controller'ı
    """
    success, result = await svc.get_support_courier_location(
        courier_id=courier_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Kurye konumu başarıyla getirildi.",
        "data": result
    }


async def get_support_courier_stats(
    courier_id: str
) -> Dict[str, Any]:
    """
    Çağrı merkezi için kurye istatistikleri controller'ı
    """
    success, result = await svc.get_support_courier_stats(
        courier_id=courier_id
    )
    
    if not success:
        return {"success": False, "message": result, "data": {}}
    
    return {
        "success": True,
        "message": "Kurye istatistikleri başarıyla getirildi.",
        "data": result
    }

