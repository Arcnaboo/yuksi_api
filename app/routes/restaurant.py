from fastapi import APIRouter, Body
from typing import List
from ..models.restaurant_model import (
    RestaurantRegisterReq,
    RestaurantRegisterResponse,
    RestaurantListItem,
    RestaurantProfileResponse,
    RestaurantProfileUpdateReq
)
from ..controllers import restaurant_controller as ctrl


router = APIRouter(
    prefix="/api/Restaurant",
    tags=["Restaurant"],
)


@router.post(
    "/register",
    summary="Restaurant Register",
    description="Yeni restoran kaydı oluşturur.",
    response_model=RestaurantRegisterResponse
)
def restaurant_register(req: RestaurantRegisterReq):
    """Restaurant kayıt endpoint"""
    result = ctrl.restaurant_register(req)
    if not result.get("success"):
        return result
    return result["data"]




@router.get(
    "/list",
    summary="Get Restaurant List",
    description="Tüm restoranları listeler.",
    response_model=List[RestaurantListItem]
)
def list_restaurants():
    """Restaurant listesi endpoint"""
    result = ctrl.list_restaurants()
    return result["data"]


@router.get(
    "/{restaurant_id}/profile",
    summary="Get Restaurant Profile",
    description="Restaurant profil bilgilerini getirir.",
    response_model=RestaurantProfileResponse
)
async def get_profile(restaurant_id: str):
    """Restaurant profil görüntüleme"""
    return await ctrl.get_restaurant_profile(restaurant_id)

@router.put(
    "/{restaurant_id}/profile",
    summary="Update Restaurant Profile",
    description="Restaurant profil bilgilerini günceller."
)
async def update_profile(restaurant_id: str, req: RestaurantProfileUpdateReq):
    """Restaurant profil güncelleme"""
    return await ctrl.update_restaurant_profile(restaurant_id, req)

