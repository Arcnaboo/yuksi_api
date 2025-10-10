from ..utils.database import db_cursor
from ..utils.security import hash_pwd, verify_pwd, create_jwt

def register(first_name: str, last_name:str, email: str, phone: str, password: str):
    with db_cursor() as cur:
        cur.execute("SELECT id FROM drivers WHERE email=%s OR phone=%s", (email, phone))
        if cur.fetchone():
            return None  # already exists
        hashed = hash_pwd(password)
        cur.execute(
            "INSERT INTO drivers (first_name,last_name,email,phone,password_hash) VALUES (%s,%s,%s,%s) RETURNING id",
            (first_name,last_name, email, phone, hashed),
        )
        driver_id = cur.fetchone()[0]
        cur.execute("INSERT INTO driver_status (driver_id) VALUES (%s)", (driver_id,))
    token = create_jwt({"sub": str(driver_id)})
    return token

def login(email: str, password: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT id,password_hash FROM drivers WHERE email=%s", (email,))
        row = cur.fetchone()
        if not row or not verify_pwd(password, row["password_hash"]):
            return None
        token = create_jwt({"sub": str(row["id"])})
        return token

def get_driver(driver_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT id,first_name,last_name,email,phone FROM drivers WHERE id=%s", (driver_id,))
        return cur.fetchone()
