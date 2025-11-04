from uuid import UUID
from fastapi import APIRouter, Depends, Path, Query, Body, HTTPException
from app.controllers import dealer_restaurant_controller as ctrl
from app.models.dealer_restaurant_model import DealerCreateRestaurantReq, DealerLinkRestaurantReq
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/dealer/restaurants", tags=["Dealer Restaurants"])


# ✅ POST: Bayi için yeni restoran oluştur ve bağla
@router.post(
    "",
    summary="Yeni Restoran Oluştur ve Bağla",
    description="Bayi için yeni restoran oluşturur ve bayisine otomatik olarak bağlar.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def create_and_link_restaurant(
    body: DealerCreateRestaurantReq = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayi için yeni restoran oluştur ve bağla endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_create_and_link_restaurant(str(dealer_id), body.model_dump())


# ✅ POST: Mevcut restoranı bayisine bağla
@router.post(
    "/restourant_id",
    summary="Mevcut Restoranı Bağla",
    description="Mevcut bir restoranı bayisine bağlar.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def link_existing_restaurant(
    body: DealerLinkRestaurantReq = Body(...),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Mevcut restoranı bayisine bağla endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_link_existing_restaurant(str(dealer_id), body.restaurant_id)


# ✅ GET: Bayinin restoranlarını listele
@router.get(
    "",
    summary="Bayinin Restoranlarını Listele",
    description="Bayinin bağlı olduğu tüm restoranları listeler.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_dealer_restaurants(
    limit: int = Query(50, ge=1, le=200, description="Maksimum restoran sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin restoranlarını listele endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_restaurants(str(dealer_id), limit, offset)


# ✅ GET: Bayinin belirli bir restoranının profilini getir
@router.get(
    "/{restaurant_id}",
    summary="Restoran Profilini Getir",
    description="Bayinin kendisine ait bir restoranın detaylı profilini getirir.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_restaurant_profile(
    restaurant_id: UUID = Path(..., description="Profilini görüntülemek istediğiniz restoranın UUID'si"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin belirli bir restoranının profilini getir endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_restaurant_profile(str(dealer_id), str(restaurant_id))


# ✅ GET: Bayinin restoranının kuryelerini listele
@router.get(
    "/{restaurant_id}/couriers",
    summary="Restoran Kuryelerini Getir",
    description="Bayinin kendisine ait bir restoranın kuryelerini listeler.",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def get_restaurant_couriers(
    restaurant_id: UUID = Path(..., description="Kuryelerini görüntülemek istediğiniz restoranın UUID'si"),
    limit: int = Query(50, ge=1, le=200, description="Maksimum kurye sayısı"),
    offset: int = Query(0, ge=0, description="Sayfalama offset"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Bayinin belirli bir restoranının kuryelerini getir endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_get_restaurant_couriers(
        str(dealer_id), str(restaurant_id), limit, offset
    )





# ✅ DELETE: Restoran bağlantısını kaldır
@router.delete(
    "/{restaurant_id}",
    summary="Restoran Bağlantısını Kaldır",
    description="Bayiden restoran bağlantısını kaldırır (restoran silinmez, sadece bağlantı kesilir).",
    dependencies=[Depends(require_roles(["Dealer"]))],
)
async def remove_restaurant(
    restaurant_id: UUID = Path(..., description="Kaldırılacak restoranın UUID'si"),
    claims: dict = Depends(require_roles(["Dealer"]))
):
    """Restoran bağlantısını kaldır endpoint"""
    dealer_id = claims.get("userId") or claims.get("sub")
    if not dealer_id:
        raise HTTPException(status_code=403, detail="Token'da bayi ID bulunamadı")
    
    return await ctrl.dealer_remove_restaurant(str(dealer_id), str(restaurant_id))

