# app/services/order_service.py
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
import random
import string
from datetime import datetime
from ..utils.database import db_cursor

def generate_order_code() -> str:
    """ORD-YYMMDD formatında random kod üret"""
    today = datetime.now()
    date_part = today.strftime("%y%m%d")
    random_part = ''.join(random.choices(string.digits, k=3))
    return f"ORD-{date_part}{random_part}"

def create_order(
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
    items: List[Dict[str, Any]] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Sipariş oluştur"""
    try:
        with db_cursor() as cur:
            # Restoran kontrolü
            cur.execute("SELECT id FROM restaurants WHERE id=%s", (restaurant_id,))
            if not cur.fetchone():
                return None, "Restaurant not found"
            
            # Random kod üret
            code = generate_order_code()
            
            # Sipariş oluştur
            cur.execute("""
                INSERT INTO orders (
                    restaurant_id, code, customer, phone, address, delivery_address,
                    type, amount, carrier_type, vehicle_type, cargo_type, special_requests
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (
                restaurant_id, code, customer, phone, address, delivery_address,
                order_type, amount, carrier_type, vehicle_type, cargo_type, special_requests
            ))
            
            order_row = cur.fetchone()
            order_id = order_row[0]
            created_at = order_row[1]
            
            # Ürünleri ekle
            if items:
                for item in items:
                    total = item['price'] * item['quantity']
                    cur.execute("""
                        INSERT INTO order_items (order_id, product_name, price, quantity, total)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['product_name'], item['price'], item['quantity'], total))
            
            return {
                "id": str(order_id),
                "code": code,
                "created_at": created_at
            }, None
            
    except Exception as e:
        return None, str(e)

def get_order(order_id: str, restaurant_id: str) -> Optional[Dict[str, Any]]:
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

def update_order(
    order_id: str,
    restaurant_id: str,
    **kwargs
) -> Tuple[bool, Optional[str]]:
    """Sipariş güncelle"""
    try:
        with db_cursor() as cur:
            # Sipariş kontrolü
            cur.execute("SELECT id FROM orders WHERE id=%s AND restaurant_id=%s", (order_id, restaurant_id))
            if not cur.fetchone():
                return False, "Order not found"
            
            # Güncellenecek alanları hazırla
            update_fields = []
            update_values = []
            
            for field, value in kwargs.items():
                if value is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(value)
            
            if not update_fields:
                return True, None
            
            # Sipariş güncelle
            update_values.append(order_id)
            cur.execute(f"""
                UPDATE orders 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = %s
            """, update_values)
            
            # Ürünler güncelleniyorsa
            if 'items' in kwargs and kwargs['items']:
                # Eski ürünleri sil
                cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
                
                # Yeni ürünleri ekle
                for item in kwargs['items']:
                    total = item['price'] * item['quantity']
                    cur.execute("""
                        INSERT INTO order_items (order_id, product_name, price, quantity, total)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['product_name'], item['price'], item['quantity'], total))
            
            return True, None
            
    except Exception as e:
        return False, str(e)

def delete_order(order_id: str, restaurant_id: str) -> Tuple[bool, Optional[str]]:
    """Sipariş sil"""
    try:
        with db_cursor() as cur:
            cur.execute("DELETE FROM orders WHERE id=%s AND restaurant_id=%s", (order_id, restaurant_id))
            if cur.rowcount == 0:
                return False, "Order not found"
            return True, None
    except Exception as e:
        return False, str(e)

def list_orders(
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
            SELECT o.id, o.code, o.customer, o.phone, o.address, o.delivery_address, o.type, o.amount, o.status, o.created_at
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

def get_order_history(
    restaurant_id: str,
    status: Optional[str] = None,
    order_type: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Dict[str, Any]], int, float]:
    """Sipariş geçmişi (list_orders ile aynı ama farklı response formatı)"""
    return list_orders(restaurant_id, status, order_type, search, start_date, end_date, limit, offset)