from fastapi import HTTPException
from ..services import map_service
from ..models.map_model import Coordinate

async def create_route(start: Coordinate, end: Coordinate):
    route = await map_service.create_route(start, end)
    if not route:
        raise HTTPException(status_code=400, detail="Could not create route")
    return route