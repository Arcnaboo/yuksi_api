from ..utils.database import db_cursor

def upsert_vehicle(driver_id: str, make: str, model: str, year: int, plate: str):
    with db_cursor() as cur:
        cur.execute(
            """INSERT INTO vehicles (driver_id,make,model,year,plate)
               VALUES (%s,%s,%s,%s,%s)
               ON CONFLICT (driver_id) DO UPDATE
               SET make=EXCLUDED.make, model=EXCLUDED.model, year=EXCLUDED.year, plate=EXCLUDED.plate""",
            (driver_id, make, model, year, plate),
        )

def insert_document(driver_id: str, doc_type: str, url: str):
    with db_cursor() as cur:
        cur.execute(
            "INSERT INTO documents (driver_id,doc_type,file_url) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
            (driver_id, doc_type, url),
        )

def list_documents(driver_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT doc_type,file_url,uploaded_at FROM documents WHERE driver_id=%s", (driver_id,))
        return cur.fetchall()

def finalize_profile(driver_id: str):
    with db_cursor() as cur:
        cur.execute("SELECT id FROM vehicles WHERE driver_id=%s", (driver_id,))
        if not cur.fetchone():
            return "Vehicle info missing"
        cur.execute("SELECT COUNT(*) FROM documents WHERE driver_id=%s", (driver_id,))
        if (cur.fetchone()[0] or 0) < 2:
            return "Upload at least license and criminal record"
    return None

def set_online(driver_id: str, online: bool):
    with db_cursor() as cur:
        if online:
            cur.execute(
                "INSERT INTO driver_status (driver_id,online) VALUES (%s,TRUE) ON CONFLICT (driver_id) DO UPDATE SET online=TRUE, updated_at=NOW()",
                (driver_id,),
            )
        else:
            cur.execute("UPDATE driver_status SET online=FALSE, updated_at=NOW() WHERE driver_id=%s", (driver_id,))

def earnings(driver_id: str) -> float:
    with db_cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(price),0) FROM jobs WHERE driver_id=%s AND status='delivered'", (driver_id,))
        return float(cur.fetchone()[0])

def get_banners():
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT title,image_url FROM banners WHERE active=TRUE ORDER BY priority DESC")
        return cur.fetchall()
