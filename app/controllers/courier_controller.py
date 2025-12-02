from fastapi import HTTPException, status

from app.models.courier_model import CourierOrderStatusChangeReq
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
        req.dealer_id,
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

# async def list_couriers():
#     couriers = await svc.list_couriers()
#     return {"success": True, "message": "Courier list", "data": couriers}

async def list_couriers(_claims: dict):
    roles = _claims.get("role") or _claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Dealer" in roles:
        dealer_id = _claims.get("userId")
        couriers = await svc.list_couriers(dealer_id=dealer_id)
    else:
        couriers = await svc.list_couriers()
    return {"success": True, "message": "Courier list", "data": couriers}

async def get_courier_documents(user_id: str, _claims: dict):
    roles = _claims.get("role") or _claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Dealer" in roles:
        dealer_id = _claims.get("userId")
        documents = await svc.get_courier_documents(user_id, dealer_id=dealer_id)
    else:
        documents = await svc.get_courier_documents(user_id)
    if documents is None:
        return {"success": False, "message": "Courier not found", "data": {}}
    return {"success": True, "message": "Courier documents", "data": documents}

async def update_courier_document_status(user_id: str, document_id: str, status: str, _claims: dict):
    roles = _claims.get("role") or _claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]
    if "Dealer" in roles:
        dealer_id = _claims.get("userId")
        err = await svc.update_courier_document_status(user_id, document_id, status, dealer_id=dealer_id)
    else:
        err = await svc.update_courier_document_status(user_id, document_id, status)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Document status updated", "data": {}}

async def delete_courier_user(user_id: UUID):
    err = await svc.delete_courier_user(user_id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Courier user deleted", "data": {}}


async def update_courier_profile(user_id: str, req):
    err = await svc.update_courier_profile(
        driver_id=user_id,
        first_name=req.firstName,
        last_name=req.lastName,
        email=(req.email.lower().strip() if req.email else None),
        phone=(req.phone.strip() if req.phone else None),
        country_id=req.countryId,
    )
    if err:
        return {"success": False, "message": err, "data": {}}
    
    # Güncellenmiş profili getir
    updated_profile = await svc.get_courier(user_id)
    if not updated_profile:
        return {
            "success": True,
            "message": "Courier profile updated",
            "data": {}
        }
    
    return {
        "success": True,
        "message": "Courier profile updated",
        "data": updated_profile
    }

async def get_dealers_by_state(state_id: int):
    dealers = await svc.get_dealers_by_state(state_id)
    return {"success": True, "message": "Dealers list", "data": dealers}

async def get_courier_history(_claims: dict, date: str = None, page: int = 1, page_size: int = 25):
    roles = _claims.get("role") or _claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Courier" not in roles:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this courier's resources"
        )
    
    user_id = _claims.get("userId")

    try:
        user_id = UUID(user_id)
    except ValueError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    return await svc.get_courier_history(
        courier_id=user_id,
        date=date,
        page=page,
        page_size=page_size
    )

async def change_courier_order_status(_claims: dict, order_id: str, req: CourierOrderStatusChangeReq):
    roles = _claims.get("role") or _claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Courier" not in roles:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this courier's resources"
        )
    
    user_id = _claims.get("userId")

    try:
        user_id = UUID(user_id)
    except ValueError:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    err = await svc.change_courier_order_status(
        courier_id=user_id,
        order_id=order_id,
        new_status=req.new_status
    )
    if err:
        return {"success": False, "message": err}
    return {"success": True, "message": "Sipariş durumu başarıyla güncellendi."}