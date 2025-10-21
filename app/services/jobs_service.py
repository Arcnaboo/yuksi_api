import uuid
from app.utils.database_async import fetch_all, fetch_one, execute


# === TÜM UYGUN İŞLER ===
async def list_available_jobs():
    query = """
        SELECT id, customer_name, customer_phone, pickup_address, drop_address, price
        FROM jobs
        WHERE status = 'pending'
        ORDER BY created_at DESC;
    """
    rows = await fetch_all(query)
    return [dict(r) for r in rows] if rows else []


# === İŞ KABUL ET ===
async def accept_job(driver_id: str, job_id: str) -> bool:
    try:
        uuid.UUID(driver_id)
        uuid.UUID(job_id)
    except:
        return None
    query = """
        UPDATE jobs
        SET status = 'accepted',
            driver_id = $1,
            updated_at = NOW()
        WHERE id = $2
          AND status = 'pending';
    """
    result = await execute(query, driver_id, job_id)
    # asyncpg `execute()` sonuç formatı: "UPDATE <rowcount>"
    return result and result.startswith("UPDATE") and not result.endswith(" 0")


# === DURUM GÜNCELLE ===
async def update_job_status(driver_id: str, job_id: str, status: str):
    allowed = {"picked_up", "arrived", "delivered"}
    if status not in allowed:
        return False, "Invalid status"
    try:
        uuid.UUID(driver_id)
        uuid.UUID(job_id)
    except:
        return None, "Invalid UUID"
    query = """
        UPDATE jobs
        SET status = $1,
            updated_at = NOW()
        WHERE id = $2
          AND driver_id = $3;
    """
    result = await execute(query, status, job_id, driver_id)
    if not result or result.endswith(" 0"):
        return False, "Job not found or not yours"

    return True, None


# === KENDİ İŞLERİM ===
async def my_jobs(driver_id: str):
    try:
        uuid.UUID(driver_id)
    except:
        return None
    query = """
        SELECT id, customer_name, customer_phone, pickup_address, drop_address,
               price, status, created_at
        FROM jobs
        WHERE driver_id = $1
        ORDER BY created_at DESC;
    """
    rows = await fetch_all(query, driver_id)
    return [dict(r) for r in rows] if rows else []
