# app/controllers/order_controller.py
from typing import Dict, Any, List
from ..services import order_service as svc
from ..models.order_model import (
    OrderCreateReq, OrderUpdateReq, OrderResponse, OrderHistoryItem, OrderListResponse
)

async def create_order(restaurant_id: str, req: OrderCreateReq) -> Dict[str, Any]:
    """Sipariş oluştur controller"""
    # Ürünleri dict'e çevir
    items = [item.dict() for item in req.items]
    
    result, error = await svc.create_order(
        restaurant_id=restaurant_id,
        customer=req.customer,
        phone=req.phone,
        address=req.address,
        delivery_address=req.delivery_address,
        order_type=req.type.value,
        amount=req.amount,
        carrier_type=req.carrier_type,
        vehicle_type=req.vehicle_type,
        cargo_type=req.cargo_type,
        special_requests=req.special_requests,
        items=items
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Order created successfully", "data": result}

async def get_order(restaurant_id: str, order_id: str) -> Dict[str, Any]:
    """Sipariş detayı controller"""
    order = await svc.get_order(order_id, restaurant_id)
    if not order:
        return {"success": False, "message": "Order not found", "data": {}}
    
    return {"success": True, "message": "Order details", "data": order}

async def update_order(restaurant_id: str, order_id: str, req: OrderUpdateReq) -> Dict[str, Any]:
    """Sipariş güncelle controller"""
    # Güncellenecek alanları hazırla
    update_data = {}
    
    if req.customer is not None:
        update_data['customer'] = req.customer
    if req.phone is not None:
        update_data['phone'] = req.phone
    if req.address is not None:
        update_data['address'] = req.address
    if req.delivery_address is not None:
        update_data['delivery_address'] = req.delivery_address
    if req.type is not None:
        update_data['type'] = req.type.value
    if req.status is not None:
        update_data['status'] = req.status.value
    if req.amount is not None:
        update_data['amount'] = req.amount
    if req.cargo_type is not None:
        update_data['cargo_type'] = req.cargo_type
    if req.special_requests is not None:
        update_data['special_requests'] = req.special_requests
    if req.items is not None:
        update_data['items'] = [item.dict() for item in req.items]
    
    success, error = await svc.update_order(order_id, restaurant_id, **update_data)
    
    if not success:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Order updated successfully", "data": {}}

async def delete_order(restaurant_id: str, order_id: str) -> Dict[str, Any]:
    """Sipariş sil controller"""
    success, error = await svc.delete_order(order_id, restaurant_id)
    
    if not success:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Order deleted successfully", "data": {}}

async def list_orders(
    restaurant_id: str,
    status: str = None,
    order_type: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Sipariş listesi controller"""
    orders, total_count, total_amount = await svc.list_orders(
        restaurant_id=restaurant_id,
        status=status,
        order_type=order_type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return {
        "success": True,
        "message": "Orders list",
        "data": {
            "orders": orders,
            "total_count": total_count,
            "total_amount": total_amount
        }
    }

async def get_order_history(
    restaurant_id: str,
    status: str = None,
    order_type: str = None,
    search: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Sipariş geçmişi controller"""
    orders, total_count, total_amount = await svc.get_order_history(
        restaurant_id=restaurant_id,
        status=status,
        order_type=order_type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return {
        "success": True,
        "message": "Order history",
        "data": {
            "orders": orders,
            "total_count": total_count,
            "total_amount": total_amount
        }
    }



