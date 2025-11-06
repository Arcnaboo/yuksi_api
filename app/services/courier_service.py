from typing import Optional, Tuple, Dict, Any, List
from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.security import hash_pwd
from ..utils.database import db_cursor
from ..utils.database_async import fetch_all,fetch_one,execute
from ..utils.security import hash_pwd
from uuid import UUID

VALID_STATUSES = {
    "evrak_bekleniyor",
    "inceleme_bekleniyor",
    "eksik_belge",
    "reddedildi",
    "onaylandi",
}



# === STEP 1 ===
async def courier_register_step1(
    phone: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    country_id: int,
    confirm_contract: bool
) -> Tuple[Optional[str], Optional[str]]:
    first_name, last_name = first_name.strip(), last_name.strip()
    full_name = f"{first_name} {last_name}".strip()

    # Email veya telefon kayıtlı mı?
    exists = await fetch_one("SELECT id FROM drivers WHERE email=$1 OR phone=$2", email, phone)
    if exists:
        return None, "Email or phone already registered"

    pwd_hash = hash_pwd(password)
    row = await fetch_one(
        "INSERT INTO drivers (first_name,last_name,email,phone,password_hash) "
        "VALUES ($1,$2,$3,$4,$5) RETURNING id;",
        first_name, last_name, email, phone, pwd_hash
    )
    driver_id = row["id"]

    await execute("INSERT INTO driver_status (driver_id) VALUES ($1) ON CONFLICT DO NOTHING;", driver_id)

    await execute(
        """INSERT INTO driver_onboarding (driver_id, contract_confirmed, country_id, step)
           VALUES ($1, $2, $3, 1)
           ON CONFLICT (driver_id) DO UPDATE
             SET contract_confirmed=EXCLUDED.contract_confirmed,
                 country_id=EXCLUDED.country_id,
                 step=1;""",
        driver_id, confirm_contract, country_id
    )

    return str(driver_id), None


# === STEP 2 ===
async def courier_register_step2(driver_id: str, working_type: int) -> Optional[str]:
    exists = await fetch_one("SELECT 1 FROM drivers WHERE id=$1", driver_id)
    if not exists:
        return "User not found"

    await execute(
        """INSERT INTO driver_onboarding (driver_id, step, working_type)
           VALUES ($1, 2, $2)
           ON CONFLICT (driver_id) DO UPDATE
             SET working_type=EXCLUDED.working_type, step=2;""",
        driver_id, working_type
    )
    return None


# === STEP 3 ===
async def courier_register_step3(
    driver_id: str,
    vehicle_type: int,
    vehicle_capacity: int,
    state_id: int,
    dealer_id: Optional[UUID],
    vehicle_year: int,
    documents: Optional[List[Dict[str, Any]]] = None
) -> Optional[str]:
    exists = await fetch_one("SELECT 1 FROM drivers WHERE id=$1", driver_id)
    if not exists:
        return "User not found"

    if dealer_id is not None:
        dealer_exists = await fetch_one("SELECT 1 FROM dealers WHERE id=$1", str(dealer_id))
        if not dealer_exists:
            return "Dealer not found"
        
    
    await execute(
        """
        INSERT INTO driver_onboarding
            (driver_id, vehicle_type, vehicle_capacity, state_id, dealer_id, vehicle_year, step)
        VALUES
            ($1::uuid, $2, $3, $4, $5::uuid, $6, 3)
        ON CONFLICT (driver_id) DO UPDATE SET
            vehicle_type      = EXCLUDED.vehicle_type,
            vehicle_capacity  = EXCLUDED.vehicle_capacity,
            state_id          = EXCLUDED.state_id,
            dealer_id         = EXCLUDED.dealer_id,
            vehicle_year      = EXCLUDED.vehicle_year,
            step              = 3;
        """,
        driver_id, vehicle_type, vehicle_capacity, state_id, dealer_id, vehicle_year
    )

    if not documents:
        return None

    allowed_types = {
        "VergiLevhasi", "EhliyetOn", "EhliyetArka", "RuhsatOn",
        "RuhsatArka", "KimlikOn", "KimlikArka"
    }

    for doc in documents:
        doc_type = doc.get("docType") if isinstance(doc, dict) else getattr(doc, "docType", None)
        file_id = doc.get("fileId") if isinstance(doc, dict) else getattr(doc, "fileId", None)
        if not doc_type or not file_id:
            return "Invalid document payload"
        if doc_type not in allowed_types:
            return f"Invalid docType: {doc_type}"

        file_id_str = str(file_id)
        driver_id_str = str(driver_id)

        valid = await fetch_one(
            "SELECT 1 FROM files WHERE id=$1 AND user_id=$2 AND is_deleted=FALSE;",
            file_id_str, driver_id_str
        )
        if not valid:
            return f"Invalid fileId for user: {file_id}"

        await execute(
            """INSERT INTO courier_documents (user_id, file_id, doc_type)
               VALUES ($1, $2, $3)
               ON CONFLICT (user_id, doc_type)
               DO UPDATE SET file_id = EXCLUDED.file_id;""",
            driver_id_str, file_id_str, doc_type
        )

    return None


# === GET ONBOARDING ===
async def get_onboarding(driver_id: str) -> Optional[Dict[str, Any]]:
    row = await fetch_one("SELECT * FROM driver_onboarding WHERE driver_id=$1", driver_id)
    return dict(row) if row else None


# === LIST COURIERS ===
async def list_couriers(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    sql = """
    SELECT
      d.id,
      d.first_name,
      d.last_name,
      d.email,
      d.phone,
      d.created_at,
      d.is_active,
      d.deleted,
      d.deleted_at,
      ob.country_id,
      COALESCE(ds.online, FALSE) AS is_online,
      c.name   AS country_name,
      ob.state_id,
      s.name   AS state_name,
      ob.working_type,
      ob.vehicle_type,
      ob.vehicle_capacity,
      ob.vehicle_year,
      ob.step
    FROM drivers d
    LEFT JOIN driver_onboarding ob ON ob.driver_id = d.id
    LEFT JOIN countries c ON c.id = ob.country_id
    LEFT JOIN states s ON s.id = ob.state_id
    LEFT JOIN driver_status ds ON ds.driver_id = d.id
    ORDER BY d.created_at DESC
    LIMIT $1 OFFSET $2;
    """
    rows = await fetch_all(sql, limit, offset)
    return [dict(r) for r in rows] if rows else []


# === GET COURIER ===
async def get_courier(driver_id: str) -> Optional[Dict[str, Any]]:
    sql = """
    SELECT
      d.id,
      d.first_name,
      d.last_name,
      d.email,
      d.phone,
      d.created_at,
      d.is_active,
      d.deleted,
      d.deleted_at,
      ob.country_id,
      c.name   AS country_name,
      ob.state_id,
      s.name   AS state_name,
      ob.working_type,
      ob.vehicle_type,
      ob.vehicle_capacity,
      ob.vehicle_year,
      ob.step
    FROM drivers d
    LEFT JOIN driver_onboarding ob ON ob.driver_id = d.id
    LEFT JOIN countries c ON c.id = ob.country_id
    LEFT JOIN states s ON s.id = ob.state_id
    WHERE d.id = $1;
    """
    row = await fetch_one(sql, driver_id)
    return dict(row) if row else None

async def get_courier_documents(driver_id: str) -> Optional[List[Dict[str, Any]]]:
    #check if driver exists
    driver_check_sql = "SELECT 1 FROM drivers WHERE id = $1"
    driver = await fetch_one(driver_check_sql, driver_id)
    if driver is None:
        return None #driver not found
    

    sql = """
    SELECT
        cd.id AS document_id,
      cd.doc_type,
      cd.file_id,
      cd.courier_document_status AS document_status,
      f.image_url AS image_url,
      f.uploaded_at
    FROM courier_documents cd
    JOIN files f ON f.id = cd.file_id
    WHERE cd.user_id = $1
    """
    documents = await fetch_all(sql, driver_id)
    
    return [dict(doc) for doc in documents]


async def update_courier_document_status(driver_id: str, document_id: str, status: str) -> Optional[str]:
    if status not in VALID_STATUSES:
        return "Invalid status value"
    #check if driver exists
    driver_check_sql = "SELECT 1 FROM drivers WHERE id = $1"
    driver = await fetch_one(driver_check_sql, driver_id)
    if driver is None:
        return "Driver not found"
    
    #check if document exists for this driver
    document_check_sql = "SELECT 1 FROM courier_documents WHERE user_id = $1 AND id = $2"
    document = await fetch_one(document_check_sql, driver_id, document_id)
    if document is None:
        return "Document not found for this driver"
    
    update_sql = """
    UPDATE courier_documents
    SET courier_document_status = $1
    WHERE user_id = $2 AND id = $3
    """
    await execute(update_sql, status, driver_id, document_id)
    
    all_ok_sql = """
    SELECT (COUNT(*) > 0) AND bool_and(courier_document_status = 'onaylandi') AS all_approved
    FROM courier_documents
    WHERE user_id = $1
    """
    row = await fetch_one(all_ok_sql, driver_id)
    all_approved = bool(row["all_approved"]) if row is not None else False
    if all_approved:
        await execute("UPDATE drivers SET is_active = TRUE WHERE id = $1", driver_id)
    else:
        await execute("UPDATE drivers SET is_active = FALSE WHERE id = $1", driver_id)

    

    return None

async def delete_courier_user(driver_id: UUID) -> Optional[str]:
    driver = await fetch_one("SELECT 1 FROM drivers WHERE id = $1", driver_id)
    if driver is None:
        return "Driver not found"

    await execute("""
        UPDATE drivers
        SET deleted = TRUE, deleted_at = NOW(), is_active = FALSE
        WHERE id = $1
    """, driver_id)

    return None


async def update_courier_profile(
    driver_id: str,
    first_name: Optional[str] = None,
    last_name:  Optional[str] = None,
    email:      Optional[str] = None,
    phone:      Optional[str] = None,
    country_id: Optional[int] = None,
) -> Optional[str]:
    exists = await fetch_one("SELECT 1 FROM drivers WHERE id = $1::uuid", driver_id)
    if exists is None:
        return "Kurye kullanıcısı bulunamadı"

    if email is not None:
        dup = await fetch_one(
            "SELECT 1 FROM drivers WHERE LOWER(email)=LOWER($1) AND id <> $2::uuid AND (deleted IS DISTINCT FROM TRUE)",
            email, driver_id
        )
        if dup:
            return "Bu email zaten kullanılıyor"
    if phone is not None:
        dup = await fetch_one(
            "SELECT 1 FROM drivers WHERE phone=$1 AND id <> $2::uuid AND (deleted IS DISTINCT FROM TRUE)",
            phone, driver_id
        )
        if dup:
            return "Bu telefon numarası zaten kullanılıyor"

    sets = []
    params = []
    i = 1

    if first_name is not None:
        sets.append(f"first_name = ${i}"); params.append(first_name.strip()); i += 1
    if last_name is not None:
        sets.append(f"last_name  = ${i}"); params.append(last_name.strip());  i += 1
    if email is not None:
        sets.append(f"email      = ${i}"); params.append(email.strip().lower()); i += 1
    if phone is not None:
        sets.append(f"phone      = ${i}"); params.append(phone.strip()); i += 1
    if country_id is not None:
        sets.append(f"country_id = ${i}"); params.append(country_id); i += 1

    if not sets:
        return None  

    sets.append("updated_at = NOW()")

    sql = f"""
    UPDATE drivers
    SET {', '.join(sets)}
    WHERE id = ${i}::uuid
    """
    params.append(driver_id)

    await execute(sql, *params)
    return None

async def get_dealers_by_state(state_id: int) -> List[Dict[str, Any]]:
    sql = """
    SELECT
      id,
      name,
      address,
      phone,
      email,
      state_id,
      created_at
    FROM dealers
    WHERE state_id = $1
    ORDER BY name ASC;
    """
    rows = await fetch_all(sql, state_id)
    return [dict(r) for r in rows] if rows else []