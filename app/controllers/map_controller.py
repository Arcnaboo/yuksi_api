from fastapi import HTTPException
from ..services import map_service
from ..models.map_model import Coordinate

async def create_route(driver, order_id: str):
    route = await map_service.create_route("353537b0-40df-4923-b16c-1532b8baa8d1", order_id)
    if not route:
        raise HTTPException(status_code=400, detail="Could not create route")
    return route