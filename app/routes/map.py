from fastapi import APIRouter, Depends
from ..controllers import map_controller, auth_controller
from ..models.map_model import RouteResponse

router = APIRouter(prefix="/map", tags=["Map"])

@router.get("/route/{order_id}", response_model=RouteResponse)
async def create_route(order_id: str, driver=Depends(auth_controller.get_current_driver)):
    return await map_controller.create_route(driver, order_id)