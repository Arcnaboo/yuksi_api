import uuid
import requests

from app.utils.database_async import fetch_one
from app.services.gps_service import get_latest
from ..models.map_model import Coordinate

async def create_route(driver_id: str, order_id: str):
    try:
        uuid.UUID(order_id)
        uuid.UUID(driver_id)
    except ValueError:
        return None
    query = """
        SELECT pickup_lat, pickup_lng, dropoff_lat, dropoff_lng
        FROM orders
        WHERE id = $1
    """
    row = await fetch_one(query, order_id)
    if not row:
        return None
    pickup = Coordinate(lgn=row["pickup_lng"], lat=row["pickup_lat"])
    dropoff = Coordinate(lgn=row["dropoff_lng"], lat=row["dropoff_lat"])

    driver_location, err = await get_latest(driver_id)
    if err or not driver_location:
        return None
    driver_coords = Coordinate(lat=driver_location["latitude"], lgn=driver_location["longitude"])

    url = f"http://router.project-osrm.org/route/v1/driving/{driver_coords.lat},{driver_coords.lgn};{pickup.lat},{pickup.lgn};{dropoff.lat},{dropoff.lgn}?overview=full&geometries=polyline"
    
    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    data = response.json()
    encoded = data["routes"][0]["geometry"]

    route = {
        "order_id": order_id,
        "route_polyline": encoded,
        "distance": data["routes"][0]["distance"],
        "duration": data["routes"][0]["duration"],
        "driver": driver_coords,
        "pickup": pickup,
        "dropoff": dropoff
    }

    return route