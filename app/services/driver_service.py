from app.utils.database_async import fetch_one, fetch_all, execute


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


# === SET ONLINE STATUS ===
async def set_online(driver_id: str, online: bool):
    if online:
        query = """
            INSERT INTO driver_status (driver_id, online)
            VALUES ($1, TRUE)
            ON CONFLICT (driver_id) DO UPDATE
            SET online=TRUE, updated_at=NOW();
        """
        await execute(query, driver_id)
    else:
        query = "UPDATE driver_status SET online=FALSE, updated_at=NOW() WHERE driver_id=$1;"
        await execute(query, driver_id)


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
