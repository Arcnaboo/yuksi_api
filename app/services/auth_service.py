from ..utils.database import db_cursor
from ..utils.security import hash_pwd, verify_pwd, create_jwt
import os
import base64
from datetime import timedelta, datetime

def _generate_refresh_token() -> str:
    return base64.b64encode(os.urandom(32)).decode("utf-8")

REFRESH_TOKEN_TTL_DAYS = 7

def _refresh_expires_at() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_TOKEN_TTL_DAYS)

def _store_refresh_token(user_id: str | int, user_type: str, token: str, expires_at: datetime):
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO refresh_tokens (user_id, user_type, token, expires_at)
            VALUES (%s, %s, %s, %s)
            """,
            (str(user_id), user_type.lower(), token, expires_at),
        )

def _revoke_refresh_token(token: str):
    with db_cursor() as cur:
        cur.execute(
            """
            UPDATE refresh_tokens
               SET revoked_at = NOW()
             WHERE token = %s AND revoked_at IS NULL
            """,
            (token,),
        )

def _get_valid_refresh_row(token: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(
            """
            SELECT user_id, user_type, token, expires_at, revoked_at
              FROM refresh_tokens
             WHERE token = %s
               AND revoked_at IS NULL
               AND expires_at > NOW()
            """,
            (token,),
        )
        return cur.fetchone()

def _generate_tokens_net_style(user_id: int | str, email: str, roles: list[str], user_type: str):
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

def register(first_name: str, last_name:str, email: str, phone: str, password: str):
    with db_cursor() as cur:
        cur.execute("SELECT id FROM drivers WHERE email=%s OR phone=%s", (email, phone))
        if cur.fetchone():
            return None  
        hashed = hash_pwd(password)
        cur.execute(
            "INSERT INTO drivers (first_name,last_name,email,phone,password_hash) VALUES (%s,%s,%s,%s) RETURNING id",
            (first_name,last_name, email, phone, hashed),
        )
        driver_id = cur.fetchone()[0]
        cur.execute("INSERT INTO driver_status (driver_id) VALUES (%s)", (driver_id,))
    tokens = _generate_tokens_net_style(
        user_id=driver_id,
        email=email,
        roles=["Courier"],
        user_type="courier",
    )
    return tokens

def login(email: str, password: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT id, email, password_hash FROM drivers WHERE email=%s", (email,))
        row = cur.fetchone()
        if row and verify_pwd(password, row["password_hash"]):
            tokens = _generate_tokens_net_style(
                user_id=row["id"],
                email=row["email"],
                roles=["Courier"],
                user_type="courier",
            )
            return tokens

    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT id, email, password_hash FROM restaurants WHERE email=%s", (email,))
        r = cur.fetchone()
        if r and verify_pwd(password, r["password_hash"]):
            tokens = _generate_tokens_net_style(
                user_id=r["id"],
                email=r["email"],
                roles=["Restaurant"],
                user_type="restaurant",
            )
            return tokens

    return None

def get_driver(driver_id: str):
    with db_cursor(dict_cursor=True) as cur:
        cur.execute("SELECT id,first_name,last_name,email,phone FROM drivers WHERE id=%s", (driver_id,))
        return cur.fetchone()

def refresh_with_token(refresh_token: str):
    row = _get_valid_refresh_row(refresh_token)
    if not row:
        return None

    user_id = row["user_id"]
    user_type = row["user_type"].lower()

    if user_type == "courier":
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("SELECT email FROM drivers WHERE id=%s", (user_id,))
            drv = cur.fetchone()
            if not drv:
                return None
            email = drv["email"]
            roles = ["Courier"]
    elif user_type == "restaurant":
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("SELECT email FROM restaurants WHERE id=%s", (user_id,))
            rst = cur.fetchone()
            if not rst:
                return None
            email = rst["email"]
            roles = ["Restaurant"]
    else:
        return None

    _revoke_refresh_token(refresh_token)
    tokens = _generate_tokens_net_style(
        user_id=user_id,
        email=email,
        roles=roles,
        user_type=user_type,
    )
    return tokens


def revoke_refresh_token(refresh_token: str) -> bool:
    row = _get_valid_refresh_row(refresh_token)
    if not row:
        return False
    _revoke_refresh_token(refresh_token)
    return True
