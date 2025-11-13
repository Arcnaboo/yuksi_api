from typing import Any, Dict, Optional, Tuple
from ..utils.security import hash_pwd
import app.utils.database_async as db

async def register_admin(first_name: str, last_name: str, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Yeni admin kaydı oluşturur (birden fazla admin eklenebilir)"""
    try:
        pwd_hash = hash_pwd(password)

        query = """
            INSERT INTO system_admins (first_name, last_name, email, password_hash)
            VALUES ($1, $2, $3, $4)
            RETURNING id, first_name, last_name, email, created_at;
        """
        row = await db.fetch_one(query, first_name, last_name, email.lower(), pwd_hash)

        if isinstance(row, dict):
            data = {
                "id": row["id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "created_at": row["created_at"],
            }
        else:
            data = {
                "id": row[0],
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "created_at": row[4],
            }

        return data, None

    except Exception as e:
        return None, str(e)
