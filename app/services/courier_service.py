from typing import Optional, Tuple, Dict, Any, List
from ..utils.database import db_cursor
from ..utils.security import hash_pwd

def courier_register_step1(
    phone: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    country_id: int,
    confirm_contract: bool
) -> Tuple[Optional[str], Optional[str]]:
    full_name = f"{first_name.strip()} {last_name.strip()}".strip()
    first_name = first_name.strip()
    last_name = last_name.strip()
    with db_cursor() as cur:
        cur.execute("SELECT id FROM drivers WHERE email=%s OR phone=%s", (email, phone))
        if cur.fetchone():
            return None, "Email or phone already registered"

        pwd_hash = hash_pwd(password)
        cur.execute(
            "INSERT INTO drivers (first_name,last_name,email,phone,password_hash) VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (first_name,last_name, email, phone, pwd_hash),
        )
        driver_id = cur.fetchone()[0]

        cur.execute("INSERT INTO driver_status (driver_id) VALUES (%s) ON CONFLICT DO NOTHING", (driver_id,))

        cur.execute(
            """INSERT INTO driver_onboarding (driver_id, contract_confirmed, country_id, step)
               VALUES (%s, %s, %s, 1)
               ON CONFLICT (driver_id) DO UPDATE SET contract_confirmed=EXCLUDED.contract_confirmed,
                                                    country_id=EXCLUDED.country_id,
                                                    step=1""",
            (driver_id, confirm_contract, country_id),
        )

    return str(driver_id), None

def courier_register_step2(driver_id: str, working_type: int) -> Optional[str]:
    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM drivers WHERE id=%s", (driver_id,))
        if not cur.fetchone():
            return "User not found"

        cur.execute(
            """INSERT INTO driver_onboarding (driver_id, step, working_type)
               VALUES (%s, 2, %s)
               ON CONFLICT (driver_id) DO UPDATE SET working_type=EXCLUDED.working_type, step=2""",
            (driver_id, working_type),
        )
    return None

def courier_register_step3(
    driver_id: str,
    vehicle_type: int,
    vehicle_capacity: int,
    state_id: int,
    vehicle_year: int,
) -> Optional[str]:
    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM drivers WHERE id=%s", (driver_id,))
        if not cur.fetchone():
            return "User not found"

        cur.execute(
            """INSERT INTO driver_onboarding (driver_id, vehicle_type, vehicle_capacity, state_id, vehicle_year, step)
               VALUES (%s, %s, %s, %s, %s, 3)
               ON CONFLICT (driver_id) DO UPDATE SET
                 vehicle_type=EXCLUDED.vehicle_type,
                 vehicle_capacity=EXCLUDED.vehicle_capacity,
                 state_id=EXCLUDED.state_id,
                 vehicle_year=EXCLUDED.vehicle_year,
                 step=3""",
            (driver_id, vehicle_type, vehicle_capacity, state_id, vehicle_year),
        )
    return None

def get_onboarding(driver_id: str) -> Optional[Dict[str, Any]]:
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT * FROM driver_onboarding WHERE driver_id=%s", (driver_id,))
        return cur.fetchone()


def list_couriers(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    sql = """
    SELECT
      d.id,
      d.first_name,
      d.last_name,
      d.email,
      d.phone,
      d.created_at,
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
    LEFT JOIN countries c          ON c.id = ob.country_id
    LEFT JOIN states s             ON s.id = ob.state_id
    ORDER BY d.created_at DESC
    LIMIT %s OFFSET %s
    """
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (limit, offset))
        return cur.fetchall() or []

def get_courier(driver_id: str) -> Dict[str, Any] | None:
    sql = """
    SELECT
      d.id,
      d.firs_tname,
      d.last_name,
      d.email,
      d.phone,
      d.created_at,
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
    LEFT JOIN countries c          ON c.id = ob.country_id
    LEFT JOIN states s             ON s.id = ob.state_id
    WHERE d.id = %s
    """
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (driver_id,))
        return cur.fetchone()