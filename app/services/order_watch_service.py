from uuid import UUID

from fastapi import HTTPException
from ..utils.database_async import fetch_one, fetch_all, execute
from ..models.order_watch_model import OrderWatch
from ..services.pool_service import try_push_to_pool
from ..services.restaurant_service import get_nearby_couriers

TABLE = "order_watchers"

async def create_watch(order_id: UUID):
    restaurant_row = await fetch_one(
        "SELECT restaurant_id FROM orders WHERE id = $1",
        order_id
    )

    if not restaurant_row:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    restaurant_id = restaurant_row["restaurant_id"]

    # === Restoranın kendi kuryeleri (online ve aktif) ===
    restaurant_drivers_rows = await fetch_all(
        """
        SELECT d.id AS driver_id
        FROM restaurant_couriers rc
        JOIN drivers d ON d.id = rc.courier_id
        JOIN driver_status ds ON ds.driver_id = d.id
        WHERE rc.restaurant_id = $1
          AND d.is_active = true
          AND d.deleted = false
          AND COALESCE(ds.online, false) = true
        """,
        restaurant_id
    )

    restaurant_drivers = [row["driver_id"] for row in restaurant_drivers_rows]

    # === 10 km içindeki kuryeler (zaten online ve aktif filtreli) ===
    nearby_rows = await get_nearby_couriers(restaurant_id)

    nearby_driver_ids = [row["courier_id"] for row in nearby_rows]

    # === Tek liste: sadece uygun sürücüler ===
    drivers = list(set(restaurant_drivers + nearby_driver_ids))

    await execute(
        f"""
        INSERT INTO {TABLE} 
        (order_id, restaurant_id, avalible_drivers, rejected_drivers, last_check, closed)
        VALUES ($1, $2, $3, ARRAY[]::uuid[], NOW(), false)
        """,
        order_id,
        restaurant_id,
        drivers
    )

async def update_available_drivers(order_id: UUID):
    row = await fetch_one(
        "SELECT restaurant_id FROM orders WHERE id = $1",
        order_id
    )
    if not row:
        return

    restaurant_id = row["restaurant_id"]

    # Restoran online kuryeleri
    restaurant_drivers_rows = await fetch_all(
        """
        SELECT d.id AS driver_id
        FROM restaurant_couriers rc
        JOIN drivers d ON d.id = rc.courier_id
        JOIN driver_status ds ON ds.driver_id = d.id
        WHERE rc.restaurant_id = $1
          AND d.is_active = true
          AND d.deleted = false
          AND COALESCE(ds.online, false) = true
        """,
        restaurant_id
    )
    restaurant_driver_ids = [r["driver_id"] for r in restaurant_drivers_rows]

    # Çevredeki online+aktif kuryeler (10 km)
    nearby_rows = await get_nearby_couriers(restaurant_id)
    nearby_driver_ids = [r["courier_id"] for r in nearby_rows]

    # Final liste
    drivers = list(set(restaurant_driver_ids + nearby_driver_ids))

    await execute(
        f"""
        UPDATE {TABLE}
        SET avalible_drivers = $2,
            last_check = NOW()
        WHERE order_id = $1 AND closed = false
        """,
        order_id,
        drivers
    )



async def add_rejection(order_id: UUID, driver_id: UUID):
    await execute(
        f"""
        UPDATE {TABLE}
        SET rejected_drivers = array_append(rejected_drivers, $2),
            last_check = NOW()
        WHERE order_id = $1 AND closed = false
        """,
        order_id,
        driver_id
    )


async def get_watch(order_id: UUID) -> OrderWatch | None:
    row = await fetch_one(
        f"SELECT * FROM {TABLE} WHERE order_id = $1",
        order_id
    )
    return OrderWatch(**row) if row else None


async def compute_final_candidates(order_id: UUID) -> list[UUID]:
    row = await get_watch(order_id)
    if not row:
        return []

    avail = set(row.avalible_drivers or [])
    rejected = set(row.rejected_drivers or [])

    return list(avail - rejected)

async def open(order_id: UUID):
    await execute(
        f"UPDATE {TABLE} SET closed = false WHERE order_id = $1",
        order_id
    )

async def close(order_id: UUID):
    await execute(
        f"UPDATE {TABLE} SET closed = true WHERE order_id = $1",
        order_id
    )

async def delete(order_id: UUID):
    await execute(
        f"DELETE FROM {TABLE} WHERE order_id = $1",
        order_id
    )

async def tick_watch(order_id: UUID):
    watch = await get_watch(order_id)
    if not watch or watch.closed:
        return

    candidates = await compute_final_candidates(order_id)

    if len(candidates) == 0:
        pushed = await try_push_to_pool(order_id)
        if not pushed:
            return
        await close(order_id)