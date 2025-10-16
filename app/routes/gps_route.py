from fastapi import APIRouter, Body
from ..models.gps_model import GPSUpdateRequest
from ..controllers import gps_controller as ctrl

router = APIRouter(prefix="/api/gps", tags=["GPS"])

@router.post("/update", summary="Driver creates or updates its GPS location")
async def update_gps(req: GPSUpdateRequest = Body(...)):
    return await ctrl.upsert_location(req)

@router.get("/all", summary="Get all latest GPS positions")
async def get_all_gps():
    return await ctrl.get_all_latest()
