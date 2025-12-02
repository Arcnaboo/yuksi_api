from typing import Optional, Dict, Any, Tuple
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


async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Bireysel kullanıcı profil bilgilerini getirir"""
    try:
        row = await fetch_one(
            """
            SELECT 
                email, phone, first_name, last_name
            FROM users 
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE)
              AND is_active = TRUE;
            """,
            user_id
        )
        if not row:
            return None

        return {
            "email": row.get("email"),
            "phone": row.get("phone"),
            "firstName": row.get("first_name") or "",
            "lastName": row.get("last_name") or "",
        }
    except Exception as e:
        print(f"Error getting user profile: {e}")
        return None


async def update_user_profile(
    user_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Bireysel kullanıcı profil bilgilerini günceller"""
    try:
        update_fields = []
        params = []
        i = 1

        if email is not None:
            # Email unique kontrolü (sadece silinmemiş kayıtlar için)
            existing = await fetch_one(
                "SELECT id FROM users WHERE email = $1 AND id != $2 AND (deleted IS NULL OR deleted = FALSE);",
                email, user_id
            )
            if existing:
                return False, "Bu email adresi zaten kullanılıyor"
            update_fields.append(f"email = ${i}")
            params.append(email)
            i += 1
        if phone is not None:
            update_fields.append(f"phone = ${i}")
            params.append(phone)
            i += 1
        if first_name is not None:
            update_fields.append(f"first_name = ${i}")
            params.append(first_name)
            i += 1
        if last_name is not None:
            update_fields.append(f"last_name = ${i}")
            params.append(last_name)
            i += 1

        if not update_fields:
            return False, "Güncellenecek alan bulunamadı"

        # updated_at'i güncelle (parametre gerektirmez, SQL fonksiyonu)
        update_fields.append(f"updated_at = NOW()")

        query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = ${i}
              AND (deleted IS NULL OR deleted = FALSE)
              AND is_active = TRUE
            RETURNING id;
        """
        
        params.append(user_id)
        result = await fetch_one(query, *params)
        if not result:
            return False, "Kullanıcı bulunamadı veya güncellenemedi"

        return True, None
    except Exception as e:
        print(f"Error updating user profile: {e}")
        return False, str(e)

