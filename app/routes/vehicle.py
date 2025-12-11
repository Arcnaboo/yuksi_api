from fastapi import APIRouter, Depends
from fastapi.params import Query
import app.controllers.vehicle_controller as ctrl
from app.controllers.auth_controller import require_roles
from app.models.vehicles_models import VehicleRequest, VehicleTypeRequest, VehicleFeatureRequest

router = APIRouter(prefix="/api/Vehicle", tags=["Vehicle"])

@router.get(
    "",
    summary="Tüm araçları getirir",
    description="Tüm araçları özellikleri ile listeler.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def get_all_vehicles(size: int = Query(50), offset: int = Query(0), vehicle_type: str = Query(None), vehicle_features: list[str] = Query(None)):
    return await ctrl.get_all_vehicles(size, offset)

@router.get(
    "/get/{vehicle_id}",
    summary="Belirli aracı getirir",
    description="Tüm araçları özellikleri ile listeler.",
    dependencies= [Depends(require_roles(["Admin", "Courier"]))]
)
async def get_vehicle(vehicle_id: str, _claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.get_vehicle(vehicle_id, _claims)

@router.post(
    "",
    summary="Yeni araç oluşturur",
    description="Yeni bir aracı özellikleri ile oluşturur.",
    dependencies= [Depends(require_roles(["Admin", "Courier"]))]
)
async def create_vehicle(req: VehicleRequest, _claims: dict = Depends(require_roles(["Admin", "Courier"])), ):
    return await ctrl.create_vehicle(req, _claims)

@router.put(
    "/update/{vehicle_id}",
    summary="Mevcut aracı düzenler",
    description="Mevcut aracın özelliklerini düzenler",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def update_vehicle(vehicle_id: str ,req: VehicleRequest, _claims: dict = Depends(require_roles(["Admin", "Courier"]))):
    return await ctrl.update_vehicle(vehicle_id , req, _claims)

# Types

@router.get(
    "/Type",
    summary="Tüm araç tiplerini getirir.",
    description="Veri tabanındaki araç tiplerini getirir.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def get_vehicle_types():
    return await ctrl.get_vehicle_types()

@router.post(
    "/Type",
    summary="Yeni araç tipi ekler.",
    description="Veri tabanına araç tipi ekler.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def create_vehicle_type(req: VehicleTypeRequest):
    return await ctrl.post_vehicle_type(req)

@router.delete(
    "/Type/{name}",
    summary="Araç tipini siler.",
    description="Veri tabanındaki araç tipini siler.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def delete_vehicle_type(type: str):
    return await ctrl.delete_vehicle_type(type)

# Features

@router.get(
    "/Feature",
    summary="Tüm araç özelliklerini getirir.",
    description="Veri tabanındaki araç özelliklerini getirir.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def get_vehicle_features():
    return await ctrl.get_vehicle_features()

@router.post(
    "/Feature",
    summary="Yeni araç özelliği oluşturur.",
    description="Veri tabanına araç özelliği ekler.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def create_vehicle_feature(req: VehicleFeatureRequest):
    return await ctrl.post_vehicle_feature(req)

@router.delete(
    "/Feature",
    summary="Araç özelliğini siler.",
    description="Veri tabanındaki araç özelliğini siler.",
    dependencies= [Depends(require_roles(["Admin"]))]
)
async def delete_vehicle_feature(feature: str):
    return await ctrl.delete_vehicle_feature(feature)