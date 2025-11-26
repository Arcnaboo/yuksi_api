from app.utils.database_async import fetch_one, fetch_all, execute
from typing import Optional


# === UPSERT VEHICLE ===
async def upsert_vehicle(driver_id: str, make: str, model: str, year: int, plate: str):
    query = """
        INSERT INTO vehicles (driver_id, make, model, year, plate)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (driver_id) DO UPDATE
        SET make = EXCLUDED.make,
            model = EXCLUDED.model,
            year  = EXCLUDED.year,
            plate = EXCLUDED.plate;
    """
    await execute(query, driver_id, make, model, year, plate)


# === INSERT DOCUMENT ===
async def insert_document(driver_id: str, doc_type: str, url: str):
    query = """
        INSERT INTO documents (driver_id, doc_type, file_url)
        VALUES ($1, $2, $3)
        ON CONFLICT DO NOTHING;
    """
    await execute(query, driver_id, doc_type, url)


# === LIST DOCUMENTS ===
async def list_documents(driver_id: str):
    query = """
        SELECT doc_type, file_url, uploaded_at
        FROM documents
        WHERE driver_id = $1;
    """
    rows = await fetch_all(query, driver_id)
    return [dict(r) for r in rows] if rows else []


# === FINALIZE PROFILE ===
async def finalize_profile(driver_id: str):
    # Check vehicle existence
    vehicle = await fetch_one("SELECT id FROM vehicles WHERE driver_id=$1;", driver_id)
    if not vehicle:
        return "Vehicle info missing"

    # Check documents
    row = await fetch_one("SELECT COUNT(*) AS count FROM documents WHERE driver_id=$1;", driver_id)
    if not row or (row["count"] or 0) < 2:
        return "Upload at least license and criminal record"

    return None


# === HELPER: CHECK DOCUMENTS APPROVED ===
async def _check_documents_approved(driver_id: str) -> bool:
    """
    Kuryenin tüm belgelerinin onaylanıp onaylanmadığını kontrol eder
    """
    doc_check = await fetch_one("""
        SELECT 
            COUNT(*) as total_docs,
            COUNT(CASE WHEN courier_document_status = 'onaylandi' THEN 1 END) as approved_docs
        FROM courier_documents
        WHERE user_id = $1::uuid
    """, driver_id)
    
    if not doc_check:
        return False
    
    total = doc_check.get("total_docs", 0) or 0
    approved = doc_check.get("approved_docs", 0) or 0
    
    # En az bir belge olmalı ve tüm belgeler onaylı olmalı
    return total > 0 and approved == total

# === SET ONLINE STATUS ===

async def set_online(driver_id: str, online: bool, at: Optional[str] = None):
    # Online olmak için belgelerin onaylanmış olması gerekiyor
    if online:
        documents_approved = await _check_documents_approved(driver_id)
        if not documents_approved:
            return {"documents_not_approved": True, "message": "Tüm belgeleriniz onaylanmadan çevrimiçi olamazsınız"}
    
    exists = await fetch_one("""
        SELECT EXISTS (
            SELECT 1
            FROM courier_package_subscriptions
            WHERE courier_id = $1::uuid
            AND is_active = TRUE
            AND deleted_at IS NULL
            AND start_date <= NOW()
            AND end_date   >  NOW()
        ) AS ok
    """, driver_id)
    is_ok = bool(exists and (exists["ok"] is True))
    if not is_ok:
        return {"subscription_inactive_or_expired": True}

    checkDriver = await fetch_one(
        "SELECT id FROM drivers WHERE id = $1::uuid  AND is_active = TRUE AND (deleted IS NULL OR deleted = FALSE)",
        driver_id
    )
    if not checkDriver:
        return {"deleted": True}
    
    last = await fetch_one(
        "SELECT online FROM driver_status WHERE driver_id = $1::uuid",
        driver_id
    )
    if last is not None and last["online"] == online:
        return {"changed": False, "inserted_event": False}


    sql = """
    WITH ts AS (
      SELECT COALESCE($3::timestamptz, NOW()) AS ts
    ),
    ins_event AS (
      INSERT INTO driver_presence_events (driver_id, is_online, at_utc)
      SELECT $1::uuid, $2, ts.ts FROM ts
      RETURNING 1
    ),
    up_status AS (
      INSERT INTO driver_status (driver_id, online, updated_at)
      SELECT $1::uuid, $2, ts.ts FROM ts
      ON CONFLICT (driver_id) DO UPDATE
        SET online = EXCLUDED.online,
            updated_at = EXCLUDED.updated_at
      RETURNING 1
    )
    SELECT 1;
    """
    await execute(sql, driver_id, online, at)
    return {"changed": True, "inserted_event": True}


# === GET EARNINGS ===
async def earnings(driver_id: str) -> float:
    query = """
        SELECT COALESCE(SUM(price), 0) AS total
        FROM jobs
        WHERE driver_id = $1
          AND status = 'delivered';
    """
    row = await fetch_one(query, driver_id)
    return float(row["total"]) if row else 0.0

async def how_many_left_works_hour(driver_id: str):
    # 1) Geçerli abonelik + paket meta
    sub = await fetch_one("""
        SELECT s.id AS subscription_id,
               s.start_date,
               s.end_date,
               p.id  AS package_id,
               COALESCE(p.duration_days, 0)::numeric AS duration_days
        FROM courier_package_subscriptions s
        JOIN courier_packages p ON p.id = s.package_id
        WHERE s.courier_id = $1::uuid
          AND s.is_active = TRUE
          AND s.deleted_at IS NULL
          AND s.start_date <= NOW()
          AND s.end_date   >  NOW()
        ORDER BY s.end_date DESC
        LIMIT 1
    """, driver_id)

    if not sub:
        return {
            "success": False,
            "message": "Active subscription not found",
            "data": {"remaining_hours": 0.0, "consumed_hours": 0.0}
        }

    start_date = sub["start_date"]
    # pencere sonunu 'şu an' ile sınırla (henüz bitmediyse)
    end_or_now_sql = "LEAST($3::timestamptz, NOW())"
    total_quota_hours = float(sub["duration_days"]) * 24.0

    row = await fetch_one(f"""
        WITH bounds AS (
            SELECT $1::uuid AS driver_id,
                   $2::timestamptz AS win_start,
                   {end_or_now_sql} AS win_end
        ),
        base_events AS (
            SELECT dpe.at_utc, dpe.is_online
            FROM driver_presence_events dpe, bounds b
            WHERE dpe.driver_id = b.driver_id
              AND dpe.at_utc >= b.win_start
              AND dpe.at_utc <  b.win_end
        ),
        start_state AS (
            -- pencere başlamadan önceki son event => start anındaki state
            SELECT b.win_start AS at_utc,
                   COALESCE((
                     SELECT dpe.is_online
                     FROM driver_presence_events dpe
                     WHERE dpe.driver_id = b.driver_id
                       AND dpe.at_utc < b.win_start
                     ORDER BY dpe.at_utc DESC
                     LIMIT 1
                   ), FALSE) AS is_online
            FROM bounds b
        ),
        end_cap AS (
            -- pencere sonuna sentinel (offline)
            SELECT b.win_end AS at_utc, FALSE AS is_online
            FROM bounds b
        ),
        timeline AS (
            SELECT * FROM base_events
            UNION ALL
            SELECT * FROM start_state
            UNION ALL
            SELECT * FROM end_cap
        ),
        ordered AS (
            SELECT
                at_utc,
                is_online,
                LEAD(at_utc) OVER (ORDER BY at_utc) AS next_at
            FROM timeline
        )
        SELECT
            COALESCE(
              SUM(
                CASE WHEN is_online AND next_at IS NOT NULL
                     THEN EXTRACT(EPOCH FROM (next_at - at_utc))
                     ELSE 0 END
              ), 0
            )::bigint AS online_seconds
        FROM ordered;
    """, driver_id, start_date, sub["end_date"])

    online_seconds = int(row["online_seconds"])
    consumed_hours = online_seconds / 3600.0
    remaining_hours = max(0.0, total_quota_hours - consumed_hours)

    return {
        "success": True,
        "message": "Remaining work hours calculated", 
        "data": {
            "subscription_id": str(sub["subscription_id"]),
            "package_id": str(sub["package_id"]),
            "window_start": start_date.isoformat(),
            "window_end": sub["end_date"].isoformat(),
            "total_quota_hours": round(total_quota_hours, 3),
            "consumed_hours": round(consumed_hours, 3),
            "remaining_hours": round(remaining_hours, 3),
        }
    }
# === GET BANNERS ===
async def get_banners():
    query = """
        SELECT title, image_url
        FROM banners
        WHERE active = TRUE
        ORDER BY priority DESC;
    """
    rows = await fetch_all(query)
    return [dict(r) for r in rows] if rows else []
