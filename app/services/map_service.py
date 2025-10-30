import uuid
import polyline
import requests
from ..models.map_model import Coordinate

async def create_route(start: Coordinate, end: Coordinate):
    url = f"http://router.project-osrm.org/route/v1/driving/{start.lgn},{start.lat};{end.lgn},{end.lat}?overview=full&geometries=polyline"
    response = requests.get(url)
    data = response.json()

    if "routes" not in data or not data["routes"]:
        return None

    encoded = data["routes"][0]["geometry"]
    decoded_coords = polyline.decode(encoded)

    distance = data["routes"][0]["distance"]
    duration = data["routes"][0]["duration"]

    route = {
        "id": str(uuid.uuid4()),
        "distance": distance,
        "duration": duration,
        "geometry": [{"lat": lat, "lgn": lgn} for lat, lgn in decoded_coords]
    }
    return route