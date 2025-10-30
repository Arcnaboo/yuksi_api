from fastapi import APIRouter, Depends
from ..controllers import map_controller, auth_controller
from ..models.map_model import RouteRequest, RouteResponse

router = APIRouter(prefix="/map", tags=["Map"])

@router.post("/route", response_model=RouteResponse)
async def create_route(req: RouteRequest):
    return await map_controller.create_route(req.start, req.end)