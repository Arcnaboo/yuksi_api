from fastapi import APIRouter, Body
from typing import Any, List, Union
from fastapi import APIRouter, Body, Path, Query, Depends, HTTPException
from ..controllers.auth_controller import require_roles
from ..models.restaurant_model import RestaurantAdminUpdateReq
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
    description="Yeni restoran kaydı oluşturur. Sadece Admin ve Bayi erişebilir.",
    response_model=Union[RestaurantRegisterResponse, Any],
    dependencies=[Depends(require_roles(["Admin", "Dealer"]))]
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
async def list_restaurants(
    _=Depends(require_roles(["Admin", "Dealer"]))
):
    """Restaurant listesi endpoint"""
    result = await ctrl.list_restaurants()
    return result['data']


@router.get(
    "/{restaurant_id}/profile",
    summary="Get Restaurant Profile",
    description="Restaurant profil bilgilerini getirir.",
    response_model=Union[RestaurantProfileResponse, Any]
)
async def get_profile(
    restaurant_id: str,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view this restaurant profile")
    """Restaurant profil görüntüleme"""
    return await ctrl.get_restaurant_profile(restaurant_id)

@router.put(
    "/{restaurant_id}/profile",
    summary="Update Restaurant Profile",
    description="Restaurant profil bilgilerini günceller."
)
async def update_profile(
    restaurant_id: str,
    req: RestaurantProfileUpdateReq,
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to update this restaurant profile")
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
    notes: Optional[str] = Body(None, description="Assignment notes"),
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restorana kurye atama endpoint"""
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to assign courier to this restaurant")
    
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
    offset: int = Query(0, ge=0, description="Page offset"),
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restoranın kuryelerini getir endpoint"""
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to view couriers for this restaurant")
    
    return await ctrl.get_restaurant_couriers(restaurant_id, limit, offset)

@router.delete(
    "/{restaurant_id}/couriers/{assignment_id}",
    summary="Remove Courier from Restaurant",
    description="Restorandan kurye atamasını kaldır",
    response_model=Dict[str, Any]
)
async def remove_courier_from_restaurant(
    restaurant_id: str = Path(..., description="Restaurant ID"),
    assignment_id: str = Path(..., description="Assignment ID"),
    claims: dict = Depends(require_roles(["Restaurant", "Admin"]))
):
    """Restorandan kurye atamasını kaldır endpoint"""
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Admin" not in roles:
        if claims.get("userId") != restaurant_id:
            raise HTTPException(status_code=403, detail="Unauthorized to remove courier from this restaurant")
    
    return await ctrl.remove_courier_from_restaurant(restaurant_id, assignment_id)


# ✅ ADMIN UPDATE RESTAURANT
@router.put(
    "/{restaurant_id}",
    summary="Admin: Restoran Güncelle",
    description="Yalnızca Admin tarafından restoran bilgilerini günceller.",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=Dict[str, Any]
)
async def admin_update_restaurant(
    restaurant_id: str = Path(..., description="Restoran UUID"),
    body: RestaurantAdminUpdateReq = ...,
):
    """Admin restoran güncelleme endpoint"""
    fields = body.dict(exclude_unset=True, by_alias=True)
    # fullAddress desteği: adres_line1/2 yerine tek alanla güncelleme ve bölme
    full_addr = fields.pop("fullAddress", None) or getattr(body, "full_address", None)
    if full_addr:
        import re
        parts = [p.strip() for p in re.split(r",|;|\n", str(full_addr)) if p.strip()]
        if parts:
            fields["address_line1"] = parts[0]
            if "address_line2" not in fields:
                fields["address_line2"] = ", ".join(parts[1:]) if len(parts) > 1 else ""
        else:
            fields["address_line1"] = str(full_addr).strip()
            fields.setdefault("address_line2", "")
    return await ctrl.admin_update_restaurant(restaurant_id, fields)


# ✅ ADMIN DELETE RESTAURANT
@router.delete(
    "/{restaurant_id}",
    summary="Admin: Restoran Sil",
    description="Yalnızca Admin tarafından restoranı siler.",
    dependencies=[Depends(require_roles(["Admin"]))],
    response_model=Dict[str, Any]
)
async def admin_delete_restaurant(
    restaurant_id: str = Path(..., description="Restoran UUID")
):
    """Admin restoran silme endpoint"""
    return await ctrl.admin_delete_restaurant(restaurant_id)


# ✅ GET RESTAURANT COURIERS GPS
@router.get(
    "/{restaurant_id}/couriers/gps",
    summary="Get Restaurant Couriers GPS Locations",
    description="Restoranın kendi kuryelerinin canlı GPS konumlarını getirir.",
    response_model=Dict[str, Any]
)
async def get_restaurant_couriers_gps(
    restaurant_id: str = Path(..., description="Restoran UUID")
):
    """Restoranın kuryelerinin GPS konumlarını getir endpoint"""
    return await ctrl.get_restaurant_couriers_gps(restaurant_id)

