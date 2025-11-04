from uuid import uuid4
from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq, PoolOrderModel
from ..utils.database_async import fetch_all, fetch_one

TABLE_NAME = "pool_orders"

async def get_pool_orders(driver_id: str):
    """
    Driver konumuna göre en yakın siparişleri (pickup konumlarına göre) listeler.
    """
    # Driver konumunu al
    driver_location = await fetch_one(
        "SELECT latitude, longitude FROM drivers WHERE id = $1;",
        driver_id
    )
    if not driver_location:
        return []

    driver_lat = driver_location["latitude"]
    driver_lng = driver_location["longitude"]

    # Driver konumuna göre sipariş pickup noktalarını mesafeye göre sırala
    query = f"""
        SELECT 
            p.id,
            p.order_id,
            p.restaurant_id,
            p.created_at,
            o.pickup_lat,
            o.pickup_lng,
            SQRT(POWER(o.pickup_lat - {driver_lat}, 2) + POWER(o.pickup_lng - {driver_lng}, 2)) AS distance
        FROM {TABLE_NAME} AS p
        JOIN orders AS o ON p.order_id = o.id
        ORDER BY distance ASC;
    """

    rows = await fetch_all(query)
    return [PoolOrderModel(**row) for row in rows]

async def push_to_pool(restaurant_id: str, req: PoolPushReq):
    # Aynı order zaten eklenmiş mi kontrol et
    exists_query = f"SELECT id FROM {TABLE_NAME} WHERE order_id = $1;"
    exists = await fetch_one(exists_query, req.order_id)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already exists in pool"
        )

    new_id = str(uuid4())
    query = f"""
        INSERT INTO {TABLE_NAME} (id, order_id, message, restaurant_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id, order_id, message, restaurant_id;
    """
    values = {
        "id": new_id,
        "order_id": req.order_id,
        "message": req.message,
        "restaurant_id": restaurant_id,
    }

    row = await fetch_one(query, values)
    return PoolOrderModel(**row)


async def delete_pool_order(order_id: str):
    query = f"DELETE FROM {TABLE_NAME} WHERE order_id = $1 RETURNING id;"
    result = await fetch_one(query, order_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in pool"
        )

    return {"message": "Order deleted from pool", "order_id": order_id}

async def try_push_to_pool(restaurant_id: str, req: PoolPushReq):
    try:
        return await push_to_pool(restaurant_id, req)
    except HTTPException as e:
        if e.status_code == status.HTTP_400_BAD_REQUEST and "already exists" in e.detail:
            return {"message": "Order already exists in pool", "order_id": req.order_id}
        else:
            raise
