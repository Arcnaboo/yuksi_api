from pydantic import BaseModel
from typing import Tuple

class Coordinate(BaseModel):
    lgn: float
    lat: float

class RouteRequest(BaseModel):
    start: Coordinate # (lon, lat)
    end: Coordinate   # (lon, lat)

class RouteResponse(BaseModel):
    id: str
    distance: float  # in meters
    duration: float  # in seconds
    geometry: list[Coordinate]  # list of (lat, lon) coordinates