from ..utils.database import db_cursor

def start_payment_session(driver_id: str, job_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT price FROM jobs WHERE id=%s AND driver_id=%s", (job_id, driver_id))
        row = cur.fetchone()
        if not row:
            return None, "Job not found"
        amount = row["price"]
        cur.execute(
            "INSERT INTO payments (job_id,amount) VALUES (%s,%s) ON CONFLICT (job_id) DO UPDATE SET amount=EXCLUDED.amount RETURNING id",
            (job_id, amount),
        )
        payment_id = cur.fetchone()["id"]
        return {"payment_id": payment_id, "redirect_url": f"https://fake-payment.com/{payment_id}"}, None

def get_payment_status(driver_id: str, payment_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            """SELECT p.id,p.status,p.amount,j.id as job_id
               FROM payments p
               JOIN jobs j ON j.id=p.job_id
               WHERE p.id=%s AND j.driver_id=%s""",
            (payment_id, driver_id),
        )
        return cur.fetchone()
