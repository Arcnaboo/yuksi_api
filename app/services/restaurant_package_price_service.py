from app.utils.database import db_cursor
from typing import Dict, Any, Optional, Tuple


# ✅ RESTAURANT PAKET DURUMUNU HESAPLA
async def get_restaurant_package_status(restaurant_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Restaurant'ın paket durumunu hesapla (kalan paket, teslim edilen, toplam)"""
    try:
        with db_cursor(dict_cursor=True) as cur:
            # Paket fiyat bilgilerini getir
            cur.execute("""
                SELECT 
                    id,
                    restaurant_id,
                    unit_price,
                    min_package,
                    max_package,
                    note,
                    updated_at
                FROM restaurant_package_prices
                WHERE restaurant_id = %s;
            """, (restaurant_id,))
            package_info = cur.fetchone()
            
            if not package_info:
                return False, None, "Paket tanımı bulunamadı"
            
            max_package = package_info.get("max_package") or 0
            
            # Teslim edilmiş paket sayısını hesapla
            cur.execute("""
                SELECT COUNT(*) as delivered_count
                FROM orders
                WHERE restaurant_id = %s
                  AND type = 'paket_servis'
                  AND status = 'teslim_edildi';
            """, (restaurant_id,))
            delivered_result = cur.fetchone()
            delivered_count = delivered_result.get("delivered_count", 0) if delivered_result else 0
            
            # Toplam paket sipariş sayısı (tüm durumlar)
            cur.execute("""
                SELECT COUNT(*) as total_count
                FROM orders
                WHERE restaurant_id = %s
                  AND type = 'paket_servis';
            """, (restaurant_id,))
            total_result = cur.fetchone()
            total_count = total_result.get("total_count", 0) if total_result else 0
            
            # Kalan paket sayısı
            remaining_packages = max_package - delivered_count if max_package > 0 else None
            
            # Uyarı mesajı (10 ve 3 paket kaldığında)
            warning_message = None
            if remaining_packages is not None and remaining_packages == 10:
                warning_message = "Paketiniz bitmek üzere! Lütfen paket yükleyin."
            elif remaining_packages is not None and remaining_packages == 3:
                warning_message = "Paketiniz bitmek üzere! Lütfen paket yükleyin."
            elif remaining_packages is not None and remaining_packages == 0:
                warning_message = "Paket hakkınız tükenmiştir!"
            
            return True, {
                "package_info": package_info,
                "max_package": max_package,
                "delivered_count": delivered_count,
                "total_count": total_count,
                "remaining_packages": remaining_packages,
                "has_package_left": remaining_packages is None or remaining_packages > 0,
                "warning_message": warning_message
            }, None
            
    except Exception as e:
        return False, None, str(e)


# ✅ CREATE or UPDATE (UUID uyumlu)
async def create_or_update_price(data):
    try:
        with db_cursor() as cur:
            # Eğer restoranın kaydı varsa güncelle, yoksa oluştur
            cur.execute("""
                INSERT INTO restaurant_package_prices 
                    (restaurant_id, unit_price, min_package, max_package, note)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (restaurant_id)
                DO UPDATE SET
                    unit_price = EXCLUDED.unit_price,
                    min_package = EXCLUDED.min_package,
                    max_package = EXCLUDED.max_package,
                    note = EXCLUDED.note,
                    updated_at = now()
                RETURNING id;
            """, (
                str(data["restaurant_id"]),  # ✅ UUID → string
                data["unit_price"],
                data.get("min_package"),
                data.get("max_package"),
                data.get("note")
            ))

            result = cur.fetchone()

        return True, {"id": str(result[0])}
    except Exception as e:
        return False, str(e)


# ✅ LIST ALL PRICES
async def list_prices():
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT 
                    p.id,
                    r.name AS restaurant_name,
                    r.email,
                    p.unit_price,
                    p.min_package,
                    p.max_package,
                    p.note,
                    p.updated_at
                FROM restaurant_package_prices p
                JOIN restaurants r ON r.id = p.restaurant_id
                ORDER BY p.updated_at DESC;
            """)
            data = cur.fetchall()

        return True, data
    except Exception as e:
        return False, str(e)


# ✅ UPDATE BY ID
async def update_price(id: str, data):
    try:
        with db_cursor() as cur:
            cur.execute("""
                UPDATE restaurant_package_prices
                SET unit_price = %s,
                    min_package = %s,
                    max_package = %s,
                    note = %s,
                    updated_at = now()
                WHERE id = %s
                RETURNING id;
            """, (
                data["unit_price"],
                data.get("min_package"),
                data.get("max_package"),
                data.get("note"),
                str(id)  # ✅ UUID → string
            ))
            result = cur.fetchone()

        if not result:
            return False, "Record not found"

        return True, {"id": str(result[0])}

    except Exception as e:
        return False, str(e)


# ✅ DELETE BY RESTAURANT ID
async def delete_price(restaurant_id: str):
    try:
        with db_cursor() as cur:
            cur.execute("""
                DELETE FROM restaurant_package_prices
                WHERE restaurant_id = %s
                RETURNING id;
            """, (str(restaurant_id),))  # ✅ UUID → string

            deleted = cur.fetchone()

        if not deleted:
            return False, "Record not found"

        return True, {"restaurant_id": str(restaurant_id)}

    except Exception as e:
        return False, str(e)
