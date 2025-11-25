from typing import List, Optional, Tuple
from uuid import UUID
from app.utils.database_async import fetch_one
import math


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    İki koordinat arasındaki mesafeyi km cinsinden hesaplar (Haversine formülü)
    """
    R = 6371  # Dünya yarıçapı (km)
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )
    
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return round(distance, 2)


async def get_city_price_by_template(
    city_id: int,
    template: str
) -> Optional[dict]:
    """
    Şehir ID'si ve araç tipine göre city_prices tablosundan fiyat bilgisini getirir
    """
    try:
        query = """
            SELECT 
                courier_price,
                minivan_price,
                panelvan_price,
                kamyonet_price,
                kamyon_price
            FROM city_prices
            WHERE city_id = $1
            LIMIT 1;
        """
        
        row = await fetch_one(query, city_id)
        
        if not row:
            return None
        
        # Template'e göre fiyat seç
        price_map = {
            "motorcycle": row.get("courier_price"),
            "minivan": row.get("minivan_price"),
            "panelvan": row.get("panelvan_price"),
            "kamyonet": row.get("kamyonet_price"),
            "kamyon": row.get("kamyon_price")
        }
        
        base_price = price_map.get(template, row.get("courier_price"))
        
        return {
            "base_price": float(base_price) if base_price else 0.0,
            "template": template
        }
        
    except Exception as e:
        return None


async def get_city_id_from_coordinates(
    lat: float,
    lng: float
) -> Optional[int]:
    """
    Koordinatlardan şehir ID'sini bulur (basit yaklaşım - en yakın şehir)
    """
    try:
        # En yakın şehri bul (basit mesafe hesaplaması ile)
        query = """
            SELECT id, lat, lng
            FROM cities
            WHERE lat IS NOT NULL AND lng IS NOT NULL
            ORDER BY (
                6371 * acos(
                    LEAST(1.0,
                        cos(radians($1)) * 
                        cos(radians(lat)) * 
                        cos(radians(lng) - radians($2)) + 
                        sin(radians($1)) * 
                        sin(radians(lat))
                    )
                )
            )
            LIMIT 1;
        """
        
        row = await fetch_one(query, lat, lng)
        
        if row:
            return row.get("id")
        
        return None
        
    except Exception as e:
        return None


async def calculate_job_price(
    vehicle_product_id: Optional[UUID] = None,
    vehicle_template: Optional[str] = None,
    pickup_coords: Optional[List[float]] = None,
    dropoff_coords: Optional[List[float]] = None,
    city_id: Optional[int] = None,
    extra_services_total: float = 0.0,
    base_price: Optional[float] = None
) -> Tuple[Optional[float], Optional[str]]:
    """
    Yük fiyatını hesaplar
    
    Args:
        vehicle_product_id: Araç ürün ID'si (yeni sistem)
        vehicle_template: Araç tipi (motorcycle, minivan, etc.)
        pickup_coords: Alış koordinatları [lat, lng]
        dropoff_coords: Teslimat koordinatları [lat, lng]
        city_id: Şehir ID'si (opsiyonel, koordinatlardan bulunabilir)
        extra_services_total: Ek hizmetler toplamı
        base_price: Direkt base fiyat (opsiyonel)
    
    Returns:
        (fiyat, hata_mesajı)
    """
    try:
        # 1. Template belirleme
        template = vehicle_template
        
        if vehicle_product_id and not template:
            # Vehicle product'tan template çek
            from app.services.vehicle_product_service import get_vehicle_product
            product, error = await get_vehicle_product(vehicle_product_id)
            if error or not product:
                return None, f"Araç ürünü bulunamadı: {error}"
            template = product.get("productTemplate")
        
        if not template:
            template = "motorcycle"  # Default
        
        # 2. Base price belirleme
        if base_price is None:
            # City prices'tan fiyat çek
            if not city_id and pickup_coords:
                # Koordinatlardan şehir bul
                city_id = await get_city_id_from_coordinates(
                    pickup_coords[0],
                    pickup_coords[1]
                )
            
            if city_id:
                city_price = await get_city_price_by_template(city_id, template)
                if city_price:
                    base_price = city_price["base_price"]
                else:
                    # Varsayılan fiyatlar (city_prices bulunamazsa)
                    default_prices = {
                        "motorcycle": 50.0,
                        "minivan": 150.0,
                        "panelvan": 200.0,
                        "kamyonet": 300.0,
                        "kamyon": 500.0
                    }
                    base_price = default_prices.get(template, 50.0)
            else:
                # Şehir bulunamazsa varsayılan fiyat
                default_prices = {
                    "motorcycle": 50.0,
                    "minivan": 150.0,
                    "panelvan": 200.0,
                    "kamyonet": 300.0,
                    "kamyon": 500.0
                }
                base_price = default_prices.get(template, 50.0)
        
        # 3. Mesafe hesaplama (eğer koordinatlar varsa)
        distance_km = 0.0
        km_price = 0.0
        
        if pickup_coords and dropoff_coords and len(pickup_coords) >= 2 and len(dropoff_coords) >= 2:
            distance_km = calculate_distance_km(
                pickup_coords[0],
                pickup_coords[1],
                dropoff_coords[0],
                dropoff_coords[1]
            )
            
            # KM başına fiyat (basit hesaplama - carrier_types tablosundan da çekilebilir)
            # Şimdilik template'e göre sabit değerler
            km_price_map = {
                "motorcycle": 2.0,
                "minivan": 5.0,
                "panelvan": 6.0,
                "kamyonet": 8.0,
                "kamyon": 10.0
            }
            km_price = km_price_map.get(template, 2.0)
        
        # 4. Toplam fiyat hesaplama
        total = base_price + (distance_km * km_price) + extra_services_total
        
        return round(total, 2), None
        
    except Exception as e:
        return None, str(e)

