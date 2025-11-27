from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from app.utils.database_async import fetch_one, fetch_all, execute
from app.utils.security import hash_pwd


async def create_corporate_user(data: Dict[str, Any]) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Admin tarafından Corporate kullanıcı oluşturur (Restoran gibi ayrı tablo)
    """
    try:
        # Email kontrolü (sadece silinmemiş kayıtlar)
        existing = await fetch_one("SELECT id FROM corporate_users WHERE email = $1 AND (deleted IS NULL OR deleted = FALSE);", data["email"])
        if existing:
            return False, "Bu email adresi zaten kayıtlı"
        
        # Password hashle
        password_hash = hash_pwd(data["password"])
        
        # fullAddress desteği: adres_line1/2 yerine tek alanla giriş ve bölme
        import re
        address_line1 = data.get("addressLine1")
        address_line2 = data.get("addressLine2")
        full_address = data.get("fullAddress")
        
        if full_address and not address_line1:
            # fullAddress varsa ve addressLine1 yoksa, fullAddress'i böl
            parts = [p.strip() for p in re.split(r",|;|\n", str(full_address)) if p.strip()]
            if parts:
                address_line1 = parts[0]
                address_line2 = ", ".join(parts[1:]) if len(parts) > 1 else (address_line2 or "")
            else:
                address_line1 = str(full_address).strip()
                address_line2 = address_line2 or ""
        
        # Corporate user oluştur (Restoran gibi direkt tabloya insert)
        commission_rate = data.get("commissionRate")
        country_id = data.get("countryId")
        state_id = data.get("stateId")
        city_id = data.get("cityId")
        row = await fetch_one("""
            INSERT INTO corporate_users (
                email, password_hash, 
                phone, first_name, last_name, commission_rate,
                country_id, state_id, city_id,
                address_line1, address_line2
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id, email, phone, first_name, last_name, is_active, commission_rate, country_id, state_id, city_id, address_line1, address_line2, created_at;
        """,
        data["email"], password_hash,
        data["phone"], data["first_name"], data["last_name"], commission_rate,
        country_id, state_id, city_id,
        address_line1, address_line2
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
                address_line1,
                address_line2,
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
                "addressLine1": row.get("address_line1"),
                "addressLine2": row.get("address_line2"),
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
                address_line1,
                address_line2,
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
            "addressLine1": row.get("address_line1"),
            "addressLine2": row.get("address_line2"),
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
        
        # fullAddress desteği: adres_line1/2 yerine tek alanla güncelleme ve bölme
        import re
        full_address = fields.pop("fullAddress", None)
        address_line1 = fields.get("addressLine1")
        address_line2 = fields.get("addressLine2")
        
        if full_address and not address_line1:
            # fullAddress varsa ve addressLine1 yoksa, fullAddress'i böl
            parts = [p.strip() for p in re.split(r",|;|\n", str(full_address)) if p.strip()]
            if parts:
                fields["addressLine1"] = parts[0]
                if "addressLine2" not in fields:
                    fields["addressLine2"] = ", ".join(parts[1:]) if len(parts) > 1 else ""
            else:
                fields["addressLine1"] = str(full_address).strip()
                fields.setdefault("addressLine2", "")
        
        mapping = {
            "email": "email",
            "phone": "phone",
            "first_name": "first_name",
            "last_name": "last_name",
            "is_active": "is_active",
            "commissionRate": "commission_rate",
            "countryId": "country_id",
            "stateId": "state_id",
            "cityId": "city_id",
            "addressLine1": "address_line1",
            "addressLine2": "address_line2"
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


# === GET PROFILE ===
async def get_corporate_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Kurumsal kullanıcı profil bilgilerini getirir"""
    try:
        row = await fetch_one(
            """
            SELECT 
                email, phone, first_name, last_name, 
                address_line1, address_line2,
                country_id, state_id, city_id,
                commission_rate, commission_description
            FROM corporate_users 
            WHERE id = $1
              AND (deleted IS NULL OR deleted = FALSE);
            """,
            user_id
        )
        if not row:
            return None

        # fullAddress: addressLine1 ve addressLine2'yi birleştir
        address_line1 = row.get("address_line1") or ""
        address_line2 = row.get("address_line2") or ""
        full_address = f"{address_line1} {address_line2}".strip() if address_line1 or address_line2 else None

        return {
            "email": row.get("email"),
            "phone": row.get("phone"),
            "firstName": row.get("first_name") or "",
            "lastName": row.get("last_name") or "",
            "fullAddress": full_address,
            "countryId": int(row["country_id"]) if row.get("country_id") is not None else None,
            "stateId": int(row["state_id"]) if row.get("state_id") is not None else None,
            "cityId": int(row["city_id"]) if row.get("city_id") is not None else None,
            "commissionRate": float(row["commission_rate"]) if row.get("commission_rate") is not None else None,
            "commissionDescription": row.get("commission_description"),
        }
    except Exception as e:
        print(f"Error getting corporate profile: {e}")
        return None


# === UPDATE PROFILE ===
async def update_corporate_profile(
    user_id: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    full_address: Optional[str] = None,
    country_id: Optional[int] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """Kurumsal kullanıcı profil bilgilerini günceller"""
    try:
        update_fields = []
        params = []
        i = 1

        if email is not None:
            # Email unique kontrolü (sadece silinmemiş kayıtlar için)
            existing = await fetch_one(
                "SELECT id FROM corporate_users WHERE email = $1 AND id != $2 AND (deleted IS NULL OR deleted = FALSE);",
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
        if full_address is not None:
            # fullAddress'i addressLine1/2'ye böl
            import re
            parts = [p.strip() for p in re.split(r",|;|\n", str(full_address)) if p.strip()]
            if parts:
                address_line1 = parts[0]
                address_line2 = ", ".join(parts[1:]) if len(parts) > 1 else ""
            else:
                address_line1 = full_address
                address_line2 = ""
            
            update_fields.append(f"address_line1 = ${i}")
            params.append(address_line1)
            i += 1
            update_fields.append(f"address_line2 = ${i}")
            params.append(address_line2)
            i += 1
        if country_id is not None:
            update_fields.append(f"country_id = ${i}")
            params.append(country_id)
            i += 1
        if state_id is not None:
            update_fields.append(f"state_id = ${i}")
            params.append(state_id)
            i += 1
        if city_id is not None:
            update_fields.append(f"city_id = ${i}")
            params.append(city_id)
            i += 1

        if not update_fields:
            return False, "Güncellenecek alan bulunamadı"

        # updated_at ekle
        update_fields.append(f"updated_at = NOW()")
        params.append(user_id)

        query = f"""
            UPDATE corporate_users 
            SET {', '.join(update_fields)}
            WHERE id = ${i};
        """
        
        result = await execute(query, *params)
        
        if result.endswith(" 0"):
            return False, "Kurumsal kullanıcı bulunamadı"
        
        return True, None
    except Exception as e:
        return False, str(e)

