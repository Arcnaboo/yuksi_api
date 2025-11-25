from typing import Optional, List, Dict, Any, Tuple
import random
import string
from datetime import datetime
import uuid
from app.utils.database import db_cursor
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services.order_watch_service import tick_watch, add_rejection, delete, create_watch, update_available_drivers, close


# === Kod Üretimi ===
async def generate_order_code() -> str:
    """ORD-YYMMDD formatında random kod üret"""
    today = datetime.now()
    date_part = today.strftime("%y%m%d")
    random_part = ''.join(random.choices(string.digits, k=3))
    return f"ORD-{date_part}{random_part}"


# === Sipariş Oluştur ===
async def create_order(
    restaurant_id: str,
    customer: str,
    phone: str,
    address: str,
    delivery_address: str,
    pickup_lat: float,
    pickup_lng: float,
    dropoff_lat: float,
    dropoff_lng: float,
    order_type: str,
    amount: float,
    carrier_type: str = "kurye",
    vehicle_type: str = "2_teker_motosiklet",
    cargo_type: Optional[str] = None,
    special_requests: Optional[str] = None,
    items: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Sipariş oluştur"""
    try:
        uuid.UUID(restaurant_id)
    except:
        return "Invalid UUID"  
    try:
        rest = await fetch_one("SELECT id FROM restaurants WHERE id=$1;", restaurant_id)
        if not rest:
            return None, "Restaurant not found"

        code = await generate_order_code()
        row = await fetch_one(
            """
            INSERT INTO orders (
                restaurant_id, code, customer, phone, address, delivery_address,
                pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
                type, amount, carrier_type, vehicle_type, cargo_type, special_requests
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
            RETURNING id, created_at;
            """,
            restaurant_id, code, customer, phone, address, delivery_address,
            pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
            order_type, amount, carrier_type, vehicle_type, cargo_type, special_requests
        )

        order_id = row["id"]
        created_at = row["created_at"]

        if items:
            for item in items:
                total = item["price"] * item["quantity"]
                await execute(
                    """
                    INSERT INTO order_items (order_id, product_name, price, quantity, total)
                    VALUES ($1,$2,$3,$4,$5);
                    """,
                    order_id, item["product_name"], item["price"], item["quantity"], total
                )

        # Order izleyiciyi başlat
        await create_watch(uuid.UUID(str(order_id)))

        return {"id": str(order_id), "code": code, "created_at": created_at}, None

    except Exception as e:
        return None, str(e)


# === Sipariş Detayı ===
async def get_order(order_id: str, restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Sipariş detayını getir"""
    with db_cursor(dict_cursor=True) as cur:
        # Sipariş bilgileri
        cur.execute("""
            SELECT o.*, r.name as restaurant_name
            FROM orders o
            LEFT JOIN restaurants r ON r.id = o.restaurant_id
            WHERE o.id = %s AND o.restaurant_id = %s
        """, (order_id, restaurant_id))
        
        order = cur.fetchone()
        if not order:
            return None
        
        # Ürünleri getir
        cur.execute("""
            SELECT id, product_name, price, quantity, total
            FROM order_items
            WHERE order_id = %s
            ORDER BY created_at
        """, (order_id,))
        
        items = cur.fetchall()
        order['items'] = items or []
        
        return order

async def update_order(
    order_id: str,
    restaurant_id: str,
    **kwargs
) -> Tuple[bool, Optional[str]]:
    """Sipariş güncelle"""
    try:
        uuid.UUID(order_id)
        uuid.UUID(restaurant_id)
    except:
        return "Invalid UUID"    
    query = """
        SELECT o.*, r.name AS restaurant_name
        FROM orders o
        LEFT JOIN restaurants r ON r.id = o.restaurant_id
        WHERE o.id=$1 AND o.restaurant_id=$2;
    """
    order = await fetch_one(query, order_id, restaurant_id)
    if not order:
        return None

    rows = await fetch_all(
        """
        SELECT id, product_name, price, quantity, total
        FROM order_items
        WHERE order_id=$1
        ORDER BY created_at;
        """,
        order_id
    )
    order = dict(order)
    order["items"] = [dict(r) for r in rows] if rows else []
    return order


# === Sipariş Güncelle ===
async def update_order(order_id: str, restaurant_id: str, **kwargs) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(order_id)
        uuid.UUID(restaurant_id)
    except:
        return False, "Invalid UUID"  
    try:
        exists = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND restaurant_id=$2;",
            order_id, restaurant_id
        )
        if not exists:
            return False, "Order not found"

        update_fields = []
        values = []
        i = 1
        for field, value in kwargs.items():
            if value is not None and field != "items":
                update_fields.append(f"{field} = ${i}")
                values.append(value)
                i += 1

        if update_fields:
            values.extend([order_id])
            query = f"""
                UPDATE orders
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = ${i};
            """
            await execute(query, *values)

        # Ürünler güncelleniyorsa
        if "items" in kwargs and kwargs["items"]:
            await execute("DELETE FROM order_items WHERE order_id=$1;", order_id)
            for item in kwargs["items"]:
                total = item["price"] * item["quantity"]
                await execute(
                    """
                    INSERT INTO order_items (order_id, product_name, price, quantity, total)
                    VALUES ($1,$2,$3,$4,$5);
                    """,
                    order_id, item["product_name"], item["price"], item["quantity"], total
                )

        return True, None

    except Exception as e:
        return False, str(e)


# === Sipariş Sil ===
async def delete_order(order_id: str, restaurant_id: str) -> Tuple[bool, Optional[str]]:
    """Sipariş sil"""
    try:
        uuid.UUID(order_id)
        uuid.UUID(restaurant_id)
    except:
        return False, "Invalid UUID"  
    try:
        result = await execute(
            "DELETE FROM orders WHERE id=$1 AND restaurant_id=$2;",
            order_id, restaurant_id
        )
        if result.endswith(" 0"):
            return False, "Order not found"
        
        # Sipariş izleyicisini sil
        await delete(uuid.UUID(order_id))

        return True, None
    except Exception as e:
        return False, str(e)


# === Sipariş Listesi ===
async def list_orders(
    restaurant_id: str,
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int, float]:
    """Sipariş listesi"""
    with db_cursor(dict_cursor=True) as cur:
        # WHERE koşulları
        where_conditions = ["o.restaurant_id = %s"]
        params = [restaurant_id]
        
        if status:
            where_conditions.append("o.status = %s")
            params.append(status)
        
        if order_type:
            where_conditions.append("o.type = %s")
            params.append(order_type)
        
        if search:
            where_conditions.append("(o.code ILIKE %s OR o.customer ILIKE %s OR o.phone ILIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if start_date:
            where_conditions.append("o.created_at >= %s")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("o.created_at <= %s")
            params.append(end_date)
        
        where_clause = " AND ".join(where_conditions)
        
        # Siparişleri getir
        cur.execute(f"""
            SELECT o.id, o.code, o.customer, o.phone, o.address, o.delivery_address, 
                   o.pickup_lat, o.pickup_lng, o.dropoff_lat, o.dropoff_lng,
                   o.type, o.amount, o.status, o.created_at
            FROM orders o
            WHERE {where_clause}
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        orders = cur.fetchall()
        
        # Toplam sayı
        cur.execute(f"""
            SELECT COUNT(*) as total_count, COALESCE(SUM(amount), 0) as total_amount
            FROM orders o
            WHERE {where_clause}
        """, params)
        
        stats = cur.fetchone()
        total_count = stats['total_count']
        total_amount = float(stats['total_amount'])
        
        return orders, total_count, total_amount

async def get_order_history(
    restaurant_id: str,
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int, float]:
    try:
        uuid.UUID(restaurant_id)
    except:
        return [], 0, 0  
    where = ["o.restaurant_id = $1"]
    params = [restaurant_id]
    idx = 2

    if status:
        where.append(f"o.status = ${idx}")
        params.append(status)
        idx += 1
    if order_type:
        where.append(f"o.type = ${idx}")
        params.append(order_type)
        idx += 1
    if search:
        where.append(f"(o.code ILIKE ${idx} OR o.customer ILIKE ${idx+1} OR o.phone ILIKE ${idx+2})")
        s = f"%{search}%"
        params.extend([s, s, s])
        idx += 3
    if start_date:
        where.append(f"o.created_at >= ${idx}")
        params.append(start_date)
        idx += 1
    if end_date:
        where.append(f"o.created_at <= ${idx}")
        params.append(end_date)
        idx += 1

    where_clause = " AND ".join(where)

    query_orders = f"""
        SELECT o.id, o.code, o.customer, o.phone, o.address, o.delivery_address,
               o.pickup_lat, o.pickup_lng, o.dropoff_lat, o.dropoff_lng,
               o.type, o.amount, o.status, o.created_at
        FROM orders o
        WHERE {where_clause}
        ORDER BY o.created_at DESC
        LIMIT ${idx} OFFSET ${idx+1};
    """
    orders = await fetch_all(query_orders, *params, limit, offset)
    orders = [dict(o) for o in orders] if orders else []

    query_stats = f"""
        SELECT COUNT(*) AS total_count, COALESCE(SUM(amount), 0) AS total_amount
        FROM orders o
        WHERE {where_clause};
    """
    stats = await fetch_one(query_stats, *params)
    total_count = stats["total_count"] if stats else 0
    total_amount = float(stats["total_amount"]) if stats else 0.0

    return orders, total_count, total_amount


# === Sipariş Geçmişi ===
async def get_order_history(
    restaurant_id: str,
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int, float]:
    """Sipariş geçmişi (list_orders ile aynı)"""
    try:
        uuid.UUID(restaurant_id)
    except:
        return [], 0, 0
    return await list_orders(restaurant_id, status, order_type, search, start_date, end_date, limit, offset)
    """Sipariş geçmişi (list_orders ile aynı ama farklı response formatı)"""
    return await list_orders(restaurant_id, status, order_type, search, start_date, end_date, limit, offset)



    # order_service.py'nin sonuna ekle

async def get_courier_assigned_orders(
    courier_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Kuryeye atanan siparişleri getir"""
    try:
        from ..utils.database_async import fetch_all
        
        rows = await fetch_all("""
            SELECT 
                o.id as order_id,
                o.code as order_code,
                o.status as order_status,
                o.type as order_type,
                o.courier_id,
                o.created_at as order_created_at,
                o.updated_at as order_updated_at,
                o.delivery_address,
                o.pickup_lat,
                o.pickup_lng,
                o.dropoff_lat,
                o.dropoff_lng,
                o.customer as customer_name,
                o.phone as customer_phone,
                o.amount,
                r.name as restaurant_name,
                r.address_line1 as restaurant_address,
                r.phone as restaurant_phone
            FROM orders o
            LEFT JOIN restaurants r ON r.id = o.restaurant_id
            WHERE o.courier_id = $1
            ORDER BY o.created_at DESC
            LIMIT $2 OFFSET $3
        """, courier_id, limit, offset)
        
        # asyncpg.Record objelerini dict'e çevir
        result = []
        if rows:
            for row in rows:
                result.append(dict(row))
        
        return result
        
    except Exception as e:
        return []


async def get_order_courier_gps(order_id: str, restaurant_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Siparişe atanan kuryenin canlı GPS konumunu getir"""
    try:
        # Siparişi al ve restoran kontrolü yap
        order = await fetch_one("""
            SELECT id, courier_id, restaurant_id, code, customer
            FROM orders
            WHERE id = $1 AND restaurant_id = $2
        """, order_id, restaurant_id)
        
        if not order:
            return None, "Order not found or unauthorized"
        
        # Siparişe kurye atanmamış
        courier_id = order.get("courier_id")
        if not courier_id:
            return None, "No courier assigned to this order"
        
        # Kuryenin GPS konumunu ve bilgilerini al
        courier_data = await fetch_one("""
            SELECT 
                d.id as courier_id,
                CONCAT(d.first_name, ' ', d.last_name) as courier_name,
                d.phone as courier_phone,
                d.email as courier_email,
                g.latitude,
                g.longitude,
                g.updated_at as location_updated_at
            FROM drivers d
            LEFT JOIN gps_table g ON g.driver_id = d.id
            WHERE d.id = $1
        """, courier_id)
        
        if not courier_data:
            return None, "Courier not found"
        
        # GPS yoksa
        if courier_data.get("latitude") is None or courier_data.get("longitude") is None:
            return {
                "courier_id": courier_data.get("courier_id"),
                "courier_name": courier_data.get("courier_name"),
                "courier_phone": courier_data.get("courier_phone"),
                "courier_email": courier_data.get("courier_email"),
                "latitude": None,
                "longitude": None,
                "location_updated_at": None,
                "message": "No GPS location available yet"
            }, None
        
        return dict(courier_data), None
        
    except Exception as e:
        print(f"Error getting order courier GPS: {e}")
        return None, str(e)
    
async def reject_order_by_courier(courier_id: str, order_id: str) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(courier_id)
        uuid.UUID(order_id)
    except:
        return False, "Hatalı UUID"  
    try:
        order = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND courier_id=$2;",
            order_id, courier_id
        )
        if not order:
            return False, "Sipariş bulunamadı veya kurye yetkili değil"

        await execute(
            """
            INSERT INTO courier_orders_log (courier_id, order_id, action)
            VALUES ($1, $2, 'reddetti')
            ON CONFLICT (courier_id, order_id) DO NOTHING;
            """,
            courier_id, order_id
        )

        await execute(
            """
            UPDATE orders
            SET courier_id = NULL, status = 'kurye_reddetti', updated_at = NOW()
            WHERE id = $1;
            """,
            order_id
        )

        # Sipariş izleyicisini güncelle
        await update_available_drivers(uuid.UUID(order_id))
        await add_rejection(uuid.UUID(order_id), uuid.UUID(courier_id))
        await tick_watch(uuid.UUID(order_id))
        
        return True, None

    except Exception as e:
        return False, str(e)
    
async def accept_order_by_courier(courier_id: str, order_id: str) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(courier_id)
        uuid.UUID(order_id)
    except:
        return False, "Hatalı UUID"  
    try:
        order = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND courier_id = $2;",
            order_id, courier_id
        )
        if not order:
            return False, "Sipariş bulunamadı veya zaten bir kurye tarafından kabul edildi"

        await execute(
            """
            INSERT INTO courier_orders_log (courier_id, order_id, action)
            VALUES ($1, $2, 'kabul_etti')
            ON CONFLICT (courier_id, order_id) DO NOTHING;
            """,
            courier_id, order_id
        )

        await execute(
            """
            UPDATE orders
            SET status = 'kuryeye_verildi', updated_at = NOW()
            WHERE id = $1;
            """,
            order_id
        )

        # Sipariş izleyicisini güncelle
        await close(uuid.UUID(order_id))

        return True, None

    except Exception as e:
        return False, str(e)
    

async def get_courier_orders_log(
    courier_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int]:
    try:
        uuid.UUID(courier_id)
    except Exception:
        return [], 0

    offset_value = max(0, int(offset or 0))
    limit_value = int(limit or 50)
    if limit_value <= 0 or limit_value > 100:
        limit_value = 50

    try:
        rows = await fetch_all("""
            SELECT 
                col.id,
                col.order_id,
                col.action,
                col.created_at,
                o.code   AS order_code,
                o.status AS order_status,
                o.type   AS order_type,
                o.amount AS order_amount,
                r.name   AS restaurant_name,
                COUNT(*) OVER() AS total_count
            FROM courier_orders_log AS col
            LEFT JOIN orders      AS o ON o.id = col.order_id
            LEFT JOIN restaurants AS r ON r.id = o.restaurant_id
            WHERE col.courier_id = $1
            ORDER BY col.created_at DESC NULLS LAST
            LIMIT $2 OFFSET $3
        """, courier_id, limit_value, offset_value)

        logs = [dict(row) for row in rows] if rows else []
        total_count = int(rows[0]["total_count"]) if rows else 0
        for item in logs:
            item.pop("total_count", None)

        return logs, total_count

    except Exception:
        return [], 0
    
async def mark_order_as_delivered_by_courier(
    courier_id: str,
    order_id: str
) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(courier_id)
        uuid.UUID(order_id)
    except:
        return False, "Invalid UUID"  
    try:
        order = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND courier_id=$2;",
            order_id, courier_id
        )
        if not order:
            return False, "Order not found or unauthorized"

        await execute(
            """
            UPDATE orders
            SET status = 'kuryeye_verildi', updated_at = NOW()
            WHERE id = $1;
            """,
            order_id
        )

        return True, None

    except Exception as e:
        return False, str(e)
    
async def mark_order_as_courier_at_location(courier_id: str, order_id: str) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(courier_id)
        uuid.UUID(order_id)
    except:
        return False, "Invalid UUID"  
    try:
        order = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND courier_id=$2;",
            order_id, courier_id
        )
        if not order:
            return False, "Order not found or unauthorized"

        await execute(
            """
            UPDATE orders
            SET status = 'konuma_geldim', updated_at = NOW()
            WHERE id = $1;
            """,
            order_id
        )

        return True, None

    except Exception as e:
        return False, str(e)
    

async def mark_order_as_courier_delivered_order(
    courier_id: str,
    order_id: str
) -> Tuple[bool, Optional[str]]:
    try:
        uuid.UUID(courier_id)
        uuid.UUID(order_id)
    except:
        return False, "Invalid UUID"  
    try:
        order = await fetch_one(
            "SELECT id FROM orders WHERE id=$1 AND courier_id=$2;",
            order_id, courier_id
        )
        if not order:
            return False, "Order not found or unauthorized"

        await execute(
            """
            UPDATE orders
            SET status = 'teslim_edildi', updated_at = NOW()
            WHERE id = $1;
            """,
            order_id
        )

        return True, None

    except Exception as e:
        return False, str(e)