# app/routes/order.py
from fastapi import APIRouter, Path, Query, Body, HTTPException
from typing import Optional, Dict, Any
from ..models.order_model import (
    OrderCreateReq, OrderUpdateReq, OrderResponse, OrderListResponse
)
from ..controllers import order_controller as ctrl

router = APIRouter(
    prefix="/api/restaurant",
    tags=["Orders"],
)

@router.post(
    "/{restaurant_id}/orders",
    summary="Create Order",
    description="Yeni sipariş oluştur",
    response_model=dict
)
def create_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    req: OrderCreateReq = Body(..., description="Order creation data")
):
    return ctrl.create_order(restaurant_id, req)


@router.get(
    "/{restaurant_id}/orders/{order_id}",
    summary="Get Order Details",
    description="Sipariş detayını getir",
    response_model=dict
)
def get_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID")
):
    return ctrl.get_order(restaurant_id, order_id)

@router.put(
    "/{restaurant_id}/orders/{order_id}",
    summary="Update Order",
    description="Sipariş güncelle",
    response_model=dict
)
def update_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID"),
    req: OrderUpdateReq = Body(..., description="Order update data")
):
    return ctrl.update_order(restaurant_id, order_id, req)

@router.delete(
    "/{restaurant_id}/orders/{order_id}",
    summary="Delete Order",
    description="Sipariş sil",
    response_model=dict
)
def delete_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID")
):
    return ctrl.delete_order(restaurant_id, order_id)

@router.get(
    "/{restaurant_id}/order-history",
    summary="Get Order History",
    description="Sipariş geçmişini getir",
    response_model=dict
)
def get_order_history(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    status: Optional[str] = Query(None, description="Order status filter"),
    type: Optional[str] = Query(None, description="Order type filter"),
    search: Optional[str] = Query(None, description="Search in code, customer, phone"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset")
):
    return ctrl.get_order_history(
        restaurant_id=restaurant_id,
        status=status,
        order_type=type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )




# order.py'nin sonuna ekle

@router.get(
    "/courier/{courier_id}/assigned-orders",
    summary="Get Courier Assigned Orders",
    description="Kuryeye atanan siparişleri listele",
    response_model=dict
)
async def get_courier_assigned_orders(
    courier_id: str = Path(..., description="Courier ID"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset")
):
    """Kuryeye atanan siparişleri getir endpoint"""
    return await ctrl.get_courier_assigned_orders(courier_id, limit, offset)
