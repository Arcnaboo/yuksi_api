from uuid import UUID
from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq, PoolOrderRes
from ..utils.database_async import fetch_all, fetch_one

TABLE_NAME = "pool_orders"

async def get_pool_orders(driver_id: str, page: int = 1, size: int = 50):
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pagination parameters"
        )
    
    try:
        UUID(driver_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid driver ID"
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
                p.message
            FROM {TABLE_NAME} AS p
            LIMIT $1 OFFSET $2;
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
                SQRT(
                    POWER(o.pickup_lat - {driver_lat}, 2) +
                    POWER(o.pickup_lng - {driver_lng}, 2)
                ) AS distance
            FROM {TABLE_NAME} AS p
            JOIN orders AS o ON p.order_id = o.id
            ORDER BY distance ASC
            LIMIT $1 OFFSET $2;
        """

        rows = await fetch_all(query, size, offset)
        return [PoolOrderRes(**{**dict(row), "order_id": str(row["order_id"])}) for row in rows]

async def push_to_pool(req: PoolPushReq, restaurant_id: str):
    try:
        UUID(restaurant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format"
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
            detail="Order does not belong to this restaurant"
        )

    # Pool kayıt kontrolü
    exists = await fetch_one(
        f"SELECT order_id FROM {TABLE_NAME} WHERE order_id = $1;",
        req.order_id
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

    row = await fetch_one(query, req.order_id, req.message)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to push order to pool"
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
            detail="Invalid order ID format"
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
            detail="Order not found in pool"
        )

    return {"message": "Order deleted from pool", "order_id": order_id}


async def try_push_to_pool(order_id: str):
    try:
        order_id = UUID(order_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format"
        )    
    
    # TODO : Implement logic to decide whether to push to pool
