from fastapi import APIRouter, Depends
from ..controllers import map_controller, auth_controller
from ..models.map_model import RouteRequest, RouteResponse

router = APIRouter(prefix="/map", tags=["Map"])

@router.post("/route", response_model=RouteResponse)
async def get_route(req: RouteRequest, driver=Depends(auth_controller.get_current_driver)):
    return await map_controller.create_route(req.start, req.end)