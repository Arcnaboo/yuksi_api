from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
import json

from fastapi import HTTPException, status   
from app.models.courier_model import CourierHistoryRes, CourierHistory
from app.models.order_model import OrderStatus
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
    exists = await fetch_one("SELECT 1 FROM drivers WHERE id=$1::uuid", driver_id)
    if not exists:
        return "User not found"
    
    # working_type kontrolü: 0=Taşıyıcı, 1=Kurye
    if working_type not in [0, 1]:
        return "Invalid workingType. Must be 0 (carrier) or 1 (courier)"
    
    # user_type belirleme
    user_type = 'carrier' if working_type == 0 else 'courier'

    # Step 1'de zaten kayıt var, sadece UPDATE yap
    result = await execute(
        """UPDATE driver_onboarding 
           SET working_type=$1, 
               user_type=$2,
               step=2
           WHERE driver_id=$3::uuid;""",
        working_type, user_type, driver_id
    )
    
    # Eğer hiçbir satır güncellenmediyse (Step 1'de kayıt oluşturulmamışsa), INSERT yap
    if result == "UPDATE 0":
        await execute(
            """INSERT INTO driver_onboarding (driver_id, step, working_type, user_type)
               VALUES ($1::uuid, 2, $2, $3);""",
            driver_id, working_type, user_type
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
    documents: Optional[List[Dict[str, Any]]] = None,
    # Taşıyıcı için ek alanlar
    username: Optional[str] = None,
    support_reference: Optional[str] = None,
    company_name: Optional[str] = None,
    company_address: Optional[str] = None,
    company_number: Optional[str] = None,
    city_id: Optional[int] = None,
    full_address: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    plate: Optional[str] = None,
    vehicle_features: Optional[List[str]] = None
) -> Optional[str]:
    exists = await fetch_one("SELECT 1 FROM drivers WHERE id=$1::uuid", driver_id)
    if not exists:
        return "User not found"
    
    # user_type kontrolü
    onboarding = await fetch_one("SELECT user_type, step FROM driver_onboarding WHERE driver_id=$1::uuid", driver_id)
    if not onboarding:
        return "User onboarding not found. Please complete step 2 first."
    
    # asyncpg Record objesini dict'e çevir
    onboarding_dict = dict(onboarding) if not isinstance(onboarding, dict) else onboarding
    user_type = onboarding_dict.get("user_type")
    step = onboarding_dict.get("step")
    
    # Step 2 kontrolü - step değeri integer olarak kontrol et
    if step is None or (isinstance(step, (int, float)) and int(step) != 2):
        return f"Please complete step 2 first. Current step: {step}, user_type: {user_type}"
    
    # user_type kontrolü
    if not user_type or user_type not in ['courier', 'carrier']:
        return f"Invalid user_type. Please complete step 2 first. Current user_type: {user_type}, step: {step}"
    
    # Kurye için dealer kontrolü
    if user_type == 'courier' and dealer_id is not None:
        dealer_exists = await fetch_one("SELECT 1 FROM dealers WHERE id=$1", str(dealer_id))
        if not dealer_exists:
            return "Dealer not found"
    
    # Taşıyıcı için dealer_id olmamalı
    if user_type == 'carrier' and dealer_id is not None:
        return "Dealer ID should not be provided for carriers"
    
    # Taşıyıcı için zorunlu alan kontrolü
    if user_type == 'carrier':
        required_fields = {
            'username': username,
            'support_reference': support_reference,
            'company_name': company_name,
            'company_address': company_address,
            'company_number': company_number,
            'city_id': city_id,
            'full_address': full_address,
            'vehicle_make': vehicle_make,
            'vehicle_model': vehicle_model,
            'plate': plate
        }
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            return f"Missing required fields for carrier: {', '.join(missing)}"
        
        # AdliSicil belgesi kontrolü
        if documents:
            has_adli_sicil = any(
                (doc.get("docType") if isinstance(doc, dict) else getattr(doc, "docType", None)) == "AdliSicil"
                for doc in documents
            )
            if not has_adli_sicil:
                return "AdliSicil document is required for carriers"
    
    # driver_onboarding güncelleme
    await execute(
        """
        INSERT INTO driver_onboarding
            (driver_id, vehicle_type, vehicle_capacity, state_id, dealer_id, vehicle_year, step, city_id, full_address)
        VALUES
            ($1::uuid, $2, $3, $4, $5::uuid, $6, 3, $7, $8)
        ON CONFLICT (driver_id) DO UPDATE SET
            vehicle_type      = EXCLUDED.vehicle_type,
            vehicle_capacity  = EXCLUDED.vehicle_capacity,
            state_id          = EXCLUDED.state_id,
            dealer_id         = EXCLUDED.dealer_id,
            vehicle_year      = EXCLUDED.vehicle_year,
            city_id           = EXCLUDED.city_id,
            full_address      = EXCLUDED.full_address,
            step              = 3;
        """,
        driver_id, vehicle_type, vehicle_capacity, state_id, dealer_id, vehicle_year, city_id, full_address
    )
    
    # Taşıyıcı için drivers tablosuna ek bilgiler
    if user_type == 'carrier':
        await execute(
            """
            UPDATE drivers SET
                username = $1,
                customer_service_reference = $2,
                company_name = $3,
                company_address = $4,
                company_number = $5,
                city_id = $6
            WHERE id = $7::uuid;
            """,
            username, support_reference, company_name, company_address, company_number, city_id, driver_id
        )
        
        # Vehicles tablosuna araç bilgileri
        vehicle_details_json = {}
        if vehicle_features:
            vehicle_details_json = {"features": vehicle_features}
        
        await execute(
            """
            INSERT INTO vehicles (driver_id, make, model, year, plate, vehicle_details)
            VALUES ($1::uuid, $2, $3, $4, $5, $6::jsonb)
            ON CONFLICT (plate) DO UPDATE SET
                make = EXCLUDED.make,
                model = EXCLUDED.model,
                year = EXCLUDED.year,
                vehicle_details = EXCLUDED.vehicle_details;
            """,
            driver_id, vehicle_make, vehicle_model, vehicle_year, plate, json.dumps(vehicle_details_json)
        )

    # Belgeler işleme
    if not documents:
        return None

    allowed_types = {
        "VergiLevhasi", "EhliyetOn", "EhliyetArka", "RuhsatOn",
        "RuhsatArka", "KimlikOn", "KimlikArka", "SRC", "Psikoteknik",
        "KBelgesi", "P1Belgesi", "AdliSicil"
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
async def list_couriers(dealer_id: UUID = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
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
      ob.dealer_id,
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
    if dealer_id is not None:
        result = []
        for r in rows:
            row = dict(r)
            row_dealer = row.get("dealer_id")

            if row_dealer is None:
                continue
            
            if str(row_dealer) == str(dealer_id):
                result.append(row)
        print(result)
        return result
    else:
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

async def get_courier_documents(driver_id: str, dealer_id: UUID = None) -> Optional[List[Dict[str, Any]]]:

    driver_check_sql = "SELECT 1 FROM drivers WHERE id = $1"
    driver = await fetch_one(driver_check_sql, driver_id)
    if driver is None:
        return None
    
    if dealer_id:
        onboarding_sql = """
            SELECT 1
            FROM driver_onboarding
            WHERE driver_id = $1
              AND dealer_id = $2
        """
        onboarding_match = await fetch_one(onboarding_sql, driver_id, dealer_id)
        if onboarding_match is None:
            return None

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
        ORDER BY f.uploaded_at DESC
    """

    documents = await fetch_all(sql, driver_id)
    return [dict(doc) for doc in documents] if documents else []


async def update_courier_document_status(
    driver_id: str,
    document_id: str,
    status: str,
    dealer_id: UUID = None
) -> Optional[str]:

    if status not in VALID_STATUSES:
        return "Invalid status value"

    # Check if driver exists
    driver_check_sql = "SELECT 1 FROM drivers WHERE id = $1"
    driver = await fetch_one(driver_check_sql, driver_id)
    if driver is None:
        return "Driver not found"

    # If dealer_id is provided, check if driver belongs to that dealer
    if dealer_id:
        onboarding_sql = """
            SELECT 1
            FROM driver_onboarding
            WHERE driver_id = $1
              AND dealer_id = $2
        """
        onboarding_match = await fetch_one(onboarding_sql, driver_id, dealer_id)
        if onboarding_match is None:
            return "Driver is not assigned to this dealer"

    # Check if document exists for this driver
    document_check_sql = "SELECT 1 FROM courier_documents WHERE user_id = $1 AND id = $2"
    document = await fetch_one(document_check_sql, driver_id, document_id)
    if document is None:
        return "Document not found for this driver"

    # Update document status
    update_sql = """
    UPDATE courier_documents
    SET courier_document_status = $1
    WHERE user_id = $2 AND id = $3
    """
    await execute(update_sql, status, driver_id, document_id)

    # Check if all documents approved
    all_ok_sql = """
    SELECT (COUNT(*) > 0) AND bool_and(courier_document_status = 'onaylandi') AS all_approved
    FROM courier_documents
    WHERE user_id = $1
    """
    row = await fetch_one(all_ok_sql, driver_id)
    all_approved = bool(row["all_approved"]) if row is not None else False

    # Update driver's active state
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

    # Drivers tablosunu güncelle
    driver_sets = []
    driver_params = []
    i = 1

    if first_name is not None:
        driver_sets.append(f"first_name = ${i}"); driver_params.append(first_name.strip()); i += 1
    if last_name is not None:
        driver_sets.append(f"last_name  = ${i}"); driver_params.append(last_name.strip());  i += 1
    if email is not None:
        driver_sets.append(f"email      = ${i}"); driver_params.append(email.strip().lower()); i += 1
    if phone is not None:
        driver_sets.append(f"phone      = ${i}"); driver_params.append(phone.strip()); i += 1

    # Drivers tablosunda güncellenecek alan varsa güncelle
    if driver_sets:
        driver_sql = f"""
        UPDATE drivers
        SET {', '.join(driver_sets)}
        WHERE id = ${i}::uuid
        """
        driver_params.append(driver_id)
        await execute(driver_sql, *driver_params)

    # Country_id varsa driver_onboarding tablosunu güncelle
    if country_id is not None:
        await execute(
            """INSERT INTO driver_onboarding (driver_id, country_id)
               VALUES ($1::uuid, $2)
               ON CONFLICT (driver_id) DO UPDATE
                 SET country_id = EXCLUDED.country_id;""",
            driver_id, country_id
        )

    # Hiçbir alan güncellenmediyse
    if not driver_sets and country_id is None:
        return None

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

# TODO : ödemeler eklendikten sonra ödeme durumu da eklenecek

async def get_courier_history(
    courier_id: UUID,
    date: Optional[str] = None,
    page: int = 1,
    page_size: int = 25
) -> List[CourierHistory] | Any:

    offset = (page - 1) * page_size
    params = [courier_id]

    # Her durumda default boş filtre
    date_filter = ""

    # Tarih geldiyse filtre eklenir
    if date:
        try:
            time = datetime.strptime(date, "%Y-%m-%d").date()
            date_filter = "AND DATE(o.updated_at) = $2"
            params.append(time)
        except ValueError:
            return CourierHistoryRes(
                success=False,
                message="Invalid date format. Use YYYY-MM-DD.",
                data=[]
            )

    # === HISTORY QUERY ===
    history_sql = f"""
    SELECT
      o.id,
      o.amount AS price,
      o.updated_at AS date,
      o.status,
      o.address AS from_address,
      o.delivery_address AS to_address
    FROM orders o
    WHERE o.courier_id = $1
      AND o.status IN ('iptal', 'teslim_edildi')
      {date_filter}
    ORDER BY o.updated_at DESC
    LIMIT ${len(params)+1} OFFSET ${len(params)+2};
    """

    # Page params eklenir
    params.extend([page_size, offset])

    rows = await fetch_all(history_sql, *params)

    result = [
        CourierHistory(
            order_id=r["id"],
            price=float(r["price"]),
            date=r["date"].strftime("%Y-%m-%d %H:%M:%S") if r["date"] else None,
            status=r["status"],
            payment_status="N/A",
            from_address=r["from_address"],
            to_address=r["to_address"]
        )
    for r in rows] if rows else []

    return CourierHistoryRes(
        success=True,
        message="Courier history fetched",
        data=result
    )

async def change_courier_order_status(
    courier_id: UUID,
    order_id: UUID,
    new_status: OrderStatus
) -> Optional[str]:
    order = await fetch_one(
        "SELECT status FROM orders WHERE id = $1 AND courier_id = $2",
        order_id, courier_id
    )
    if order is None:
        return "Kuryeye bağlı sipariş bulunamadı."
    elif order["status"] in [OrderStatus.IPTAL, OrderStatus.TESLIM_EDILDI]:
        return "Bu siparişin durumu kurye tarafından değiştirilemez."
    elif order["status"] == new_status:
        return "Sipariş zaten bu durumda."
    elif not [OrderStatus.KURYEYE_VERILDI, OrderStatus.YOLDA, OrderStatus.TESLIM_EDILDI].__contains__(new_status):
        return "Geçersiz veya yetkisiz sipariş durumu."

    await execute(
        "UPDATE orders SET status = $1, updated_at = NOW() WHERE id = $2",
        new_status, order_id
    )
    return None