from fastapi import HTTPException
from ..services import map_service

async def create_route(start: tuple[float, float], end: tuple[float, float]):
    route = await map_service.create_route(start, end)
    if not route:
        raise HTTPException(status_code=400, detail="Could not create route")
    return route