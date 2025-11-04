from datetime import datetime
from uuid import uuid4
from fastapi import HTTPException, status
from ..models.pool_model import PoolPushReq, PoolOrderModel
from ..database import database  # mevcut async Database instance'ını kullan

TABLE_NAME = "pool_orders"

async def get_pool_orders(driver_id: str):
    """
    Şu anda basit bir örnek olarak tüm pool kayıtlarını döner.
    Eğer driver_id -> order bağlantısı varsa burada JOIN'le filtrelenebilir.
    """
    query = f"SELECT id, order_id, restaurant_id, created_at FROM {TABLE_NAME};"
    rows = await database.fetch_all(query)
    return [PoolOrderModel(**row) for row in rows]


async def push_to_pool(restaurant_id: str, req: PoolPushReq):
    # Aynı order zaten eklenmiş mi kontrol et
    exists_query = f"SELECT id FROM {TABLE_NAME} WHERE order_id = :order_id;"
    exists = await database.fetch_one(exists_query, {"order_id": req.order_id})
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already exists in pool"
        )

    new_id = str(uuid4())
    query = f"""
        INSERT INTO {TABLE_NAME} (id, order_id, message, created_at, restaurant_id)
        VALUES (:id, :order_id, :message, NOW(), :restaurant_id)
        RETURNING id, order_id, restaurant_id, created_at;
    """
    values = {
        "id": new_id,
        "order_id": req.order_id,
        "message": req.message,
        "restaurant_id": restaurant_id,
    }

    row = await database.fetch_one(query, values)
    return PoolOrderModel(**row)


async def delete_pool_order(order_id: str):
    query = f"DELETE FROM {TABLE_NAME} WHERE order_id = :order_id RETURNING id;"
    result = await database.fetch_one(query, {"order_id": order_id})

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in pool"
        )

    return {"message": "Order deleted from pool", "order_id": order_id}
