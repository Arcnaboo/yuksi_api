from typing import Any, Dict, Optional, Tuple
from ..utils.security import hash_pwd
import app.utils.database_async as db

async def register_admin(first_name: str, last_name: str, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Yeni admin kaydı oluşturur."""
    try:
        pwd_hash = hash_pwd(password)

        # Admin rolünün id'sini al
        role_query = "SELECT id FROM roles WHERE name = 'Admin';"
        role_row = await db.fetch_one(role_query)
        if not role_row:
            return None, "Admin rolü bulunamadı."

        role_id = role_row["id"] if isinstance(role_row, dict) else role_row[0]

        # User ekle
        query = """
            INSERT INTO users (role_id, first_name, last_name, email, password_hash)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, role_id, first_name, last_name, email, created_at, updated_at;
        """

        row = await db.fetch_one(
            query,
            role_id,
            first_name,
            last_name,
            email.lower(),
            pwd_hash
        )

        data = dict(row)

        return data, None

    except Exception as e:
        return None, str(e)