from typing import Dict, Any, Tuple, Optional, List
from app.utils.database_async import fetch_one, execute
from app.utils.security import hash_pwd

async def create_support_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: str,
    access: list[int] = None
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi üyesi oluşturma servisi (Admin tarafından)
    
    Args:
        first_name: Ad
        last_name: Soyad
        email: E-posta adresi (unique olmalı)
        password: Şifre (hash'lenecek)
        phone: Telefon numarası
        access: Erişim modülleri listesi (1-7 arası)
        
    Returns:
        Tuple[bool, dict | str]: (success, result veya error_message)
    """
    try:
        # Email unique kontrolü (sadece silinmemiş kullanıcılar için)
        existing = await fetch_one(
            "SELECT id FROM support_users WHERE email = $1 AND (deleted IS NULL OR deleted = FALSE);",
            email.lower()
        )
        if existing:
            return False, "Bu e-posta adresi zaten kullanılıyor."
        
        # Access validasyonu (1-7 arası olmalı)
        if access is None:
            access = []
        else:
            # Geçersiz modül numaralarını filtrele
            access = [m for m in access if 1 <= m <= 7]
        
        # Password hash
        password_hash = hash_pwd(password)
        
        # DB'ye kayıt
        query = """
            INSERT INTO support_users (first_name, last_name, email, password_hash, phone, access)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, first_name, last_name, email, phone, is_active, access, created_at;
        """
        
        row = await fetch_one(
            query,
            first_name,
            last_name,
            email.lower(),
            password_hash,
            phone,
            access
        )
        
        if not row:
            return False, "Support üyesi oluşturulamadı."
        
        # Response formatla
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        # PostgreSQL array'i list'e çevir
        access_list = list(row_dict.get("access", [])) if row_dict.get("access") else []
        
        return True, {
            "id": str(row_dict["id"]),
            "first_name": row_dict["first_name"],
            "last_name": row_dict["last_name"],
            "email": row_dict["email"],
            "phone": row_dict["phone"],
            "is_active": row_dict.get("is_active", True),
            "access": access_list,
            "created_at": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None
        }
        
    except Exception as e:
        return False, f"Support üyesi oluşturulurken hata oluştu: {str(e)}"


async def delete_support_user(
    support_user_id: str
) -> Tuple[bool, str | None]:
    """
    Çağrı merkezi üyesi silme servisi (soft delete) - Admin tarafından
    
    Args:
        support_user_id: Support kullanıcı ID'si
        
    Returns:
        Tuple[bool, str | None]: (success, error_message)
    """
    try:
        # Kullanıcıyı kontrol et
        user = await fetch_one(
            """
            SELECT id, deleted
            FROM support_users
            WHERE id = $1;
            """,
            support_user_id
        )
        
        if not user:
            return False, "Support kullanıcısı bulunamadı."
        
        if user.get("deleted"):
            return False, "Support kullanıcısı zaten silinmiş."
        
        # Soft delete yap
        result = await execute(
            """
            UPDATE support_users
            SET deleted = TRUE, deleted_at = NOW(), is_active = FALSE, updated_at = NOW()
            WHERE id = $1;
            """,
            support_user_id
        )
        
        if result.endswith(" 0"):
            return False, "Support kullanıcısı bulunamadı."
        
        return True, None
        
    except Exception as e:
        return False, f"Support kullanıcısı silinirken hata oluştu: {str(e)}"


async def update_support_user(
    support_user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    is_active: Optional[bool] = None,
    access: Optional[List[int]] = None
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi üyesi güncelleme servisi (Admin tarafından)
    
    Args:
        support_user_id: Support kullanıcı ID'si
        first_name: Ad (opsiyonel)
        last_name: Soyad (opsiyonel)
        email: E-posta adresi (opsiyonel)
        phone: Telefon numarası (opsiyonel)
        is_active: Aktif durumu (opsiyonel)
        access: Erişim modülleri listesi (opsiyonel)
        
    Returns:
        Tuple[bool, dict | str]: (success, result veya error_message)
    """
    try:
        # Kullanıcıyı kontrol et
        user = await fetch_one(
            """
            SELECT id, deleted
            FROM support_users
            WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);
            """,
            support_user_id
        )
        
        if not user:
            return False, "Support kullanıcısı bulunamadı veya silinmiş."
        
        # Güncellenecek alanları belirle
        update_fields = []
        params = []
        i = 1
        
        if first_name is not None:
            update_fields.append(f"first_name = ${i}")
            params.append(first_name)
            i += 1
        
        if last_name is not None:
            update_fields.append(f"last_name = ${i}")
            params.append(last_name)
            i += 1
        
        if email is not None:
            # Email unique kontrolü (sadece silinmemiş kullanıcılar için)
            existing = await fetch_one(
                "SELECT id FROM support_users WHERE email = $1 AND id != $2 AND (deleted IS NULL OR deleted = FALSE);",
                email.lower(),
                support_user_id
            )
            if existing:
                return False, "Bu e-posta adresi zaten kullanılıyor."
            update_fields.append(f"email = ${i}")
            params.append(email.lower())
            i += 1
        
        if phone is not None:
            update_fields.append(f"phone = ${i}")
            params.append(phone)
            i += 1
        
        if is_active is not None:
            update_fields.append(f"is_active = ${i}")
            params.append(is_active)
            i += 1
        
        if access is not None:
            # Access validasyonu (1-7 arası olmalı)
            access_filtered = sorted(list(set([m for m in access if 1 <= m <= 7])))
            update_fields.append(f"access = ${i}")
            params.append(access_filtered)
            i += 1
        
        if not update_fields:
            return False, "Güncellenecek alan bulunamadı."
        
        # updated_at'i güncelle
        update_fields.append("updated_at = NOW()")
        
        # Güncelleme sorgusu
        query = f"""
            UPDATE support_users
            SET {', '.join(update_fields)}
            WHERE id = ${i}
            RETURNING id, first_name, last_name, email, phone, is_active, access, updated_at;
        """
        params.append(support_user_id)
        
        row = await fetch_one(query, *params)
        
        if not row:
            return False, "Support kullanıcısı güncellenemedi."
        
        # Response formatla
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        # PostgreSQL array'i list'e çevir
        access_list = list(row_dict.get("access", [])) if row_dict.get("access") else []
        
        return True, {
            "id": str(row_dict["id"]),
            "first_name": row_dict["first_name"],
            "last_name": row_dict["last_name"],
            "email": row_dict["email"],
            "phone": row_dict["phone"],
            "is_active": row_dict.get("is_active", True),
            "access": access_list,
            "updated_at": row_dict["updated_at"].isoformat() if row_dict.get("updated_at") else None
        }
        
    except Exception as e:
        return False, f"Support kullanıcısı güncellenirken hata oluştu: {str(e)}"

