from typing import Any, Dict, Optional, Tuple
from ..utils.security import hash_pwd
import app.utils.database_async as db

async def register_admin(first_name: str, last_name: str,email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        count_query = "SELECT COUNT(*) FROM system_admins"
        count_row = await db.fetch_one(count_query)
        count_val = count_row.get("count") if isinstance(count_row, dict) else count_row[0]
        if (count_val or 0) > 0:
            return None, "Zaten admin kayıtlı."
        
        pwd_hash = hash_pwd(password)
        pwd_query = """
            INSERT INTO system_admins (first_name,last_name,email, password_hash)
            VALUES (%s, %s, %s,%s)
            RETURNING id, first_name,last_name,email, created_at;
        """
        pwd_row = await db.fetch_one(pwd_query, first_name, last_name, email.lower(), pwd_hash)
        if isinstance(pwd_row, dict):
            data = {
                "id": pwd_row["id"],
                "first_name": pwd_row["first_name"],
                "last_name": pwd_row["last_name"],
                "email": pwd_row["email"],
                "created_at": pwd_row["created_at"],
            }
        else:
            data = {
                "id": pwd_row[0],
                "first_name": pwd_row[1],
                "last_name": pwd_row[2],
                "email": pwd_row[3],
                "created_at": pwd_row[4],
            }
        return data, None
    except Exception as e:
        # DB unique hatası (singleton) dahil
        return None, str(e)
