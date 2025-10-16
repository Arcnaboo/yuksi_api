from fastapi import APIRouter, Body
from ..models.gps_model import GPSUpdateRequest
from ..controllers import gps_controller as ctrl

router = APIRouter(prefix="/api/GPS", tags=["GPS"])

@router.post("/update", summary="Driver creates or updates its GPS location")
async def update_gps(req: GPSUpdateRequest = Body(...)):
    return await ctrl.upsert_location(req)

@router.get("/all", summary="Get all latest GPS positions")
async def get_all_gps():
    return await ctrl.get_all_latest()

@router.get("/get/{driver_id}", summary="Get driver's latest GPS position")
async def get_gps(driver_id: str):
    return await ctrl.get_latest(driver_id)