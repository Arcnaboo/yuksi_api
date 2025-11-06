from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq
from ..services import pool_service as svc

async def get_pool_orders(claims: dict, page: int, size: int):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles and "Courier" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this driver's pool orders"
        )

    driver_id = claims.get("userId")

    return await svc.get_pool_orders(driver_id, page, size)


async def push_to_pool(req: PoolPushReq, claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles and "Restaurant" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to push to pool for this restaurant"
        )
    
    restaurant_id = claims.get("userId")

    return await svc.push_to_pool(req, restaurant_id)


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
