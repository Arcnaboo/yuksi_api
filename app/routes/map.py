from fastapi import APIRouter, Depends
from ..controllers import map_controller, auth_controller
from ..models.map_model import RouteResponse, CourierRouteResponse

router = APIRouter(prefix="/map", tags=["Map"])

@router.get("/route/{order_id}", response_model=RouteResponse)
async def create_route(order_id: str, driver=Depends(auth_controller.get_current_driver)):
    return await map_controller.create_route(driver, order_id)

@router.get("/route/courier/{order_id}", response_model=CourierRouteResponse)
async def create_courier_route_serpapi(
    order_id: str, 
    driver=Depends(auth_controller.get_current_driver)
):
    """
    SerpAPI kullanarak Google Maps Directions ile kurye için anlık rota oluşturur.
    
    - Kurye konumu GPS servisinden alınır
    - Order'dan pickup ve dropoff noktaları alınır
    - SerpAPI ile Google Maps'ten rota hesaplanır
    """
    return await map_controller.create_courier_route_serpapi(driver, order_id)