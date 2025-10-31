
# app/services/courier_rating_service.py
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from ..utils.database import db_cursor

# ==================== KURYE ATAMA SERVISLERI ====================

async def assign_courier_to_order(
    order_id: str,
    restaurant_id: str,
    courier_id: str
) -> Tuple[bool, Optional[str]]:
    """Siparişe kurye ata"""
    try:
        with db_cursor() as cur:
            # Sipariş kontrolü - paket_servis tipi olmalı
            cur.execute("""
                SELECT id, type, status FROM orders 
                WHERE id=%s AND restaurant_id=%s
            """, (order_id, restaurant_id))
            
            order = cur.fetchone()
            if not order:
                return False, "Order not found"
            
            if order[1] != 'paket_servis':
                return False, "Only package service orders can be assigned to couriers"
            
            # Paket kontrolü - Restoranın kalan paketi var mı?
            cur.execute("""
                SELECT max_package
                FROM restaurant_package_prices
                WHERE restaurant_id = %s;
            """, (restaurant_id,))
            package_info = cur.fetchone()
            
            if package_info and package_info[0]:  # max_package tanımlıysa
                max_package = package_info[0]
                # Teslim edilmiş paket sayısını say
                cur.execute("""
                    SELECT COUNT(*) as delivered_count
                    FROM orders
                    WHERE restaurant_id = %s
                      AND type = 'paket_servis'
                      AND status = 'teslim_edildi';
                """, (restaurant_id,))
                delivered_result = cur.fetchone()
                delivered_count = delivered_result[0] if delivered_result else 0
                
                # Kalan paket kontrolü
                remaining_packages = max_package - delivered_count
                if remaining_packages <= 0:
                    return False, f"Paket hakkınız tükenmiş. Kalan paket: 0, Maksimum paket: {max_package}, Teslim edilen: {delivered_count}"
            
            # Kurye kontrolü
            cur.execute("SELECT id FROM drivers WHERE id=%s", (courier_id,))
            if not cur.fetchone():
                return False, "Courier not found"
            
            # Siparişe kurye ata ve durumu güncelle
            cur.execute("""
                UPDATE orders 
                SET courier_id=%s, status='kurye_cagrildi', updated_at=NOW()
                WHERE id=%s AND restaurant_id=%s
            """, (courier_id, order_id, restaurant_id))
            
            if cur.rowcount == 0:
                return False, "Failed to assign courier"
            
            return True, None
            
    except Exception as e:
        return False, str(e)

# ==================== KURYE PUANLAMA SERVISLERI ====================

async def create_courier_rating(
    restaurant_id: str,
    courier_id: str,
    order_id: str,
    rating: int,
    comment: Optional[str] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Kurye puanlama oluştur"""
    try:
        with db_cursor() as cur:
            # Sipariş kontrolü - teslim edilmiş olmalı ve bu kuryeye atanmış olmalı
            cur.execute("""
                SELECT id, status, courier_id FROM orders 
                WHERE id=%s AND restaurant_id=%s AND courier_id=%s AND status='teslim_edildi'
            """, (order_id, restaurant_id, courier_id))
            
            if not cur.fetchone():
                return None, "Order not found, not delivered, or not assigned to this courier"
            
            # Zaten puanlanmış mı kontrol et
            cur.execute("""
                SELECT id FROM courier_ratings 
                WHERE restaurant_id=%s AND courier_id=%s AND order_id=%s
            """, (restaurant_id, courier_id, order_id))
            
            if cur.fetchone():
                return None, "Rating already exists for this order"
            
            # Puanlama oluştur
            cur.execute("""
                INSERT INTO courier_ratings (restaurant_id, courier_id, order_id, rating, comment)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (restaurant_id, courier_id, order_id, rating, comment))
            
            result = cur.fetchone()
            return {
                "id": str(result[0]),
                "created_at": result[1]
            }, None
            
    except Exception as e:
        return None, str(e)

async def update_courier_rating(
    rating_id: str,
    restaurant_id: str,
    rating: Optional[int] = None,
    comment: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """Kurye puanlamasını güncelle"""
    try:
        with db_cursor() as cur:
            # Puanlama kontrolü
            cur.execute("""
                SELECT id FROM courier_ratings 
                WHERE id=%s AND restaurant_id=%s
            """, (rating_id, restaurant_id))
            
            if not cur.fetchone():
                return False, "Rating not found"
            
            # Güncelleme yapılacak alanları belirle
            update_fields = []
            params = []
            
            if rating is not None:
                update_fields.append("rating = %s")
                params.append(rating)
            
            if comment is not None:
                update_fields.append("comment = %s")
                params.append(comment)
            
            if not update_fields:
                return False, "No fields to update"
            
            update_fields.append("updated_at = NOW()")
            params.extend([rating_id, restaurant_id])
            
            cur.execute(f"""
                UPDATE courier_ratings 
                SET {', '.join(update_fields)}
                WHERE id = %s AND restaurant_id = %s
            """, params)
            
            if cur.rowcount == 0:
                return False, "Failed to update rating"
            
            return True, None
            
    except Exception as e:
        return False, str(e)

async def delete_courier_rating(
    rating_id: str,
    restaurant_id: str
) -> Tuple[bool, Optional[str]]:
    """Kurye puanlamasını sil"""
    try:
        with db_cursor() as cur:
            cur.execute("""
                DELETE FROM courier_ratings 
                WHERE id=%s AND restaurant_id=%s
            """, (rating_id, restaurant_id))
            
            if cur.rowcount == 0:
                return False, "Rating not found"
            
            return True, None
            
    except Exception as e:
        return False, str(e)

async def get_courier_ratings(
    restaurant_id: str,
    courier_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Kurye puanlamalarını getir"""
    with db_cursor(dict_cursor=True) as cur:
        where_conditions = ["cr.restaurant_id = %s"]
        params = [restaurant_id]
        
        if courier_id:
            where_conditions.append("cr.courier_id = %s")
            params.append(courier_id)
        
        where_clause = " AND ".join(where_conditions)
        
        cur.execute(f"""
            SELECT 
                cr.id,
                cr.restaurant_id,
                cr.courier_id,
                cr.order_id,
                cr.rating,
                cr.comment,
                cr.created_at,
                cr.updated_at,
                d.first_name,
                d.last_name,
                o.code as order_code
            FROM courier_ratings cr
            LEFT JOIN drivers d ON d.id = cr.courier_id
            LEFT JOIN orders o ON o.id = cr.order_id
            WHERE {where_clause}
            ORDER BY cr.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        return cur.fetchall() or []

async def get_courier_rating_summary(courier_id: str) -> Optional[Dict[str, Any]]:
    """Kurye puanlama özeti"""
    with db_cursor(dict_cursor=True) as cur:
        # Kurye bilgileri
        cur.execute("""
            SELECT first_name, last_name FROM drivers WHERE id = %s
        """, (courier_id,))
        
        courier = cur.fetchone()
        if not courier:
            return None
        
        # Puanlama istatistikleri
        cur.execute("""
            SELECT 
                AVG(rating) as average_rating,
                COUNT(*) as total_ratings
            FROM courier_ratings 
            WHERE courier_id = %s
        """, (courier_id,))
        
        stats = cur.fetchone()
        
        # Son puanlamalar
        cur.execute("""
            SELECT 
                cr.id,
                cr.restaurant_id,
                cr.courier_id,
                cr.order_id,
                cr.rating,
                cr.comment,
                cr.created_at,
                cr.updated_at,
                r.name as restaurant_name
            FROM courier_ratings cr
            LEFT JOIN restaurants r ON r.id = cr.restaurant_id
            WHERE cr.courier_id = %s
            ORDER BY cr.created_at DESC
            LIMIT 10
        """, (courier_id,))
        
        recent_ratings = cur.fetchall() or []
        
        return {
            "courier_id": courier_id,
            "courier_name": f"{courier['first_name']} {courier['last_name']}",
            "average_rating": float(stats['average_rating']) if stats['average_rating'] else 0.0,
            "total_ratings": stats['total_ratings'] or 0,
            "recent_ratings": recent_ratings
        }

async def get_available_couriers(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Mevcut kuryeleri getir"""
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("""
            SELECT 
                d.id,
                d.first_name,
                d.last_name,
                d.email,
                d.phone,
                COALESCE(AVG(cr.rating), 0) as average_rating,
                COUNT(cr.id) as total_ratings
            FROM drivers d
            LEFT JOIN courier_ratings cr ON d.id = cr.courier_id
            GROUP BY d.id, d.first_name, d.last_name, d.email, d.phone
            ORDER BY average_rating DESC, total_ratings DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        return cur.fetchall() or []


