from uuid import UUID
from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq, PoolOrderRes
from ..utils.database_async import fetch_all, fetch_one, execute

TABLE_NAME = "pool_orders"

# TODO : Hata mesajlarını tükçeleştir
# TODO : Havuza atıldığında orderın durumunu güncelle
# TODO : get_pool_orders fonksiyonuna daha fazla detay ekle, normal orderlar nasıl geliyorsa öyle gelmeli

async def get_pool_orders(driver_id: str, page: int = 1, size: int = 50):
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sayfa numaraları sıfırdan büyük olmalı"
        )
    
    try:
        UUID(driver_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bilinmeyen sürücü ID"
        )    

    # Driver konumu
    driver_location = await fetch_one(
        """
        SELECT latitude, longitude 
        FROM gps_table 
        WHERE driver_id = $1
        """,
        driver_id
    )

    offset = (page - 1) * size

    if not driver_location:
        # Driver konumu yoksa basit sorgu
        query = f"""
            SELECT
                p.order_id,
                p.message,
                o.code AS order_code,
                o.status AS order_status,
                o.type AS order_type,
                o.created_at AS order_created_at,
                o.updated_at AS order_updated_at,
                o.delivery_address,
                o.pickup_lat,
                o.pickup_lng,
                o.dropoff_lat,
                o.dropoff_lng,
                o.customer AS customer_name,
                o.phone AS customer_phone,
                o.amount,
                r.name AS restaurant_name,
                r.address_line1 AS restaurant_address,
                r.phone AS restaurant_phone
            FROM pool_orders p
            JOIN orders o ON o.id = p.order_id
            LEFT JOIN restaurants r ON r.id = o.restaurant_id
            LIMIT $1 OFFSET $2
        """
        
        rows = await fetch_all(query, size, offset)
        return [PoolOrderRes(**{**dict(row), "order_id": str(row["order_id"])}) for row in rows]
    else:
        # Driver konumu varsa mesafeye göre sırala
        driver_lat = float(driver_location["latitude"])
        driver_lng = float(driver_location["longitude"])

        query = f"""
            SELECT
                p.order_id,
                p.message,
                o.code AS order_code,
                o.status AS order_status,
                o.type AS order_type,
                o.created_at AS order_created_at,
                o.updated_at AS order_updated_at,
                o.delivery_address,
                o.pickup_lat,
                o.pickup_lng,
                o.dropoff_lat,
                o.dropoff_lng,
                o.customer AS customer_name,
                o.phone AS customer_phone,
                o.amount,
                r.name AS restaurant_name,
                r.address_line1 AS restaurant_address,
                r.phone AS restaurant_phone,
                SQRT(
                    POWER(o.pickup_lat - {driver_lat}, 2) +
                    POWER(o.pickup_lng - {driver_lng}, 2)
                ) AS distance
            FROM pool_orders p
            JOIN orders o ON p.order_id = o.id
            LEFT JOIN restaurants r ON r.id = o.restaurant_id
            ORDER BY distance ASC
            LIMIT $1 OFFSET $2
        """

        rows = await fetch_all(query, size, offset)
        return [PoolOrderRes(**{**dict(row), "order_id": str(row["order_id"])}) for row in rows]
    
async def get_my_pool_orders(restaurant_id: str, page: int = 1, size: int = 50):
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sayfa numaraları sıfırdan büyük olmalı"
        )

    try:
        UUID(restaurant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bilinmeyen sürücü ID"
        )

    offset = (page - 1) * size

    query = f"""
        SELECT
            p.order_id,
            p.message,
            o.code AS order_code,
            o.status AS order_status,
            o.type AS order_type,
            o.created_at AS order_created_at,
            o.updated_at AS order_updated_at,
            o.delivery_address,
            o.pickup_lat,
            o.pickup_lng,
            o.dropoff_lat,
            o.dropoff_lng,
            o.customer AS customer_name,
            o.phone AS customer_phone,
            o.amount,
            r.name AS restaurant_name,
            r.address_line1 AS restaurant_address,
            r.phone AS restaurant_phone
        FROM {TABLE_NAME} p
        JOIN orders o ON o.id = p.order_id
        LEFT JOIN restaurants r ON r.id = o.restaurant_id
        WHERE o.restaurant_id = $1
        ORDER BY o.created_at DESC
        LIMIT $2 OFFSET $3
    """

    rows = await fetch_all(query, restaurant_id, size, offset)

    result = [PoolOrderRes(**dict(row)) for row in rows]

    return result


async def push_to_pool(req: PoolPushReq, restaurant_id: str):
    try:
        UUID(restaurant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bilinmeyen UUID formatı"
        )    

    # Sipariş gerçekten bu restorana ait mi kontrol et
    order_check = await fetch_one(
        """
        SELECT id 
        FROM orders
        WHERE id = $1 AND restaurant_id = $2;
        """,
        req.order_id,
        restaurant_id
    )

    if not order_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu sipariş bu restorana ait değil"
        )

    # Pool kayıt kontrolü
    exists = await fetch_one(
        f"SELECT order_id FROM {TABLE_NAME} WHERE order_id = $1;",
        req.order_id
    )

    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sipariş zaten havuzda"
        )

    # Kayıt ekle
    row = await fetch_one(
        """
            WITH ins AS (
                INSERT INTO pool_orders (order_id, message)
                VALUES ($1, $2)
                RETURNING order_id, message
            ),
            upd AS (
                UPDATE orders
                SET courier_id = NULL,
                    status = 'siparis_havuza_atildi',
                    updated_at = NOW()
                WHERE id = $1
                RETURNING *
            )
            SELECT
                upd.id AS order_id,
                $2 AS message,
                upd.code AS order_code,
                upd.status AS order_status,
                upd.type AS order_type,
                upd.created_at AS order_created_at,
                upd.updated_at AS order_updated_at,
                upd.delivery_address,
                upd.pickup_lat,
                upd.pickup_lng,
                upd.dropoff_lat,
                upd.dropoff_lng,
                upd.customer AS customer_name,
                upd.phone AS customer_phone,
                upd.amount,
                r.name AS restaurant_name,
                r.address_line1 AS restaurant_address,
                r.phone AS restaurant_phone
            FROM upd
            LEFT JOIN restaurants r ON r.id = upd.restaurant_id;

        """,
        req.order_id,
        req.message
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Havuza gönderilirken bir hata oluştu"
        )
    
    data = dict(row)
    data["order_id"] = str(data["order_id"])
    return PoolOrderRes(**data)

async def delete_pool_order(order_id: str):
    try:
        UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bilinmeyen UUID formatı"
        )
    
    query = f"""
        DELETE FROM {TABLE_NAME}
        WHERE order_id = $1
        RETURNING order_id;
    """

    result = await fetch_one(query, order_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sipariş havuzda değil"
        )

    return {"message": "Order deleted from pool", "order_id": order_id}

async def delete_pool_order_with_restaurant(order_id: str, restaurant_id: str):
    try:
        UUID(order_id)
        UUID(restaurant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bilinmeyen UUID formatı"
        )    

    # Siparişin bu restorana ait olup olmadığını kontrol et
    order_check = await fetch_one(
        """
        SELECT p.order_id
        FROM pool_orders AS p
        JOIN orders AS o ON p.order_id = o.id
        WHERE p.order_id = $1 AND o.restaurant_id = $2;
        """,
        order_id,
        restaurant_id
    )

    if not order_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sipariş bu restorana ait değil veya havuzda değil"
        )

    # Kayıt sil
    query = f"""
        DELETE FROM {TABLE_NAME}
        WHERE order_id = $1
        RETURNING order_id;
    """

    result = await fetch_one(query, order_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sipariş havuzda değil"
        )

    return {"message": "Order deleted from pool", "order_id": order_id}

async def try_push_to_pool(order_id: UUID):
    
    print(f"Trying to push order {order_id} to pool...")

    exists = await fetch_one(
        f"SELECT order_id FROM {TABLE_NAME} WHERE order_id = $1;",
        order_id
    )

    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already exists in pool"
        )

    # Kayıt ekle
    query = f"""
        INSERT INTO {TABLE_NAME} (order_id, message)
        VALUES ($1, $2)
        RETURNING order_id, message;
    """

    row = await fetch_one(query, order_id, "System auto-push")
    if not row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to push order to pool"
        )

    # TODO : Implement logic to decide whether to push to pool