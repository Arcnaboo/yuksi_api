import app.utils.database_async as db
from ..utils.security import hash_pwd, verify_pwd, create_jwt
import os
import base64
from datetime import timedelta, datetime

def _generate_refresh_token() -> str:
    return base64.b64encode(os.urandom(32)).decode("utf-8")

REFRESH_TOKEN_TTL_DAYS = 7

def _refresh_expires_at() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)

async def _store_refresh_token(user_id: str | int, user_type: str, token: str, expires_at: datetime):
    query = """
        INSERT INTO refresh_tokens (user_id, user_type, token, expires_at)
        VALUES (%s, %s, %s, %s)
    """
    await db.execute(query, user_id, user_type.lower(), token, expires_at)

async def _revoke_refresh_token(token: str):
    query = """
        UPDATE refresh_tokens
        SET revoked_at = NOW()
        WHERE token = %s AND revoked_at IS NULL
    """
    await db.execute(token)

async def _get_valid_refresh_row(token: str):
    query = """
        SELECT user_id, user_type, token, expires_at, revoked_at
          FROM refresh_tokens
         WHERE token = $1
           AND revoked_at IS NULL
           AND expires_at > NOW()
    """
    return await db.fetch_one(query, token)

async def _generate_tokens_net_style(user_id: int | str, email: str, roles: list[str], user_type: str):
    claims = {
        "sub": str(user_id),
        "unique_name": email,
        "userId": str(user_id),
        "email": email,
        "userType": user_type.lower(),
        "role": roles,
    }
    access_token = create_jwt(claims)
    refresh_token = _generate_refresh_token()
    _store_refresh_token(user_id=user_id, user_type=user_type, token=refresh_token, expires_at=_refresh_expires_at())
    return {"accessToken": access_token, "refreshToken": refresh_token}

async def register(first_name: str, last_name: str, email: str, phone: str, password: str):
    query_check = "SELECT id FROM drivers WHERE email=$1 OR phone=$2"
    exists = await db.fetch_one(query_check, email, phone)
    if exists:
        return None

    hashed = hash_pwd(password)
    query_insert = """
        INSERT INTO drivers (first_name, last_name, email, phone, password_hash)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """
    row = await db.fetch_one(query_insert, first_name, last_name, email, phone, hashed)
    driver_id = row["id"]

    await db.execute("INSERT INTO driver_status (driver_id) VALUES ($1)", driver_id)

    tokens = await _generate_tokens_net_style(
        user_id=driver_id,
        email=email,
        roles=["Courier"],
        user_type="courier",
    )
    return tokens

async def login(email: str, password: str):
    # driver
    q_driver = "SELECT id, email, password_hash FROM drivers WHERE email=$1"
    drv = await db.fetch_one(q_driver, email)
    if drv and verify_pwd(password, drv["password_hash"]):
        return await _generate_tokens_net_style(drv["id"], drv["email"], ["Courier"], "courier")

    # restaurant
    q_rest = "SELECT id, email, password_hash FROM restaurants WHERE email=$1"
    rst = await db.fetch_one(q_rest, email)
    if rst and verify_pwd(password, rst["password_hash"]):
        return await _generate_tokens_net_style(rst["id"], rst["email"], ["Restaurant"], "restaurant")

    # admin
    q_admin = "SELECT id, email, password_hash FROM system_admins WHERE email=$1"
    adm = await db.fetch_one(q_admin, email)
    if adm and verify_pwd(password, adm["password_hash"]):
        return await _generate_tokens_net_style(adm["id"], adm["email"], ["Admin"], "admin")

    return None

async def get_driver(driver_id: str):
    query = "SELECT id, first_name, last_name, email, phone FROM drivers WHERE id=$1"
    return await db.fetch_one(query, driver_id)

async def refresh_with_token(refresh_token: str):
    row = await _get_valid_refresh_row(refresh_token)
    if not row:
        return None

    user_id = row["user_id"]
    user_type = row["user_type"].lower()

    if user_type == "courier":
        drv = await db.fetch_one("SELECT email FROM drivers WHERE id=$1", user_id)
        if not drv:
            return None
        email = drv["email"]
        roles = ["Courier"]
    elif user_type == "restaurant":
        rst = await db.fetch_one("SELECT email FROM restaurants WHERE id=$1", user_id)
        if not rst:
            return None
        email = rst["email"]
        roles = ["Restaurant"]
    else:
        return None

    await _revoke_refresh_token(refresh_token)
    return await _generate_tokens_net_style(user_id, email, roles, user_type)


def revoke_refresh_token(refresh_token: str) -> bool:
    row = _get_valid_refresh_row(refresh_token)
    if not row:
        return False
    _revoke_refresh_token(refresh_token)
    return True
