from typing import Any, Dict, Optional, Tuple
from datetime import datetime
from ..utils.security import hash_pwd
import hashlib
from app.utils.database import db_cursor



async def register_admin(first_name: str, last_name: str,email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with db_cursor() as cur:
            # zaten var mı? (singleton kolonu sayesinde DB de engeller, ama biz de kontrol ediyoruz)
            cur.execute("SELECT COUNT(*) FROM system_admins;")
            count_row = cur.fetchone()
            count_val = count_row.get("count") if isinstance(count_row, dict) else count_row[0]
            if (count_val or 0) > 0:
                return None, "Zaten admin kayıtlı."

            pwd_hash = hash_pwd(password)
            cur.execute(
                """
                INSERT INTO system_admins (first_name,last_name,email, password_hash)
                VALUES (%s, %s, %s,%s)
                RETURNING id, first_name,last_name,email, created_at;
                """,
                (first_name,last_name, email.lower(), pwd_hash)
            )
            row = cur.fetchone()
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
                    "first_name":row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "created_at": row[4],
                }
            return data, None
    except Exception as e:
        # DB unique hatası (singleton) dahil
        return None, str(e)
