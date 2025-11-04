from fastapi import APIRouter, Body, Depends
from ..models.pool_model import PoolPushReq
from ..controllers import pool_controller as ctrl
from ..controllers.auth_controller import require_roles

router = APIRouter(
    prefix="/api/Pool",
    tags=["Pool"],
)

@router.post(
    "/{restaurant_id}/",
    summary="Push to Pool",
    description="Push data to the pool",
)
async def push_to_pool(restaurant_id: str ,req: PoolPushReq, claims: dict = Depends(require_roles(["Admin", "Restaurant"]))):
    return ctrl.push_to_pool(restaurant_id, req, claims)

@router.get(
    "/{driver_id}/",
    summary="Get Pool Orders",
    description="Retrieve orders from the pool",
)
async def get_pool_orders(driver_id: str, claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.get_pool_orders(driver_id, claims)

@router.delete(
    "/{order_id}/",
    summary="Delete Pool Order",
    description="Delete an order from the pool",
)
async def delete_pool_order(order_id: str, claims: dict = Depends(require_roles(["Admin"]))):
    return await ctrl.delete_pool_order(order_id, claims)

