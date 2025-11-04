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
    "",
    summary="Create Menu",
    description="Yeni menü ekler.",
    response_model=MenuResponse
)
async def create_menu(
    req: CreateMenuReq,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restorana menü oluşturma endpoint"""
    return await restaurant_menu_controller.create(req, claims)

# -------------------------------
# GET ALL
# -------------------------------
@router.get(
    "",
    summary="Get All Menus",
    description="Tüm menüleri listeler.",
    response_model=List[MenuResponse]
)
async def get_all_menus(
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restoran menülerini getiren endpoint"""
    return await restaurant_menu_controller.get_all(claims)

# -------------------------------
# GET ONE
# -------------------------------
@router.get(
    "/{menu_id}",
    summary="Get Menu",
    description="Belirli bir menüyü ID ile getirir.",
    response_model=MenuResponse
)
async def get_menu(
    menu_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Tek menüyü getiren endpoint"""
    return await restaurant_menu_controller.get_one( menu_id, claims)

# -------------------------------
# UPDATE
# -------------------------------
@router.put(
    "/{menu_id}",
    summary="Update Menu",
    description="Mevcut menüyü günceller.",
    response_model=MenuResponse
)
async def update_menu(
    menu_id: str,
    req: UpdateMenuReq,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Menü güncelleme endpoint"""
    return await restaurant_menu_controller.update(menu_id, req, claims)

# -------------------------------
# DELETE
# -------------------------------
@router.delete(
    "/{menu_id}",
    summary="Delete Menu",
    description="Belirli bir menüyü siler."
)
async def delete_menu(
    menu_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Menü silme endpoint"""
    return await restaurant_menu_controller.delete(menu_id, claims)
