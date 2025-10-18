from typing import Optional, Tuple, Dict, Any
from app.utils.database_async import fetch_one, execute


# === START PAYMENT SESSION ===
async def start_payment_session(driver_id: str, job_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Bir iş için ödeme oturumu başlat"""
    try:
        row = await fetch_one(
            "SELECT price FROM jobs WHERE id = $1 AND driver_id = $2;",
            job_id, driver_id
        )
        if not row:
            return None, "Job not found"

        amount = row["price"]
        pay_row = await fetch_one(
            """
            INSERT INTO payments (job_id, amount)
            VALUES ($1, $2)
            ON CONFLICT (job_id)
            DO UPDATE SET amount = EXCLUDED.amount
            RETURNING id;
            """,
            job_id, amount
        )
        payment_id = pay_row["id"]

        return {
            "payment_id": payment_id,
            "redirect_url": f"https://fake-payment.com/{payment_id}",
        }, None

    except Exception as e:
        return None, str(e)


# === GET PAYMENT STATUS ===
async def get_payment_status(driver_id: str, payment_id: str) -> Optional[Dict[str, Any]]:
    """Ödeme durumunu getir"""
    query = """
        SELECT p.id, p.status, p.amount, j.id AS job_id
        FROM payments p
        JOIN jobs j ON j.id = p.job_id
        WHERE p.id = $1 AND j.driver_id = $2;
    """
    row = await fetch_one(query, payment_id, driver_id)
    return dict(row) if row else None
