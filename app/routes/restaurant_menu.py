from typing import List
from fastapi import APIRouter, Depends
from ..models.restaurant_menu_model import CreateMenuReq, UpdateMenuReq, MenuResponse
from ..controllers import restaurant_menu_controller
from ..controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/Restaurant/Menu", tags=["Restaurant Menu"])

# -------------------------------
# CREATE
# -------------------------------
@router.post(
    "/{restaurant_id}/",
    summary="Create Menu",
    description="Yeni menü ekler.",
    response_model=MenuResponse
)
async def create_menu(
    restaurant_id: str,
    req: CreateMenuReq,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restorana menü oluşturma endpoint"""
    return await restaurant_menu_controller.create(restaurant_id, req, claims)

# -------------------------------
# GET ALL
# -------------------------------
@router.get(
    "/{restaurant_id}/",
    summary="Get All Menus",
    description="Tüm menüleri listeler.",
    response_model=List[MenuResponse]
)
async def get_all_menus(
    restaurant_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restoran menülerini getiren endpoint"""
    return await restaurant_menu_controller.get_all(restaurant_id, claims)

# -------------------------------
# GET ONE
# -------------------------------
@router.get(
    "/{restaurant_id}/{menu_id}/",
    summary="Get Menu",
    description="Belirli bir menüyü ID ile getirir.",
    response_model=MenuResponse
)
async def get_menu(
    restaurant_id: str,
    menu_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Tek menüyü getiren endpoint"""
    return await restaurant_menu_controller.get_one(restaurant_id, menu_id, claims)

# -------------------------------
# UPDATE
# -------------------------------
@router.put(
    "/{restaurant_id}/{menu_id}/",
    summary="Update Menu",
    description="Mevcut menüyü günceller.",
    response_model=MenuResponse
)
async def update_menu(
    restaurant_id: str,
    menu_id: str,
    req: UpdateMenuReq,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Menü güncelleme endpoint"""
    return await restaurant_menu_controller.update(restaurant_id, menu_id, req, claims)

# -------------------------------
# DELETE
# -------------------------------
@router.delete(
    "/{restaurant_id}/{menu_id}/",
    summary="Delete Menu",
    description="Belirli bir menüyü siler."
)
async def delete_menu(
    restaurant_id: str,
    menu_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Menü silme endpoint"""
    return await restaurant_menu_controller.delete(restaurant_id, menu_id, claims)
