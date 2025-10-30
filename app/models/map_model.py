from pydantic import BaseModel
from typing import Tuple

class Coordinate(BaseModel):
    lgn: float
    lat: float

class RouteRequest(BaseModel):
    start: Coordinate # (lon, lat)
    end: Coordinate   # (lon, lat)

class RouteResponse(BaseModel):
    order_id: str
    route_polyline: str
    distance: float
    duration: float
    driver: Coordinate
    pickup: Coordinate
    dropoff: Coordinate