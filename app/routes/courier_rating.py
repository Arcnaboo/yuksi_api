# app/routes/courier_rating.py
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends
from typing import Optional, Dict, Any
from uuid import UUID
from ..models.courier_rating_model import (
    OrderAssignCourierReq, CourierRatingCreateReq, CourierRatingUpdateReq
)
from ..controllers import courier_rating_controller as ctrl
from ..controllers import auth_controller

router = APIRouter(
    prefix="/api/restaurant",
    tags=["Courier Management"],
)

# ==================== KURYE ATAMA ENDPOINTS ====================

@router.post(
    "/{restaurant_id}/orders/{order_id}/assign-courier",
    summary="Assign Courier to Order",
    description="Siparişe kurye ata (sadece paket_servis tipi siparişler için)",
    response_model=Dict[str, Any]
)
async def assign_courier_to_order(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    order_id: UUID = Path(..., description="Order ID"),
    req: OrderAssignCourierReq = Body(..., description="Courier assignment data"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Siparişe kurye ata endpoint"""
    # if str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to assign courier for this restaurant")
    return await ctrl.assign_courier_to_order(str(restaurant_id), str(order_id), str(req.courier_id))

# ==================== KURYE PUANLAMA ENDPOINTS ====================

@router.post(
    "/{restaurant_id}/couriers/{courier_id}/rate",
    summary="Rate Courier",
    description="Kuryeye puan ve yorum ver (sadece teslim edilmiş siparişler için)",
    response_model=Dict[str, Any]
)
async def rate_courier(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    courier_id: UUID = Path(..., description="Courier ID"),
    req: CourierRatingCreateReq = Body(..., description="Courier rating data"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Kurye puanlama endpoint"""
    # if str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to rate courier for this restaurant")
    
    return await ctrl.create_courier_rating(str(restaurant_id), str(courier_id), req)

@router.get(
    "/{restaurant_id}/couriers",
    summary="Get Available Couriers",
    description="Mevcut kuryeleri listele",
    response_model=Dict[str, Any]
)
async def get_couriers(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    """Kurye listesi endpoint"""
    # if claims["roles"][0] == "Restaurant" and str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to view couriers for this restaurant")
    return await ctrl.get_couriers(str(restaurant_id), limit, offset)

@router.get(
    "/{restaurant_id}/couriers/{courier_id}/ratings",
    summary="Get Restaurant's Ratings for Courier",
    description="Bu restoranın belirli kuryeye verdiği puanları getir",
    response_model=Dict[str, Any]
)
async def get_restaurant_courier_ratings(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    courier_id: UUID = Path(..., description="Courier ID"),
    limit: int = Query(50, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
):
    """Restoranın kurye puanları endpoint"""
    # if claims["roles"][0] == "Restaurant" and str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to view ratings for this restaurant")
    return await ctrl.get_courier_ratings(str(restaurant_id), str(courier_id), limit, offset)

@router.get(
    "/couriers/{courier_id}/ratings",
    summary="Get Courier's All Ratings",
    description="Kuryenin tüm puanlarını ve performans özetini getir",
    response_model=Dict[str, Any]
)
async def get_courier_all_ratings(
    courier_id: UUID = Path(..., description="Courier ID"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin", "Courier"]))
):
    """Kuryenin tüm puanları endpoint"""
    # Kuryeler kendi puanlarını görebilir, restoranlar ve adminler tüm kuryelerin puanlarını görebilir
    # if claims["roles"][0] == "Courier" and str(courier_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to view other courier's ratings")
    return await ctrl.get_courier_rating_summary(str(courier_id))

@router.put(
    "/{restaurant_id}/couriers/{courier_id}/ratings/{rating_id}",
    summary="Update Courier Rating",
    description="Kurye puanını ve yorumunu güncelle",
    response_model=Dict[str, Any]
)
async def update_courier_rating(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    courier_id: UUID = Path(..., description="Courier ID"),
    rating_id: UUID = Path(..., description="Rating ID"),
    req: CourierRatingUpdateReq = Body(..., description="Updated rating data"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Kurye puanı güncelleme endpoint"""
    # if str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to update rating for this restaurant")
    return await ctrl.update_courier_rating(str(restaurant_id), str(rating_id), req)

@router.delete(
    "/{restaurant_id}/couriers/{courier_id}/ratings/{rating_id}",
    summary="Delete Courier Rating",
    description="Kurye puanını ve yorumunu sil",
    response_model=Dict[str, Any]
)
async def delete_courier_rating(
    restaurant_id: UUID = Path(..., description="Restaurant ID"),
    courier_id: UUID = Path(..., description="Courier ID"),
    rating_id: UUID = Path(..., description="Rating ID"),
    # claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant"]))
):
    """Kurye puanı silme endpoint"""
    # if str(restaurant_id) != claims["user_id"]:
    #     raise HTTPException(status_code=403, detail="Unauthorized to delete rating for this restaurant")
    return await ctrl.delete_courier_rating(str(restaurant_id), str(rating_id))

















# # app/routes/courier_rating.py
# from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends
# from typing import Optional, Dict, Any
# from uuid import UUID
# from ..models.courier_rating_model import (
#     OrderAssignCourierReq, CourierRatingCreateReq, CourierRatingUpdateReq
# )
# from ..controllers import courier_rating_controller as ctrl
# from ..controllers import auth_controller

# router = APIRouter(
#     prefix="/api/restaurant",
#     tags=["Courier Management"],
# )

# # ==================== KURYE ATAMA ENDPOINTS ====================

# @router.post(
#     "/{restaurant_id}/orders/{order_id}/assign-courier",
#     summary="Assign Courier to Order",
#     description="Siparişe kurye ata (sadece paket_servis tipi siparişler için)",
#     response_model=Dict[str, Any]
# )
# async def assign_courier_to_order(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     order_id: UUID = Path(..., description="Order ID"),
#     req: OrderAssignCourierReq = Body(..., description="Courier assignment data"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Siparişe kurye ata endpoint"""
#     # Restoran sadece kendi siparişlerine kurye atayabilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to assign courier for this restaurant")
#     return await ctrl.assign_courier_to_order(str(restaurant_id), str(order_id), str(req.courier_id))

# # ==================== KURYE PUANLAMA ENDPOINTS ====================

# @router.post(
#     "/{restaurant_id}/couriers/{courier_id}/rate",
#     summary="Rate Courier",
#     description="Kuryeye puan ve yorum ver (sadece teslim edilmiş siparişler için)",
#     response_model=Dict[str, Any]
# )
# async def rate_courier(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     courier_id: UUID = Path(..., description="Courier ID"),
#     req: CourierRatingCreateReq = Body(..., description="Courier rating data"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Kurye puanlama endpoint"""
#     # Restoran sadece kendi kuryelerini puanlayabilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to rate courier for this restaurant")
    
#     return await ctrl.create_courier_rating(str(restaurant_id), str(courier_id), req)

# @router.get(
#     "/{restaurant_id}/couriers",
#     summary="Get Available Couriers",
#     description="Mevcut kuryeleri listele",
#     response_model=Dict[str, Any]
# )
# async def get_couriers(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     limit: int = Query(50, ge=1, le=100, description="Page size"),
#     offset: int = Query(0, ge=0, description="Page offset"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Kurye listesi endpoint"""
#     # Restoran sadece kendi kuryelerini görebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view couriers for this restaurant")
#     return await ctrl.get_couriers(str(restaurant_id), limit, offset)

# @router.get(
#     "/{restaurant_id}/couriers/{courier_id}/ratings",
#     summary="Get Restaurant's Ratings for Courier",
#     description="Bu restoranın belirli kuryeye verdiği puanları getir",
#     response_model=Dict[str, Any]
# )
# async def get_restaurant_courier_ratings(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     courier_id: UUID = Path(..., description="Courier ID"),
#     limit: int = Query(50, ge=1, le=100, description="Page size"),
#     offset: int = Query(0, ge=0, description="Page offset"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Restoranın kurye puanları endpoint"""
#     # Restoran sadece kendi kurye puanlarını görebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view ratings for this restaurant")
#     return await ctrl.get_courier_ratings(str(restaurant_id), str(courier_id), limit, offset)

# @router.get(
#     "/couriers/{courier_id}/ratings",
#     summary="Get Courier's All Ratings",
#     description="Kuryenin tüm puanlarını ve performans özetini getir",
#     response_model=Dict[str, Any]
# )
# async def get_courier_all_ratings(
#     courier_id: UUID = Path(..., description="Courier ID"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin", "Courier"]))
# ):
#     """Kuryenin tüm puanları endpoint"""
#     # Kurye sadece kendi puanlarını görebilir (Admin ve Restaurant hariç)
#     if "Admin" not in claims.get("roles", []) and "Restaurant" not in claims.get("roles", []) and str(courier_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to view other courier's ratings")
#     return await ctrl.get_courier_rating_summary(str(courier_id))

# @router.put(
#     "/{restaurant_id}/couriers/{courier_id}/ratings/{rating_id}",
#     summary="Update Courier Rating",
#     description="Kurye puanını ve yorumunu güncelle",
#     response_model=Dict[str, Any]
# )
# async def update_courier_rating(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     courier_id: UUID = Path(..., description="Courier ID"),
#     rating_id: UUID = Path(..., description="Rating ID"),
#     req: CourierRatingUpdateReq = Body(..., description="Updated rating data"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Kurye puanı güncelleme endpoint"""
#     # Restoran sadece kendi kurye puanlarını güncelleyebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to update rating for this restaurant")
#     return await ctrl.update_courier_rating(str(restaurant_id), str(rating_id), req)

# @router.delete(
#     "/{restaurant_id}/couriers/{courier_id}/ratings/{rating_id}",
#     summary="Delete Courier Rating",
#     description="Kurye puanını ve yorumunu sil",
#     response_model=Dict[str, Any]
# )
# async def delete_courier_rating(
#     restaurant_id: UUID = Path(..., description="Restaurant ID"),
#     courier_id: UUID = Path(..., description="Courier ID"),
#     rating_id: UUID = Path(..., description="Rating ID"),
#     claims: Dict[str, Any] = Depends(auth_controller.require_roles(["Restaurant", "Admin"]))
# ):
#     """Kurye puanı silme endpoint"""
#     # Restoran sadece kendi kurye puanlarını silebilir (Admin hariç)
#     if "Admin" not in claims.get("roles", []) and str(restaurant_id) != claims.get("user_id"):
#         raise HTTPException(status_code=403, detail="Unauthorized to delete rating for this restaurant")
#     return await ctrl.delete_courier_rating(str(restaurant_id), str(rating_id))