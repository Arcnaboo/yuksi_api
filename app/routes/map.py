from fastapi import APIRouter, Depends
from ..controllers import map_controller, auth_controller
from ..models.map_model import RouteResponse

router = APIRouter(prefix="/map", tags=["Map"])

# Todo: Authenticate driver before creating route
@router.get("/route/{order_id}", response_model=RouteResponse)
async def create_route(order_id: str):
    return await map_controller.create_route("test", order_id)