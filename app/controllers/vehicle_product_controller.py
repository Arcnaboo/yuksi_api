from typing import Dict, Any
from uuid import UUID
from app.services import vehicle_product_service as service


async def create_vehicle_product(data: Dict[str, Any]) -> Dict[str, Any]:
    """Yeni araç ürünü oluştur"""
    product_id, error = await service.create_vehicle_product(data)
    
    if error:
        return {
            "success": False,
            "message": error,
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Araç ürünü başarıyla oluşturuldu",
        "data": {"id": str(product_id)}
    }


async def list_vehicle_products(
    template: str = None,
    is_active: bool = None
) -> Dict[str, Any]:
    """Araç ürünlerini listele"""
    products, error = await service.list_vehicle_products(template, is_active)
    
    if error:
        return {
            "success": False,
            "message": error,
            "data": []
        }
    
    return {
        "success": True,
        "message": "Araç ürünleri başarıyla getirildi",
        "data": products or []
    }


async def get_vehicle_product(product_id: UUID) -> Dict[str, Any]:
    """Araç ürünü detayını getir"""
    product, error = await service.get_vehicle_product(product_id)
    
    if error:
        return {
            "success": False,
            "message": error,
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Araç ürünü başarıyla getirildi",
        "data": product
    }


async def update_vehicle_product(
    product_id: UUID,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Araç ürününü güncelle"""
    success, error = await service.update_vehicle_product(product_id, data)
    
    if error:
        return {
            "success": False,
            "message": error,
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Araç ürünü başarıyla güncellendi",
        "data": {"id": str(product_id)}
    }


async def delete_vehicle_product(product_id: UUID) -> Dict[str, Any]:
    """Araç ürününü sil"""
    success, error = await service.delete_vehicle_product(product_id)
    
    if error:
        return {
            "success": False,
            "message": error,
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Araç ürünü başarıyla silindi",
        "data": {"id": str(product_id)}
    }

