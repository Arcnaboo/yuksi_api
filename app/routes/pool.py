from fastapi import APIRouter, Depends
from typing import List
from ..models.pool_model import PoolPushReq, PoolOrderRes
from ..controllers import pool_controller as ctrl
from ..controllers.auth_controller import require_roles

router = APIRouter(
    prefix="/api/Pool",
    tags=["Pool"],
)

@router.post(
    "",
    summary="Push to Pool",
    description="Push data to the pool",
    response_model=PoolOrderRes
)
async def push_to_pool(req: PoolPushReq, claims: dict = Depends(require_roles(["Admin", "Restaurant"]))):
    return await ctrl.push_to_pool(req, claims)

@router.get(
    "/my-orders",
    summary="Get My Pool Orders",
    description="Retrieve pool orders for the authenticated restaurant",
    response_model=List[PoolOrderRes]
)
async def get_my_pool_orders(page: int = 1, size: int = 50,claims: dict = Depends(require_roles(["Admin", "Restaurant"]))):
    return await ctrl.get_my_pool_orders(claims, page=page, size=size)

@router.get(
    "/nearby-orders",
    summary="Get Pool Orders",
    description="Retrieve pool orders for the authenticated driver with nearest orders first",
    response_model=List[PoolOrderRes],
)
async def get_pool_orders(
    page: int = 1,
    size: int = 50,
    claims: dict = Depends(require_roles(["Admin", "Courier"]))
):
    return await ctrl.get_nearby_pool_orders(claims, page=page, size=size)

@router.delete(
    "/{order_id}",
    summary="Delete Pool Order",
    description="Delete an order from the pool",
)
async def delete_pool_order(order_id: str, claims: dict = Depends(require_roles(["Admin", "Restaurant"]))):
    return await ctrl.delete_pool_order(order_id, claims)