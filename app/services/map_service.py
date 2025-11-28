import uuid
import requests

from fastapi import HTTPException
from app.utils.database_async import fetch_one
from app.services.gps_service import get_latest
from app.utils.config import get_serpapi_key
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

async def create_courier_route_serpapi(driver_id: str, order_id: str):
    """
    SerpAPI kullanarak Google Maps Directions ile kurye için rota oluşturur.
    
    Args:
        driver_id: Kurye/driver ID
        order_id: Sipariş ID
    
    Returns:
        dict: Rota bilgileri (order_id, route_polyline, distance, duration, driver, pickup, dropoff, steps)
    
    Raises:
        HTTPException: Order bulunamazsa, driver konumu bulunamazsa veya SerpAPI hatası olursa
    """
    try:
        uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    
    # Order bilgilerini al
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
    
    # Kurye konumunu al
    driver_location, err = await get_latest(str(driver_id))
    if err or not driver_location:
        raise HTTPException(status_code=404, detail=f"Driver location not found: {err}")
    driver_coords = Coordinate(lat=driver_location["latitude"], lgn=driver_location["longitude"])
    
    # SerpAPI key'i al
    serpapi_key = get_serpapi_key()
    
    # SerpAPI Google Maps Directions çağrısı
    # İki ayrı rota hesaplayıp birleştiriyoruz (waypoints desteklenmiyor olabilir)
    # 1. Driver -> Pickup
    # 2. Pickup -> Dropoff
    
    try:
        total_distance = 0
        total_duration = 0
        all_steps = []
        route_polylines = []
        
        # 1. Driver -> Pickup rotası
        # SerpAPI Google Maps Directions için start_coords ve end_coords kullanılmalı
        params_leg1 = {
            "engine": "google_maps_directions",
            "api_key": serpapi_key,
            "start_coords": f"{driver_coords.lat},{driver_coords.lgn}",
            "end_coords": f"{pickup.lat},{pickup.lgn}",
        }
        
        response1 = requests.get("https://serpapi.com/search", params=params_leg1, timeout=10)
        
        # Detaylı hata kontrolü
        if response1.status_code != 200:
            try:
                error_data = response1.json()
                error_msg = error_data.get("error", response1.text[:500])
            except:
                error_msg = response1.text[:500]
            raise HTTPException(
                status_code=500, 
                detail=f"SerpAPI request failed (leg1): Status {response1.status_code}, Error: {error_msg}"
            )
        
        data1 = response1.json()
        
        # SerpAPI error kontrolü
        if "error" in data1:
            error_msg = data1.get("error", "Unknown error")
            raise HTTPException(
                status_code=500, 
                detail=f"SerpAPI error (leg1): {error_msg}"
            )
        
        # 2. Pickup -> Dropoff rotası
        params_leg2 = {
            "engine": "google_maps_directions",
            "api_key": serpapi_key,
            "start_coords": f"{pickup.lat},{pickup.lgn}",
            "end_coords": f"{dropoff.lat},{dropoff.lgn}",
        }
        
        response2 = requests.get("https://serpapi.com/search", params=params_leg2, timeout=10)
        
        # Detaylı hata kontrolü
        if response2.status_code != 200:
            try:
                error_data = response2.json()
                error_msg = error_data.get("error", response2.text[:500])
            except:
                error_msg = response2.text[:500]
            raise HTTPException(
                status_code=500, 
                detail=f"SerpAPI request failed (leg2): Status {response2.status_code}, Error: {error_msg}"
            )
        
        data2 = response2.json()
        
        # SerpAPI error kontrolü
        if "error" in data2:
            error_msg = data2.get("error", "Unknown error")
            raise HTTPException(
                status_code=500, 
                detail=f"SerpAPI error (leg2): {error_msg}"
            )
        
        # Her iki rotayı parse et
        def parse_route(data):
            """SerpAPI response'unu parse eder - SerpAPI'nin gerçek response yapısını kullanır"""
            distance = 0
            duration = 0
            steps = []
            polyline = None
            
            # SerpAPI Google Maps Directions response yapısı:
            # { "directions": [...], "durations": [...], "places_info": {...} }
            
            # Format 1: directions key'i ile (SerpAPI'nin standart formatı)
            if "directions" in data and data["directions"]:
                directions = data["directions"]
                
                # Directions bir liste olabilir
                if isinstance(directions, list) and len(directions) > 0:
                    # Her direction objesi için
                    for direction in directions:
                        # Direction içinde routes olabilir
                        if "routes" in direction:
                            routes = direction["routes"]
                            if isinstance(routes, list) and len(routes) > 0:
                                route_data = routes[0]
                            else:
                                route_data = routes
                            
                            # Legs'leri işle
                            if "legs" in route_data:
                                for leg in route_data["legs"]:
                                    if "distance" in leg:
                                        dist_obj = leg["distance"]
                                        if isinstance(dist_obj, dict) and "value" in dist_obj:
                                            distance += dist_obj["value"]
                                        elif isinstance(dist_obj, (int, float)):
                                            distance += dist_obj
                                    
                                    if "duration" in leg:
                                        dur_obj = leg["duration"]
                                        if isinstance(dur_obj, dict) and "value" in dur_obj:
                                            duration += dur_obj["value"]
                                        elif isinstance(dur_obj, (int, float)):
                                            duration += dur_obj
                                    
                                    if "steps" in leg:
                                        for step in leg["steps"]:
                                            step_info = {
                                                "instruction": step.get("html_instructions", step.get("instruction", step.get("text", ""))),
                                                "distance": step.get("distance", {}).get("value", 0) if isinstance(step.get("distance"), dict) else step.get("distance", 0),
                                                "duration": step.get("duration", {}).get("value", 0) if isinstance(step.get("duration"), dict) else step.get("duration", 0),
                                            }
                                            steps.append(step_info)
                            
                            # Polyline'ı al
                            if "overview_polyline" in route_data:
                                polyline_obj = route_data["overview_polyline"]
                                if isinstance(polyline_obj, dict):
                                    polyline = polyline_obj.get("points", "")
                                else:
                                    polyline = str(polyline_obj)
                            
                            # Alternatif: polyline direkt route_data'da olabilir
                            if not polyline and "polyline" in route_data:
                                polyline = route_data["polyline"]
                        else:
                            # Direction direkt distance ve duration içeriyor (SerpAPI'nin gerçek formatı)
                            # { "distance": 289, "duration": 267, "trips": [...] }
                            if "distance" in direction:
                                dist_val = direction["distance"]
                                if isinstance(dist_val, (int, float)):
                                    distance += dist_val
                                elif isinstance(dist_val, dict) and "value" in dist_val:
                                    distance += dist_val["value"]
                            
                            if "duration" in direction:
                                dur_val = direction["duration"]
                                if isinstance(dur_val, (int, float)):
                                    duration += dur_val
                                elif isinstance(dur_val, dict) and "value" in dur_val:
                                    duration += dur_val["value"]
                            
                            # Steps için trips içine bak
                            if "trips" in direction and isinstance(direction["trips"], list):
                                for trip in direction["trips"]:
                                    if "steps" in trip:
                                        for step in trip["steps"]:
                                            step_info = {
                                                "instruction": step.get("html_instructions", step.get("instruction", step.get("text", ""))),
                                                "distance": step.get("distance", 0) if isinstance(step.get("distance"), (int, float)) else step.get("distance", {}).get("value", 0),
                                                "duration": step.get("duration", 0) if isinstance(step.get("duration"), (int, float)) else step.get("duration", {}).get("value", 0),
                                            }
                                            steps.append(step_info)
                                    
                                    # Polyline trips içinde olabilir
                                    if "polyline" in trip:
                                        polyline = trip["polyline"] if isinstance(trip["polyline"], str) else trip["polyline"].get("points", "")
                                    elif "overview_polyline" in trip:
                                        poly_obj = trip["overview_polyline"]
                                        polyline = poly_obj if isinstance(poly_obj, str) else poly_obj.get("points", "")
                            
                            # Alternatif: direction içinde direkt polyline
                            if not polyline and "polyline" in direction:
                                polyline = direction["polyline"] if isinstance(direction["polyline"], str) else direction["polyline"].get("points", "")
                            elif not polyline and "overview_polyline" in direction:
                                poly_obj = direction["overview_polyline"]
                                polyline = poly_obj if isinstance(poly_obj, str) else poly_obj.get("points", "")
            
            # Format 2: durations key'i ile (SerpAPI'de de var)
            if duration == 0 and "durations" in data:
                durations = data["durations"]
                if isinstance(durations, list) and len(durations) > 0:
                    # İlk duration'ı al (toplam süre)
                    dur_obj = durations[0]
                    if isinstance(dur_obj, dict):
                        duration = dur_obj.get("value", 0)
                    elif isinstance(dur_obj, (int, float)):
                        duration = dur_obj
            
            # Format 3: places_info içinde distance/duration olabilir
            if (distance == 0 or duration == 0) and "places_info" in data:
                places_info = data["places_info"]
                # places_info genellikle mesafe bilgisi içerir ama yapısı değişken
            
            # Eğer hiçbir format çalışmazsa None döndür
            if distance == 0 and duration == 0:
                return None, None, None, None
            
            return distance, duration, steps, polyline
        
        # Leg 1: Driver -> Pickup
        dist1, dur1, steps1, poly1 = parse_route(data1)
        if dist1 is None:
            raise HTTPException(
                status_code=500, 
                detail="No directions found in SerpAPI response (leg1)"
            )
        
        total_distance += dist1
        total_duration += dur1
        all_steps.extend(steps1)
        if poly1:
            route_polylines.append(poly1)
        
        # Leg 2: Pickup -> Dropoff
        dist2, dur2, steps2, poly2 = parse_route(data2)
        if dist2 is None:
            raise HTTPException(status_code=500, detail="No directions found in SerpAPI response (leg2)")
        
        total_distance += dist2
        total_duration += dur2
        all_steps.extend(steps2)
        if poly2:
            route_polylines.append(poly2)
        
        # Polylines'ı birleştir (basit yaklaşım: ilk polyline'ı kullan veya birleştir)
        # Not: Polyline birleştirme için özel kütüphane gerekebilir, şimdilik ilkini kullanıyoruz
        route_polyline = route_polylines[0] if route_polylines else ""
        
        # Response oluştur
        route_response = {
            "order_id": order_id,
            "route_polyline": route_polyline,
            "distance": total_distance,
            "duration": total_duration,
            "driver": driver_coords,
            "pickup": pickup,
            "dropoff": dropoff,
            "steps": all_steps if all_steps else None
        }
        
        return route_response
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, 
            detail=f"SerpAPI request failed: {str(e)}"
        )
    except (KeyError, IndexError, TypeError) as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error parsing SerpAPI response: {str(e)}"
        )