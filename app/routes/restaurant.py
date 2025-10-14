from fastapi import APIRouter, Body
from typing import List
from ..models.restaurant_model import (
    RestaurantRegisterReq,
    RestaurantRegisterResponse,
    RestaurantListItem
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

