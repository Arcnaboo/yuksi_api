from ..services import courier_service as svc
from uuid import UUID

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

async def list_couriers():
    couriers = await svc.list_couriers()
    return {"success": True, "message": "Courier list", "data": couriers}

async def get_courier_documents(user_id: str):
    documents = await svc.get_courier_documents(user_id)
    if documents is None:
        return {"success": False, "message": "Courier not found", "data": {}}
    return {"success": True, "message": "Courier documents", "data": documents}

async def update_courier_document_status(user_id: str, document_id: str, status: str):
    err = await svc.update_courier_document_status(user_id, document_id, status)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Document status updated", "data": {}}

async def delete_courier_user(user_id: UUID):
    err = await svc.delete_courier_user(user_id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Courier user deleted", "data": {}}
