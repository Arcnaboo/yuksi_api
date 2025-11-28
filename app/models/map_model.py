from pydantic import BaseModel
from typing import Tuple, Optional, List

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

class CourierRouteResponse(BaseModel):
    """SerpAPI Google Maps Directions için kurye rota response modeli"""
    order_id: str
    route_polyline: Optional[str] = None
    distance: float  # metre cinsinden
    duration: float  # saniye cinsinden
    driver: Coordinate
    pickup: Coordinate
    dropoff: Coordinate
    steps: Optional[List[dict]] = None  # Turn-by-turn talimatlar (isteğe bağlı)