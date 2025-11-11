import os
import base64
from datetime import timedelta, datetime
from typing import Optional, Dict, Any, Tuple
from app.utils.database_async import fetch_one, execute
from app.utils.security import hash_pwd, verify_pwd, create_jwt


REFRESH_TOKEN_TTL_DAYS = 7

USER_TYPE_MAP = {
    "Admin": "admin",
    "Courier": "courier",
    "Dealer": "dealer",
    "Restaurant": "restaurant",
}

# === Yardımcı Fonksiyonlar ===
def _generate_refresh_token() -> str:
    return base64.b64encode(os.urandom(32)).decode("utf-8")


def _refresh_expires_at() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)


async def _store_refresh_token(user_id: str | int, user_type: str, token: str, expires_at: datetime):
    query = """
        INSERT INTO refresh_tokens (user_id, user_type, token, expires_at)
        VALUES ($1, $2, $3, $4);
    """
    await execute(query, str(user_id), user_type.lower(), token, expires_at)


async def _revoke_refresh_token(token: str):
    query = """
        UPDATE refresh_tokens
        SET revoked_at = NOW()
        WHERE token = $1 AND revoked_at IS NULL;
    """
    await execute(query, token)


async def _get_valid_refresh_row(token: str) -> Optional[Dict[str, Any]]:
    query = """
        SELECT user_id, user_type, token, expires_at, revoked_at
        FROM refresh_tokens
        WHERE token = $1
          AND revoked_at IS NULL
          AND expires_at > NOW();
    """
    return await fetch_one(query, token)


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
    await _store_refresh_token(
        user_id=user_id,
        user_type=user_type,
        token=refresh_token,
        expires_at=_refresh_expires_at(),
    )
    return {"accessToken": access_token, "refreshToken": refresh_token}


# === REGISTER ===
async def register(first_name: str, last_name: str, email: str, phone: str, password: str):
    existing = await fetch_one(
        "SELECT id FROM drivers WHERE email=$1 OR phone=$2;", email, phone
    )
    if existing:
        return None

    hashed = hash_pwd(password)
    row = await fetch_one(
        """
        INSERT INTO drivers (first_name, last_name, email, phone, password_hash)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
        """,
        first_name, last_name, email, phone, hashed
    )
    driver_id = row["id"]

    await execute("INSERT INTO driver_status (driver_id) VALUES ($1);", driver_id)

    return await _generate_tokens_net_style(
        user_id=driver_id,
        email=email,
        roles=["Courier"],
        user_type="courier",
    )


# === LOGIN ===
async def login(email: str, password: str):
    row = await fetch_one(
        """
        SELECT 
            u.id,
            u.email,
            u.password_hash,
            r.name AS role_name
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE u.email = $1
        """,
        email
    )

    if not row:
        return None

    if not verify_pwd(password, row["password_hash"]):
        return None

    # Role mapping
    role = row["role_name"]  # 'Admin', 'Driver', 'Bayi', 'Restoran'

    user_type = USER_TYPE_MAP.get(role)

    return await _generate_tokens_net_style(
        user_id=row["id"],
        email=row["email"],
        roles=[role],
        user_type=user_type,
    )

# === GET DRIVER ===
async def get_driver(driver_id: str):
    return await fetch_one(
        "SELECT id, first_name, last_name, email, phone FROM drivers WHERE id=$1;",
        driver_id,
    )


# === REFRESH TOKENS ===
async def refresh_with_token(refresh_token: str):
    row = await _get_valid_refresh_row(refresh_token)
    if not row:
        return None

    user_id = row["user_id"]
    user_type = row["user_type"].lower()
    
    usr = await fetch_one("SELECT email FROM users WHERE id=$1;", user_id)
    if not usr:
        return None
    email = usr["email"]
    roles =  [USER_TYPE_MAP.get(user_type)]

    await _revoke_refresh_token(refresh_token)
    return await _generate_tokens_net_style(user_id, email, roles, user_type)


# === REVOKE REFRESH TOKEN ===
async def revoke_refresh_token(refresh_token: str) -> bool:
    row = await _get_valid_refresh_row(refresh_token)
    if not row:
        return False
    await _revoke_refresh_token(refresh_token)
    return True