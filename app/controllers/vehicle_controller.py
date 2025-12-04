from typing import List
from fastapi import HTTPException, status
import app.services.vehicle_service as svc

def _check_permissions(claims: dict):
    roles = claims.get("role") or claims.get("roles") or []
    if isinstance(roles, str):
        roles = [roles]

    if "Admin" not in roles and "Courier" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to access this restaurant's resources"
        )
    
    return claims.get("userId"), roles

async def get_all_vehicles(size: int, offset: int, types: List[str], features: List[str]):
    return await svc.get_all_vehicles(size=size, offset=offset, types=types, features=features)

async def create_vehicle(req, claims: dict):
    userId, roles = _check_permissions(claims)
    if "Admin" not in roles:
        return await svc.create_vehicle(req, userId)
    else:
        return await svc.create_vehicle(req)
    
async def update_vehicle(req, claims: dict):
    userId, roles = _check_permissions(claims)
    if "Admin" not in roles:
        return await svc.update_vehicle(req, userId)
    else:
        return await svc.update_vehicle(req)
    
async def get_vehicle_types():
    return await svc.get_vehicle_types()

async def post_vehicle_type(req):
    return await svc.post_vehicle_type(req)

async def delete_vehicle_type(type_name: str):
    return await svc.delete_vehicle_type(type_name)

async def get_vehicle_features():
    return await svc.get_vehicle_features()

async def post_vehicle_feature(req):
    return await svc.post_vehicle_feature(req)

async def delete_vehicle_feature(feature: str):
    return await svc.delete_vehicle_feature(feature)
    
