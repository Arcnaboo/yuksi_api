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
        state_id=req.cityId,      # .NET cityId → bizim state_id
        city_id=req.districtId,   # .NET districtId → bizim city_id
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

