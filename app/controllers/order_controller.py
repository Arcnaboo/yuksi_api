# app/controllers/order_controller.py
from typing import Dict, Any, List
from ..services import order_service as svc
from ..models.order_model import (
    OrderCreateReq, OrderUpdateReq, OrderResponse, OrderHistoryItem, OrderListResponse
)

async def reject_order_by_courier(
    courier_id: str,
    order_id: str
) -> Dict[str, Any]:
    success, error = await svc.reject_order_by_courier(courier_id, order_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Order rejected successfully", "data": {}}


async def accept_order_by_courier(
    courier_id: str,
    order_id: str
) -> Dict[str, Any]:
    success, error = await svc.accept_order_by_courier(courier_id, order_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Order accepted successfully", "data": {}}

async def get_courier_orders_log(
    courier_id: str,
    limit: int = 50,
    offset: int = 0
    ) -> Dict[str, Any]:
    logs, total_count = await svc.get_courier_orders_log(courier_id, limit, offset)
    return {
        "success": True,
        "message": "Courier orders log retrieved successfully",
        "data": {
            "logs": logs,
            "total_count": total_count
        }
    }


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
        pickup_lat=req.pickup_lat,
        pickup_lng=req.pickup_lng,
        dropoff_lat=req.dropoff_lat,
        dropoff_lng=req.dropoff_lng,
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



# order_controller.py kle

async def get_courier_assigned_orders(
    courier_id: str,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Kuryeye atanan siparişleri getir controller"""
    orders = await svc.get_courier_assigned_orders(courier_id, limit, offset)
    
    return {
        "success": True, 
        "message": "Courier assigned orders retrieved successfully", 
        "data": {
            "orders": orders,
            "total": len(orders)
        }
    }


async def get_order_courier_gps(
    restaurant_id: str,
    order_id: str
) -> Dict[str, Any]:
    """Siparişe atanan kuryenin GPS konumunu getir controller"""
    courier_data, error = await svc.get_order_courier_gps(order_id, restaurant_id)
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    if not courier_data:
        return {"success": False, "message": "Courier GPS data not found", "data": {}}
    
    return {
        "success": True,
        "message": "Order courier GPS location retrieved successfully",
        "data": courier_data
    }


async def mark_order_as_delivered_by_courier(
    courier_id: str,
    order_id: str
) -> Dict[str, Any]:
    success, error = await svc.mark_order_as_delivered_by_courier(courier_id, order_id)
    if not success:
        return {"success": False, "message": error, "data": {}}
    return {"success": True, "message": "Order marked as delivered successfully", "data": {}}