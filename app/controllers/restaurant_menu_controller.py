from fastapi import HTTPException, status
from ..models.restaurant_menu_model import CreateMenuReq, UpdateMenuReq
from ..services import restaurant_menu_service as service


# ----------------------------------------------------
# ROLE CHECK HELPER
# ----------------------------------------------------
def _check_permissions(claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles and "Restaurant" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this restaurant's resources"
        )
    
    return claims.get("userId")


# ----------------------------------------------------
# CREATE MENU
# ----------------------------------------------------
async def create(req: CreateMenuReq, claims: dict):
    restaurant_id = _check_permissions(claims)
    return await service.create(restaurant_id ,req)


# ----------------------------------------------------
# GET ALL MENUS
# ----------------------------------------------------
async def get_all(claims: dict):
    restaurant_id = _check_permissions(claims)
    return await service.get_all(restaurant_id)


# ----------------------------------------------------
# GET ONE MENU
# ----------------------------------------------------
async def get_one(menu_id: str, claims: dict):
    restaurant_id = _check_permissions(claims)
    return await service.get_one(restaurant_id, menu_id)


# ----------------------------------------------------
# UPDATE MENU
# ----------------------------------------------------
async def update(menu_id: str, req: UpdateMenuReq, claims: dict):
    restaurant_id = _check_permissions(claims)
    return await service.update(restaurant_id, menu_id, req)


# ----------------------------------------------------
# DELETE MENU
# ----------------------------------------------------
async def delete(menu_id: str, claims: dict):
    restaurant_id = _check_permissions(claims)
    return await service.delete(restaurant_id, menu_id)
