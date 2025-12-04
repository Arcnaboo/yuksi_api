from typing import List
from uuid import UUID
from fastapi import APIRouter, Body, Depends
from fastapi.params import Param, Query
import app.controllers.vehicle_controller as ctrl
from app.controllers.auth_controller import require_roles
from app.models.vehicles_models import VehicleRequest, VehicleResponse, VehicleTypeRequest, VehicleFeatureRequest, VehicleFeatureResponse, VehicleTypeResponse

router = APIRouter(prefix="/Vehicle", tags=["Vehicle"])

@router.get(
    "/",
    summary="Tüm araçları getirir",
    description="Tüm araçları özellikleri ile listeler.",
    dependencies= Depends(require_roles(["Admin"])),
    response_model=List[VehicleResponse]
)
async def get_all_vehicles(size: int = Query(50, le=0, lt=100), offset: int = Query(0), types: list[str] = Query(None), features: list[str] = Query(None)):
    return await ctrl.get_all_vehicles(size, offset, types, features)

@router.get(
    "/{vehicle_id}",
    summary="Belirli aracı getirir",
    description="Tüm araçları özellikleri ile listeler.",
    dependencies= Depends(require_roles(["Admin", "Courier"])),
    response_model=VehicleResponse
)
async def get_vehicle(vehicle_id: str, _claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.get_vehicles(UUID(vehicle_id), _claims)

@router.post(
    "/",
    summary="Yeni araç oluşturur",
    description="Yeni bir aracı özellikleri ile oluşturur.",
    dependencies= Depends(require_roles(["Admin", "Courier"])),
    response_model=VehicleResponse
)
async def create_vehicle(req: VehicleRequest, _claims: dict = Depends(require_roles(["Admin", "Courier"])), ):
    return await ctrl.create_vehicle(req, _claims)

@router.put(
    "/{vehicle_id}",
    summary="Mevcut aracı düzenler",
    description="Mevcut aracın özelliklerini düzenler",
    dependencies= Depends(require_roles(["Admin", "Courier"])),
    response_model=VehicleResponse
)
async def create_vehicle(vehicle_id: str ,req: VehicleRequest, _claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.update_vehicle(req, _claims)

# Types

@router.get(
    "/type",
    summary="Tüm araç tiplerini getirir.",
    description="Veri tabanındaki araç tiplerini getirir.",
    dependencies= Depends(require_roles(["Admin"])),
    response_model=List[VehicleTypeResponse]
)
async def get_vehicle_types():
    return await ctrl.get_vehicle_types()

@router.post(
    "/type",
    summary="Yeni araç tipi ekler.",
    description="Veri tabanına araç tipi ekler.",
    dependencies= Depends(require_roles(["Admin"])),
    response_model=VehicleTypeResponse
)
async def get_vehicle_types(req: VehicleTypeRequest):
    return await ctrl.post_vehicle_type(req)

@router.delete(
    "/type/{name}",
    summary="Araç tipini siler.",
    description="Veri tabanındaki araç tipini siler."
)
async def get_vehicle_types(type: str):
    return await ctrl.delete_vehicle_type(type)

# Features

@router.get(
    "/feature",
    summary="Tüm araç özelliklerini getirir.",
    description="Veri tabanındaki araç özelliklerini getirir.",
    response_model=List[VehicleFeatureResponse]
)
async def get_vehicle_features():
    return await ctrl.get_vehicle_features()

@router.post(
    "/feature",
    summary="Yeni araç özelliği oluşturur.",
    description="Veri tabanına araç özelliği ekler.",
    dependencies= Depends(require_roles(["Admin"])),
    response_model=VehicleFeatureResponse
)
async def get_vehicle_features(req: VehicleFeatureRequest):
    return await ctrl.post_vehicle_feature()

@router.delete(
    "/feature",
    summary="Araç özelliğini siler.",
    description="Veri tabanındaki araç özelliğini siler.",
    dependencies= Depends(require_roles(["Admin"]))
)
async def get_vehicle_features(feature: str):
    return await ctrl.delete_vehicle_feature(feature)