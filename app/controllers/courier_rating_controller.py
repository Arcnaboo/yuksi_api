
# app/controllers/courier_rating_controller.py
from typing import Dict, Any, List, Optional
from uuid import UUID
from ..services import courier_rating_service as svc
from ..models.courier_rating_model import (
    OrderAssignCourierReq, CourierRatingCreateReq, CourierRatingUpdateReq, CourierRatingResponse
)

# ==================== KURYE ATAMA CONTROLLERS ====================

async def assign_courier_to_order(restaurant_id: str, order_id: str, courier_id: str) -> Dict[str, Any]:
    """Siparişe kurye ata controller"""
    success, error = svc.assign_courier_to_order(order_id, restaurant_id, courier_id)
    
    if not success:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Courier assigned successfully", "data": {}}

# ==================== KURYE PUANLAMA CONTROLLERS ====================

async def create_courier_rating(restaurant_id: str, courier_id: str, req: CourierRatingCreateReq) -> Dict[str, Any]:
    """Kurye puanlama oluştur controller"""
    result, error = svc.create_courier_rating(
        restaurant_id=restaurant_id,
        courier_id=courier_id,
        order_id=str(req.order_id),
        rating=req.rating,
        comment=req.comment
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Rating created successfully", "data": result}

async def update_courier_rating(
    restaurant_id: str, 
    rating_id: str, 
    req: CourierRatingUpdateReq
) -> Dict[str, Any]:
    """Kurye puanlamasını güncelle controller"""
    success, error = svc.update_courier_rating(
        rating_id=rating_id,
        restaurant_id=restaurant_id,
        rating=req.rating,
        comment=req.comment
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Rating updated successfully", "data": {}}

async def delete_courier_rating(restaurant_id: str, rating_id: str) -> Dict[str, Any]:
    """Kurye puanlamasını sil controller"""
    success, error = svc.delete_courier_rating(
        rating_id=rating_id,
        restaurant_id=restaurant_id
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Rating deleted successfully", "data": {}}

async def get_courier_ratings(
    restaurant_id: str,
    courier_id: str = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Kurye puanlamalarını getir controller"""
    ratings = svc.get_courier_ratings(
        restaurant_id=restaurant_id,
        courier_id=courier_id,
        limit=limit,
        offset=offset
    )
    
    return {"success": True, "message": "Ratings retrieved", "data": ratings}

async def get_courier_rating_summary(courier_id: str) -> Dict[str, Any]:
    """Kurye puanlama özeti controller"""
    summary = svc.get_courier_rating_summary(courier_id=courier_id)
    
    if not summary:
        return {"success": False, "message": "Courier not found", "data": {}}
    
    return {"success": True, "message": "Rating summary", "data": summary}

async def get_couriers(restaurant_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """Mevcut kuryeleri getir controller"""
    couriers = svc.get_available_couriers(limit=limit, offset=offset)
    
    return {"success": True, "message": "Couriers retrieved", "data": couriers}

