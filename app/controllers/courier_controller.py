from ..services import courier_service as svc

async def courier_register1(req):
    user_id, err = await svc.courier_register_step1(
        phone=req.phone,
        first_name=req.firstName,
        last_name=req.lastName,
        email=req.email,
        password=req.password,
        country_id=req.countryId,
        confirm_contract=req.confirmContract,
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "CourierRegister step1 completed", "data": {"userId": user_id}}

async def courier_register2(user_id: str, req):
    err = await svc.courier_register_step2(user_id, req.workingType)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "CourierRegister step2 completed", "data": {"userId": user_id}}

async def courier_register3(user_id: str, req):
    err = await svc.courier_register_step3(
        user_id,
        req.vehicleType,
        req.vehicleCapacity,
        req.stateId,
        req.vehicleYear,
        req.documents,
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "CourierRegister step3 completed", "data": {"userId": user_id}}

async def get_courier_profile(user_id: str): 
    profile = await svc.get_courier(user_id)
    if not profile:
        return {"success": False, "message": "Courier not found", "data": {}}
    return {"success": True, "message": "Courier profile", "data": profile}

async def list_couriers():
    couriers = await svc.list_couriers()
    return {"success": True, "message": "Courier list", "data": couriers}