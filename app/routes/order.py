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
async def create_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    req: OrderCreateReq = Body(..., description="Order creation data")
):
    return await ctrl.create_order(restaurant_id, req)


@router.get(
    "/{restaurant_id}/orders/{order_id}",
    summary="Get Order Details",
    description="Sipariş detayını getir",
    response_model=dict
)
async def get_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID")
):
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
    req: OrderUpdateReq = Body(..., description="Order update data")
):
    return await ctrl.update_order(restaurant_id, order_id, req)

@router.delete(
    "/{restaurant_id}/orders/{order_id}",
    summary="Delete Order",
    description="Sipariş sil",
    response_model=dict
)
async def delete_order(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    order_id: str = Path(..., description="Order ID")
):
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
    offset: int = Query(0, ge=0, description="Page offset")
):
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
    offset: int = Query(0, ge=0, description="Page offset")
):
    """Kuryeye atanan siparişleri getir endpoint"""
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








# # app/routes/order.py
# from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends
# from typing import Optional, Dict, Any
# from ..models.order_model import (
#     OrderCreateReq, OrderUpdateReq, OrderResponse, OrderListResponse
# )
# from ..controllers import order_controller as ctrl
# from ..controllers import auth_controller

# router = APIRouter(
#     prefix="/api/restaurant",
#     tags=["Orders"],
# )

# @router.post(
#     "/{restaurant_id}/orders",
#     summary="Create Order",
#     description="Yeni sipariş oluştur",
#     response_model=dict
# )
# async def create_order(
#     restaurant_id: str = Path(..., description="Restaurant ID"),
#     req: OrderCreateReq = Body(..., description="Order creation data"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     # Restoran sadece kendi siparişlerini oluşturabilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and restaurant_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to create orders for this restaurant")
#     return await ctrl.create_order(restaurant_id, req)


# @router.get(
#     "/{restaurant_id}/orders/{order_id}",
#     summary="Get Order Details",
#     description="Sipariş detayını getir",
#     response_model=dict
# )
# async def get_order(
#     restaurant_id: str = Path(..., description="Restaurant ID"),
#     order_id: str = Path(..., description="Order ID"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin", "Courier"]))
# ):
#     # Restoran sadece kendi siparişlerini görebilir (Admin ve Courier hariç)
#     if "Admin" not in claims.get("roles", []) and "Courier" not in claims.get("roles", []) and restaurant_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view orders for this restaurant")
#     return await ctrl.get_order(restaurant_id, order_id)

# @router.put(
#     "/{restaurant_id}/orders/{order_id}",
#     summary="Update Order",
#     description="Sipariş güncelle",
#     response_model=dict
# )
# async def update_order(
#     restaurant_id: str = Path(..., description="Restaurant ID"),
#     order_id: str = Path(..., description="Order ID"),
#     req: OrderUpdateReq = Body(..., description="Order update data"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     # Restoran sadece kendi siparişlerini güncelleyebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and restaurant_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to update orders for this restaurant")
#     return await ctrl.update_order(restaurant_id, order_id, req)

# @router.delete(
#     "/{restaurant_id}/orders/{order_id}",
#     summary="Delete Order",
#     description="Sipariş sil",
#     response_model=dict
# )
# async def delete_order(
#     restaurant_id: str = Path(..., description="Restaurant ID"),
#     order_id: str = Path(..., description="Order ID"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     # Restoran sadece kendi siparişlerini silebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and restaurant_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to delete orders for this restaurant")
#     return await ctrl.delete_order(restaurant_id, order_id)

# @router.get(
#     "/{restaurant_id}/order-history",
#     summary="Get Order History",
#     description="Sipariş geçmişini getir",
#     response_model=dict
# )
# async def get_order_history(
#     restaurant_id: str = Path(..., description="Restaurant ID"),
#     status: Optional[str] = Query(None, description="Order status filter"),
#     type: Optional[str] = Query(None, description="Order type filter"),
#     search: Optional[str] = Query(None, description="Search in code, customer, phone"),
#     start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
#     end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
#     limit: int = Query(50, ge=1, le=100, description="Page size"),
#     offset: int = Query(0, ge=0, description="Page offset"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     # Restoran sadece kendi sipariş geçmişini görebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and restaurant_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view order history for this restaurant")
#     return await ctrl.get_order_history(
#         restaurant_id=restaurant_id,
#         status=status,
#         order_type=type,
#         search=search,
#         start_date=start_date,
#         end_date=end_date,
#         limit=limit,
#         offset=offset
#     )




# # order.py'nin sonuna ekle

# @router.get(
#     "/courier/{courier_id}/assigned-orders",
#     summary="Get Courier Assigned Orders",
#     description="Kuryeye atanan siparişleri listele",
#     response_model=dict
# )
# async def get_courier_assigned_orders(
#     courier_id: str = Path(..., description="Courier ID"),
#     limit: int = Query(50, ge=1, le=100, description="Page size"),
#     offset: int = Query(0, ge=0, description="Page offset"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Courier", "Admin", "Restaurant"]))
# ):
#     """Kuryeye atanan siparişleri getir endpoint"""
#     # Kurye sadece kendi siparişlerini görebilir (Admin ve Restaurant hariç)
#     if "Admin" not in claims.get("roles", []) and "Restaurant" not in claims.get("roles", []) and courier_id != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view orders for this courier")
#     return await ctrl.get_courier_assigned_orders(courier_id, limit, offset)






