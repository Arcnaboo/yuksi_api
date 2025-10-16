from ..services import restaurant_service as svc


def restaurant_register(req):
    """Restaurant kayıt controller"""
    restaurant_data, err = svc.restaurant_register(
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


def list_restaurants():
    """Restaurant listesi controller"""
    restaurants = svc.list_restaurants()
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
        address_line1=req.addressLine1,
        address_line2=req.addressLine2,
        opening_hour=req.openingHour,
        closing_hour=req.closingHour
    )
    
    if not success:
        return {"error": error}, 400
        
    return {"message": "Profil başarıyla güncellendi"}

