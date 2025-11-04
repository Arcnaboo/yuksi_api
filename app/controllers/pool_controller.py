from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq
from ..services import pool_service as svc

async def get_pool_orders(driver_id: str, claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, list):
        roles = [roles]

    if "Admin" not in roles:
        if claims.get("userId") != driver_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to access this driver's pool orders"
            )

    return await svc.get_pool_orders(driver_id)


async def push_to_pool(restaurant_id: str, req: PoolPushReq, claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to push to pool for this restaurant"
            )

    return await svc.push_to_pool(restaurant_id, req)


async def delete_pool_order(order_id: str, claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to delete pool orders"
        )

    return await svc.delete_pool_order(order_id)
