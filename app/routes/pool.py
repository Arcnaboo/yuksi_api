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
    "/",
    summary="Get Pool Orders",
    description="Retrieve orders from the pool",
    response_model=List[PoolOrderRes]
)
async def get_pool_orders(claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.get_pool_orders(claims, page=1, size=50)

@router.get(
    "/{page}/{size}",
    summary="Get Pool Orders",
    description="Retrieve orders from the pool with pagination",
    response_model=List[PoolOrderRes]
)
async def get_pool_orders(page: int, size: int, claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.get_pool_orders(claims, page=page, size=size)

@router.delete(
    "/{order_id}",
    summary="Delete Pool Order",
    description="Delete an order from the pool",
)
async def delete_pool_order(order_id: str, claims: dict = Depends(require_roles(["Admin"]))):
    return await ctrl.delete_pool_order(order_id, claims)

