from typing import Any, Dict, List
from fastapi import HTTPException, status
from app.models.vehicles_models import VehicleRequest, VehicleResponse, VehicleTypeResponse
import app.services.vehicle_service as svc

def _check_permissions(claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles and "Courier" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this endpoint"
        )
    
    return claims.get("userId"), roles

async def get_all_vehicles(size: int, offset: int) -> Dict[str, Any]:
    result = await svc.get_all_vehicles(size=size, offset=offset)
    return {"success":True, "message": "Fecthed all vehicles.", "data": result}

async def create_vehicle(req: VehicleRequest, claims: dict) -> Dict[str, Any]:
    userId, roles = _check_permissions(claims)
    if "Admin" in roles:
        result = await svc.create_vehicle(req, req.driver_id)
    else:
        result = await svc.create_vehicle(req, userId)
    return {"success":True, "message": "Vehicle created.", "data": result}

async def get_vehicle(vehicle_id: str, claims: dict)-> Dict[str, Any]:
    userId, roles = _check_permissions(claims)
    result = await svc.get_vehicle(vehicle_id)
    return {"success":True, "message": "Fetched vehicle.", "data": result}
    
async def update_vehicle(vehicle_id: str, req: VehicleRequest, claims: dict)-> Dict[str, Any]:
    userId, roles = _check_permissions(claims)
    if "Admin" in roles:
        result = await svc.update_vehicle(vehicle_id ,req, req.driver_id)
    else:
        result = await svc.update_vehicle(vehicle_id ,req, userId)
    return {"success":True, "message": "Vehicle updated.", "data": result}
    
async def get_vehicle_types() -> Dict[str, Any] :
    result = await svc.get_vehicle_types()
    return {"success":True, "message": "Fetched all vehicle types.", "data": result}

async def post_vehicle_type(req) -> Dict[str, Any]:
    result = await svc.post_vehicle_type(req)
    return {"success":True, "message": "Vehicle type created.", "data": result}

async def delete_vehicle_type(type: str) -> Dict[str, Any]:
    result = await svc.delete_vehicle_type(type)
    return {"success":True, "message": "Vehicle type deleted.", "data": result}

async def get_vehicle_features() -> Dict[str, Any]:
    result = await svc.get_vehicle_features()
    return {"success":True, "message": "Fetched all vehicle features.", "data": result}

async def post_vehicle_feature(req) -> Dict[str, Any]:
    result = await svc.post_vehicle_feature(req)
    return {"success":True, "message": "Vehicle feature created.", "data": result}

async def delete_vehicle_feature(feature: str) -> Dict[str, Any]:
    result = await svc.delete_vehicle_feature(feature)
    return {"success":True, "message": "Vehicle feature deleted.", "data": result}
    
