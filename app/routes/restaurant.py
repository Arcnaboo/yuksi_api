from fastapi import APIRouter, Body
from typing import Any, List, Union
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from typing import List, Dict, Any, Optional
from ..models.restaurant_model import (
    RestaurantRegisterReq,
    RestaurantRegisterResponse,
    RestaurantListItem,
    RestaurantProfileResponse,
    RestaurantProfileUpdateReq
)
from ..controllers import restaurant_controller as ctrl
from ..controllers import auth_controller



router = APIRouter(
    prefix="/api/Restaurant",
    tags=["Restaurant"],
)


@router.post(
    "/register",
    summary="Restaurant Register",
    description="Yeni restoran kaydı oluşturur.",
    response_model=Union[RestaurantRegisterResponse, Any]
)
async def restaurant_register(req: RestaurantRegisterReq):
    """Restaurant kayıt endpoint"""
    result = await ctrl.restaurant_register(req)
    if not result.get('success'):
        return result
    return result['data']




@router.get(
    "/list",
    summary="Get Restaurant List",
    description="Tüm restoranları listeler.",
    response_model= Union[List[RestaurantListItem]]
)
async def list_restaurants():
    """Restaurant listesi endpoint"""
    result = await ctrl.list_restaurants()
    return result['data']


@router.get(
    "/{restaurant_id}/profile",
    summary="Get Restaurant Profile",
    description="Restaurant profil bilgilerini getirir.",
    response_model=Union[RestaurantProfileResponse, Any]
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



@router.post(
    "/{restaurant_id}/assign-courier",
    summary="Assign Courier to Restaurant",
    description="Restorana kurye ata",
    response_model=Dict[str, Any]
)
async def assign_courier_to_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    courier_id: str = Body(..., description="Courier ID"),
    notes: Optional[str] = Body(None, description="Assignment notes")
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Restorana kurye atama endpoint"""
    # Restoran sadece kendine kurye atayabilir
    # if restaurant_id != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to assign courier to this restaurant")
    
    return await ctrl.assign_courier_to_restaurant(restaurant_id, courier_id, notes)

@router.get(
    "/{restaurant_id}/couriers",
    summary="Get Restaurant Couriers",
    description="Restoranın kuryelerini listele",
    response_model=Dict[str, Any]
)
async def get_restaurant_couriers(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset")
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Restoranın kuryelerini getir endpoint"""
    # Restoranlar sadece kendi kuryelerini görebilir
    # if restaurant_id != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to view couriers for this restaurant")
    
    return await ctrl.get_restaurant_couriers(restaurant_id, limit, offset)

@router.delete(
    "/{restaurant_id}/couriers/{assignment_id}",
    summary="Remove Courier from Restaurant",
    description="Restorandan kurye atamasını kaldır",
    response_model=Dict[str, Any]
)
async def remove_courier_from_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    assignment_id: str = Path(..., description="Assignment ID")
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Restorandan kurye atamasını kaldır endpoint"""
    # Restoran sadece kendi kuryelerini silebilir
    # if restaurant_id != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to remove courier from this restaurant")
    
    return await ctrl.remove_courier_from_restaurant(restaurant_id, assignment_id)

