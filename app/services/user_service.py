from typing import Optional, Dict, Any
from app.utils.database_async import fetch_one, execute
from app.utils.security import hash_pwd, verify_pwd
from app.services.auth_service import _generate_tokens_net_style


async def register_user(
    email: str,
    password: str,
    phone: str,
    first_name: str,
    last_name: str
) -> Optional[Dict[str, Any]]:
    """
    User kaydı yapar.
    Default role: 'Default'
    """
    # Email kontrolü
    existing = await fetch_one(
        "SELECT id FROM users WHERE email=$1;", email
    )
    if existing:
        return None

    # Default role'ü al
    role = await fetch_one(
        "SELECT id FROM roles WHERE name='Default';"
    )
    if not role:
        return None  # Default role yoksa hata

    role_id = role["id"]

    # Password hashle
    password_hash = hash_pwd(password)

    # User oluştur
    user_row = await fetch_one(
        """
        INSERT INTO users (role_id, email, password_hash, phone, first_name, last_name)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, email, role_id;
        """,
        role_id, email, password_hash, phone, first_name, last_name
    )

    if not user_row:
        return None

    user_id = user_row["id"]
    user_email = user_row["email"]

    # Token oluştur
    return await _generate_tokens_net_style(
        user_id=str(user_id),
        email=user_email,
        roles=["Default"],
        user_type="user",
    )


async def login_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    User login yapar.
    """
    # User'ı bul
    user = await fetch_one(
        """
        SELECT id, email, password_hash, is_active, deleted 
        FROM users 
        WHERE email=$1;
        """,
        email
    )

    if not user:
        return None

    # Silinmiş veya aktif değilse
    if user.get("deleted") or not user.get("is_active"):
        return "banned"

    # Password kontrolü
    if not verify_pwd(password, user["password_hash"]):
        return None

    # Token oluştur
    return await _generate_tokens_net_style(
        user_id=str(user["id"]),
        email=user["email"],
        roles=["Default"],
        user_type="user",
    )

