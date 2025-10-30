import uuid
import requests

from fastapi import HTTPException
from app.utils.database_async import fetch_one
from app.services.gps_service import get_latest
from ..models.map_model import Coordinate

async def create_route(driver_id: str, order_id: str):
    try:
        uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    query = """
        SELECT pickup_lat, pickup_lng, dropoff_lat, dropoff_lng
        FROM orders
        WHERE id = $1
    """
    row = await fetch_one(query, order_id)
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    pickup = Coordinate(lgn=row["pickup_lng"], lat=row["pickup_lat"])
    dropoff = Coordinate(lgn=row["dropoff_lng"], lat=row["dropoff_lat"])
    
    driver_location, err = await get_latest(str(driver_id))
    if err or not driver_location:
        raise HTTPException(status_code=404, detail=f"Driver location not found: {err}")
    driver_coords = Coordinate(lat=driver_location["latitude"], lgn=driver_location["longitude"])
    
    # added fix for lat/lgn order
    url = f"http://router.project-osrm.org/route/v1/driving/{driver_coords.lgn},{driver_coords.lat};{pickup.lgn},{pickup.lat};{dropoff.lgn},{dropoff.lat}?overview=full&geometries=polyline"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching route from OSRM")
    
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