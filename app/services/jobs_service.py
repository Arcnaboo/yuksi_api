from ..utils.database import db_cursor  # <-- doğru modül
# FastAPI Depends kullanmadan, doğrudan servis fonksiyonları

def list_available_jobs():
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            """SELECT id,customer_name,customer_phone,pickup_address,drop_address,price
               FROM jobs
               WHERE status='pending'
               ORDER BY created_at DESC"""
        )
        return cur.fetchall()

def accept_job(driver_id: str, job_id: str) -> bool:
    with db_cursor() as cur:
        cur.execute(
            "UPDATE jobs SET status='accepted', driver_id=%s, updated_at=NOW() WHERE id=%s AND status='pending'",
            (driver_id, job_id),
        )
        return cur.rowcount > 0

def update_job_status(driver_id: str, job_id: str, status: str):
    allowed = {"picked_up", "arrived", "delivered"}
    if status not in allowed:
        return False, "Invalid status"
    with db_cursor() as cur:
        cur.execute(
            "UPDATE jobs SET status=%s, updated_at=NOW() WHERE id=%s AND driver_id=%s",
            (status, job_id, driver_id),
        )
        if cur.rowcount == 0:
            return False, "Job not found or not yours"
    return True, None

def my_jobs(driver_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            """SELECT id,customer_name,customer_phone,pickup_address,drop_address,price,status,created_at
               FROM jobs
               WHERE driver_id=%s
               ORDER BY created_at DESC""",
            (driver_id,),
        )
        return cur.fetchall()
