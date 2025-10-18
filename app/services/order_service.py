from typing import Optional, List, Dict, Any, Tuple
import random
import string
from datetime import datetime
from app.utils.database_async import fetch_one, fetch_all, execute


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
        rest = await fetch_one("SELECT id FROM restaurants WHERE id=$1;", restaurant_id)
        if not rest:
            return None, "Restaurant not found"

        code = await generate_order_code()
        row = await fetch_one(
            """
            INSERT INTO orders (
                restaurant_id, code, customer, phone, address, delivery_address,
                type, amount, carrier_type, vehicle_type, cargo_type, special_requests
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            RETURNING id, created_at;
            """,
            restaurant_id, code, customer, phone, address, delivery_address,
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

        return {"id": str(order_id), "code": code, "created_at": created_at}, None

    except Exception as e:
        return None, str(e)


# === Sipariş Detayı ===
async def get_order(order_id: str, restaurant_id: str) -> Optional[Dict[str, Any]]:
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
    try:
        result = await execute(
            "DELETE FROM orders WHERE id=$1 AND restaurant_id=$2;",
            order_id, restaurant_id
        )
        if result.endswith(" 0"):
            return False, "Order not found"
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
    offset: int = 0,
) -> Tuple[List[Dict[str, Any]], int, float]:
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
    return await list_orders(restaurant_id, status, order_type, search, start_date, end_date, limit, offset)
