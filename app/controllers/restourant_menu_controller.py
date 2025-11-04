from fastapi import HTTPException, status
from uuid import UUID
from ..models.restourant_menu_model import CreateMenuReq, UpdateMenuReq
from ..services import restourant_menu_service as service


# ----------------------------------------------------
# ROLE CHECK HELPER
# ----------------------------------------------------
def _check_permissions(claims: dict, restaurant_id: str):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles:
        if claims.get("userId") != str(restaurant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized to access this restaurant's resources"
            )


# ----------------------------------------------------
# CREATE MENU
# ----------------------------------------------------
async def create(restaurant_id: UUID, req: CreateMenuReq, claims: dict):
    _check_permissions(claims, restaurant_id)
    return await service.create(req)


# ----------------------------------------------------
# GET ALL MENUS
# ----------------------------------------------------
async def get_all(restaurant_id: UUID, claims: dict):
    _check_permissions(claims, restaurant_id)
    return await service.get_all(restaurant_id)


# ----------------------------------------------------
# GET ONE MENU
# ----------------------------------------------------
async def get_one(restaurant_id: UUID, menu_id: UUID, claims: dict):
    _check_permissions(claims, restaurant_id)
    return await service.get_one(restaurant_id, menu_id)


# ----------------------------------------------------
# UPDATE MENU
# ----------------------------------------------------
async def update(restaurant_id: UUID, menu_id: UUID, req: UpdateMenuReq, claims: dict):
    _check_permissions(claims, restaurant_id)

    # Menü objesinde id yoksa route’tan gelen id’yi ata
    req.id = str(menu_id)
    req.restourant_id = str(restaurant_id)

    return await service.update(req)


# ----------------------------------------------------
# DELETE MENU
# ----------------------------------------------------
async def delete(restaurant_id: UUID, menu_id: UUID, claims: dict):
    _check_permissions(claims, restaurant_id)
    return await service.delete(restaurant_id, menu_id)
