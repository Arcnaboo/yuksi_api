# app/routes/order.py
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends
from typing import Optional, Dict, Any
from ..models.order_model import (
    OrderCreateReq, OrderUpdateReq, OrderResponse, OrderListResponse
)
from ..controllers import order_controller as ctrl
from ..controllers import auth_controller

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
async def create_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    req: OrderCreateReq = Body(..., description="Order creation data"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to create orders for this restaurant")
    return await ctrl.create_order(restaurant_id, req)


@router.get(
    "/{restaurant_id}/orders/{order_id}",
    summary="Get Order Details",
    description="Sipariş detayını getir",
    response_model=dict
)
async def get_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant", "Admin", "Courier"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles and "Courier" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view orders for this restaurant")
    return await ctrl.get_order(restaurant_id, order_id)

@router.put(
    "/{restaurant_id}/orders/{order_id}",
    summary="Update Order",
    description="Sipariş güncelle",
    response_model=dict
)
async def update_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID"),
    req: OrderUpdateReq = Body(..., description="Order update data"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to update orders for this restaurant")
    return await ctrl.update_order(restaurant_id, order_id, req)

@router.delete(
    "/{restaurant_id}/orders/{order_id}",
    summary="Delete Order",
    description="Sipariş sil",
    response_model=dict
)
async def delete_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to delete orders for this restaurant")
    return await ctrl.delete_order(restaurant_id, order_id)

@router.get(
    "/{restaurant_id}/order-history",
    summary="Get Order History",
    description="Sipariş geçmişini getir",
    response_model=dict
)
async def get_order_history(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    status: Optional[str] = Query(None, description="Order status filter"),
    type: Optional[str] = Query(None, description="Order type filter"),
    search: Optional[str] = Query(None, description="Search in code, customer, phone"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view order history for this restaurant")
    return await ctrl.get_order_history(
        restaurant_id=restaurant_id,
        status=status,
        order_type=type,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )


@router.post(
    "/courier/{courier_id}/orders/{order_id}/reject",
    summary="Reject Order by Courier",
    description="Kuryenin bir siparişi reddetmesi",
    response_model=dict
)
async def reject_order_by_courier(
    courier_id: str = Path(..., description="Courier ID"),
    order_id: str = Path(..., description="Order ID")
):
    return await ctrl.reject_order_by_courier(courier_id, order_id)


@router.post(
    "/courier/{courier_id}/orders/{order_id}/accept",
    summary="Accept Order by Courier",
    description="Kuryenin bir siparişi kabul etmesi",
    response_model=dict
)
async def accept_order_by_courier(
    courier_id: str = Path(..., description="Courier ID"),
    order_id: str = Path(..., description="Order ID")
):
    return await ctrl.accept_order_by_courier(courier_id, order_id)

@router.get(
    "/courier/{courier_id}/orders-log",
    summary="Get Courier Orders Log",
    description="Kuryenin sipariş kabul/red loglarını getirir.",
    response_model=dict
)
async def get_courier_orders_log(
    courier_id: str = Path(..., description="Courier ID"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset")
):
    return await ctrl.get_courier_orders_log(courier_id, limit, offset)

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
    offset: int = Query(0, ge=0, description="Page offset"),
    claims: dict = Depends(auth_controller.require_roles(["Courier", "Admin", "Restaurant"]))
):
    """Kuryeye atanan siparişleri getir endpoint"""
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles and "Restaurant" not in roles:
        if claims.get("userId") != courier_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view assigned orders for this courier")
    return await ctrl.get_courier_assigned_orders(courier_id, limit, offset)


@router.get(
    "/{restaurant_id}/orders/{order_id}/courier-gps",
    summary="Get Order Courier GPS Location",
    description="Siparişe atanan kuryenin canlı GPS konumunu getirir.",
    response_model=dict
)
async def get_order_courier_gps(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID")
):
    """Siparişe atanan kuryenin GPS konumunu getir endpoint"""
    return await ctrl.get_order_courier_gps(restaurant_id, order_id)


# ✅ GET NEARBY COURIERS (max 10km, sorted by distance, active and online only)
@router.get(
    "/couriers/nearby",
    summary="Get Nearby Couriers (max 10km, active and online)",
    description="Restorana 10 km içindeki aktif ve online olan tüm kuryeleri mesafeye göre sıralar (en yakından en uzağa). Restaurant token'dan otomatik olarak alınır.",
    response_model=dict
)
async def get_nearby_couriers(
    limit: int = Query(50, ge=1, le=200, description="Maksimum kurye sayısı"),
    claims: dict = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Restorana yakın kuryeleri getir endpoint (max 10 km, sadece aktif ve online)"""
    from ..controllers import restaurant_controller as restaurant_ctrl
    
    # Restaurant ID'yi token'dan al
    restaurant_id = claims.get("userId") or claims.get("sub")
    if not restaurant_id:
        raise HTTPException(status_code=403, detail="Token'da restoran ID bulunamadı")
    
    return await restaurant_ctrl.get_nearby_couriers(str(restaurant_id), limit)






