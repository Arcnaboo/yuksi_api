from typing import Dict, Any, Tuple, Optional
from app.utils.database_async import fetch_one, execute
from app.utils.security import hash_pwd

async def create_support_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi üyesi oluşturma servisi (Admin tarafından)
    
    Args:
        first_name: Ad
        last_name: Soyad
        email: E-posta adresi (unique olmalı)
        password: Şifre (hash'lenecek)
        phone: Telefon numarası
        
    Returns:
        Tuple[bool, dict | str]: (success, result veya error_message)
    """
    try:
        # Email unique kontrolü
        existing = await fetch_one(
            "SELECT id FROM support_users WHERE email = $1;",
            email.lower()
        )
        if existing:
            return False, "Bu e-posta adresi zaten kullanılıyor."
        
        # Password hash
        password_hash = hash_pwd(password)
        
        # DB'ye kayıt
        query = """
            INSERT INTO support_users (first_name, last_name, email, password_hash, phone)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, first_name, last_name, email, phone, is_active, created_at;
        """
        
        row = await fetch_one(
            query,
            first_name,
            last_name,
            email.lower(),
            password_hash,
            phone
        )
        
        if not row:
            return False, "Support üyesi oluşturulamadı."
        
        # Response formatla
        row_dict = dict(row) if not isinstance(row, dict) else row
        
        return True, {
            "id": str(row_dict["id"]),
            "first_name": row_dict["first_name"],
            "last_name": row_dict["last_name"],
            "email": row_dict["email"],
            "phone": row_dict["phone"],
            "is_active": row_dict.get("is_active", True),
            "created_at": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None
        }
        
    except Exception as e:
        return False, f"Support üyesi oluşturulurken hata oluştu: {str(e)}"

