from typing import Optional, Dict, Any
from ..services import restaurant_service as svc


async def restaurant_register(req):
    """Restaurant kayıt controller"""
    restaurant_data, err = await svc.restaurant_register(
        email=req.email,
        password=req.password,
        phone=req.phone,
        country_id=req.countryId,
        name=req.name,
        contact_person=req.contactPerson,
        tax_number=req.taxNumber,
        address_line1=req.addresLine1,  # Typo'lu field
        address_line2=req.addressLine2 or "",
        state_id=req.stateId,     # .NET stateId → bizim state_id
        city_id=req.cityId,       # .NET cityId → bizim city_id
    )
    
    if err:
        return {"success": False, "message": err, "data": {}}
    
    return {
        "success": True,
        "message": "Restaurant registered successfully",
        "data": restaurant_data
    }


async def list_restaurants():
    """Restaurant listesi controller"""
    restaurants = await svc.list_restaurants()
    return {
        "success": True,
        "message": "Restaurant list",
        "data": restaurants
    }


async def get_restaurant_profile(restaurant_id: str):
    """Restaurant profil görüntüleme controller"""
    profile = await svc.get_restaurant_profile(restaurant_id)
    if not profile:
        return {"error": "Restaurant bulunamadı"}, 404
    return profile

async def update_restaurant_profile(restaurant_id: str, req):
    """Restaurant profil güncelleme controller"""
    success, error = await svc.update_restaurant_profile(
        restaurant_id=restaurant_id,
        email=req.email,
        phone=req.phone,
        contact_person=req.contactPerson,
        address_line1=req.addressLine1,
        address_line2=req.addressLine2,
        opening_hour=req.openingHour,
        closing_hour=req.closingHour
    )
    
    if not success:
        return {"error": error}, 400
        
    return {"message": "Profil başarıyla güncellendi"}


async def assign_courier_to_restaurant(
    restaurant_id: str, 
    courier_id: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Restorana kurye ata controller"""
    success, error = await svc.assign_courier_to_restaurant(
        restaurant_id=restaurant_id,
        courier_id=courier_id,
        notes=notes
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Courier assigned to restaurant successfully", "data": {}}

async def get_restaurant_couriers(
    restaurant_id: str,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Restoranın kuryelerini getir controller"""
    couriers = await svc.get_restaurant_couriers(restaurant_id, limit, offset)
    stats = await svc.get_restaurant_courier_stats(restaurant_id)
    
    return {
        "success": True, 
        "message": "Restaurant couriers retrieved successfully", 
        "data": {
            "stats": stats,
            "couriers": couriers
        }
    }

async def remove_courier_from_restaurant(
    restaurant_id: str, 
    assignment_id: str
) -> Dict[str, Any]:
    """Restorandan kurye atamasını kaldır controller"""
    success, error = await svc.remove_courier_from_restaurant(
        assignment_id=assignment_id,
        restaurant_id=restaurant_id
    )
    
    if error:
        return {"success": False, "message": error, "data": {}}
    
    return {"success": True, "message": "Courier removed from restaurant successfully", "data": {}}
async def admin_update_restaurant(restaurant_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """Admin restoran güncelleme controller"""
    success, error = await svc.admin_update_restaurant(restaurant_id, fields)
    if not success:
        return {"success": False, "message": error or "Update failed", "data": {}}
    return {"success": True, "message": "Restaurant updated successfully", "data": {}}


async def admin_delete_restaurant(restaurant_id: str) -> Dict[str, Any]:
    """Admin restoran silme controller"""
    success, error = await svc.admin_delete_restaurant(restaurant_id)
    if not success:
        return {"success": False, "message": error or "Delete failed", "data": {}}
    return {"success": True, "message": "Restaurant deleted successfully", "data": {}}


async def get_restaurant_couriers_gps(restaurant_id: str) -> Dict[str, Any]:
    """Restoranın kuryelerinin GPS konumlarını getir controller"""
    couriers = await svc.get_restaurant_couriers_gps(restaurant_id)
    
    if not couriers:
        return {
            "success": True,
            "message": "No couriers found or no GPS data available",
            "data": {"couriers": []}
        }
    
    return {
        "success": True,
        "message": "Restaurant couriers GPS locations retrieved successfully",
        "data": {"couriers": couriers}
    }