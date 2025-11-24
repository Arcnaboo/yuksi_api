from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.security import hash_pwd


async def create_corporate_user(data: Dict[str, Any]) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Admin tarafından Corporate kullanıcı oluşturur (Restoran gibi ayrı tablo)
    """
    try:
        # Email kontrolü
        existing = await fetch_one("SELECT id FROM corporate_users WHERE email = $1;", data["email"])
        if existing:
            return False, "Bu email adresi zaten kayıtlı"
        
        # Password hashle
        password_hash = hash_pwd(data["password"])
        
        # Corporate user oluştur (Restoran gibi direkt tabloya insert)
        commission_rate = data.get("commissionRate")
        country_id = data.get("countryId")
        state_id = data.get("stateId")
        city_id = data.get("cityId")
        row = await fetch_one("""
            INSERT INTO corporate_users (
                email, password_hash, 
                phone, first_name, last_name, commission_rate,
                country_id, state_id, city_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, email, phone, first_name, last_name, is_active, commission_rate, country_id, state_id, city_id, created_at;
        """,
        data["email"], password_hash,
        data["phone"], data["first_name"], data["last_name"], commission_rate,
        country_id, state_id, city_id
        )
        
        return True, {
            "id": str(row["id"]),
            "email": row["email"],
            "phone": row["phone"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "is_active": row["is_active"],
            "commissionRate": float(row["commission_rate"]) if row.get("commission_rate") is not None else None,
            "countryId": int(row["country_id"]) if row.get("country_id") is not None else None,
            "stateId": int(row["state_id"]) if row.get("state_id") is not None else None,
            "cityId": int(row["city_id"]) if row.get("city_id") is not None else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
    except Exception as e:
        return False, str(e)


async def list_corporate_users(limit: int = 50, offset: int = 0) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Tüm Corporate kullanıcıları listeler
    """
    try:
        rows = await fetch_all("""
            SELECT 
                id,
                email,
                phone,
                first_name,
                last_name,
                is_active,
                commission_rate,
                country_id,
                state_id,
                city_id,
                created_at
            FROM corporate_users
            WHERE (deleted IS NULL OR deleted = FALSE)
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
        """, limit, offset)
        
        result = []
        for row in rows:
            result.append({
                "id": str(row["id"]),
                "email": row["email"],
                "phone": row["phone"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "is_active": row["is_active"],
                "commissionRate": float(row["commission_rate"]) if row.get("commission_rate") is not None else None,
                "countryId": int(row["country_id"]) if row.get("country_id") is not None else None,
                "stateId": int(row["state_id"]) if row.get("state_id") is not None else None,
                "cityId": int(row["city_id"]) if row.get("city_id") is not None else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            })
        
        return True, result
    except Exception as e:
        return False, str(e)


async def get_corporate_user(user_id: str) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Bir Corporate kullanıcıyı getirir
    """
    try:
        row = await fetch_one("""
            SELECT 
                id,
                email,
                phone,
                first_name,
                last_name,
                is_active,
                commission_rate,
                country_id,
                state_id,
                city_id,
                created_at
            FROM corporate_users
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
        """, user_id)
        
        if not row:
            return False, "Kurumsal kullanıcı bulunamadı"
        
        return True, {
            "id": str(row["id"]),
            "email": row["email"],
            "phone": row["phone"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "is_active": row["is_active"],
            "commissionRate": float(row["commission_rate"]) if row.get("commission_rate") is not None else None,
            "countryId": int(row["country_id"]) if row.get("country_id") is not None else None,
            "stateId": int(row["state_id"]) if row.get("state_id") is not None else None,
            "cityId": int(row["city_id"]) if row.get("city_id") is not None else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None
        }
    except Exception as e:
        return False, str(e)


async def update_corporate_user(user_id: str, fields: Dict[str, Any]) -> Tuple[bool, str | None]:
    """
    Corporate kullanıcıyı günceller
    """
    try:
        if not fields:
            return False, "Güncellenecek alan bulunamadı"
        
        # Kullanıcıyı kontrol et
        user = await fetch_one("""
            SELECT id
            FROM corporate_users
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
        """, user_id)
        
        if not user:
            return False, "Kurumsal kullanıcı bulunamadı"
        
        mapping = {
            "email": "email",
            "phone": "phone",
            "first_name": "first_name",
            "last_name": "last_name",
            "is_active": "is_active",
            "commissionRate": "commission_rate",
            "countryId": "country_id",
            "stateId": "state_id",
            "cityId": "city_id"
        }
        
        sets: List[str] = []
        params: List[Any] = []
        i = 1
        
        for k, v in fields.items():
            col = mapping.get(k)
            if not col:
                continue
            sets.append(f"{col} = ${i}")
            params.append(v)
            i += 1
        
        if not sets:
            return False, "Geçerli güncellenecek alan bulunamadı"
        
        params.append(user_id)
        
        result = await execute(f"""
            UPDATE corporate_users
            SET {', '.join(sets)}, updated_at = NOW()
            WHERE id = ${i};
        """, *params)
        
        if result.endswith(" 0"):
            return False, "Kurumsal kullanıcı bulunamadı"
        return True, None
    except Exception as e:
        return False, str(e)


async def delete_corporate_user(user_id: str) -> Tuple[bool, str | None]:
    """
    Corporate kullanıcıyı siler (soft delete)
    """
    try:
        # Kullanıcıyı kontrol et
        user = await fetch_one("""
            SELECT id
            FROM corporate_users
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
        """, user_id)
        
        if not user:
            return False, "Kurumsal kullanıcı bulunamadı"
        
        result = await execute("""
            UPDATE corporate_users
            SET deleted = TRUE, updated_at = NOW()
            WHERE id = $1;
        """, user_id)
        
        if result.endswith(" 0"):
            return False, "Kurumsal kullanıcı bulunamadı"
        return True, None
    except Exception as e:
        return False, str(e)

