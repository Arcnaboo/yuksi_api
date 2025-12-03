from typing import Dict, Any, Tuple, Optional, List
from app.utils.database_async import fetch_one, fetch_all, execute

async def update_support_permissions(
    support_user_id: str,
    access: List[int]
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi üyesi yetkilerini güncelleme servisi (Admin tarafından)
    
    Args:
        support_user_id: Support kullanıcı ID'si
        access: Erişim modülleri listesi (1-7 arası)
        
    Returns:
        Tuple[bool, dict | str]: (success, result veya error_message)
    """
    try:
        # Kullanıcı var mı kontrol et
        user = await fetch_one(
            "SELECT id FROM support_users WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);",
            support_user_id
        )
        if not user:
            return False, "Support kullanıcısı bulunamadı veya silinmiş."
        
        # Access validasyonu (1-7 arası olmalı)
        if access is None:
            access = []
        else:
            # Geçersiz modül numaralarını filtrele ve tekrarları kaldır
            access = sorted(list(set([m for m in access if 1 <= m <= 7])))
        
        # Yetkileri güncelle
        query = """
            UPDATE support_users
            SET access = $1, updated_at = NOW()
            WHERE id = $2
            RETURNING id, first_name, last_name, email, phone, is_active, access, updated_at;
        """
        
        row = await fetch_one(query, access, support_user_id)
        
        if not row:
            return False, "Yetkiler güncellenemedi."
        
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
        return False, f"Yetkiler güncellenirken hata oluştu: {str(e)}"


async def get_support_permissions(
    support_user_id: str
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Çağrı merkezi üyesi yetkilerini getirme servisi
    
    Args:
        support_user_id: Support kullanıcı ID'si
        
    Returns:
        Tuple[bool, dict | str]: (success, result veya error_message)
    """
    try:
        row = await fetch_one(
            """
            SELECT id, first_name, last_name, email, phone, is_active, access, created_at, updated_at
            FROM support_users
            WHERE id = $1 AND (deleted IS NULL OR deleted = FALSE);
            """,
            support_user_id
        )
        
        if not row:
            return False, "Support kullanıcısı bulunamadı."
        
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
            "created_at": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
            "updated_at": row_dict["updated_at"].isoformat() if row_dict.get("updated_at") else None
        }
        
    except Exception as e:
        return False, f"Yetkiler getirilirken hata oluştu: {str(e)}"


async def check_support_module(
    support_user_id: str,
    module_number: int
) -> bool:
    """
    Support kullanıcısının belirli bir modüle erişim yetkisi var mı kontrol eder
    
    Args:
        support_user_id: Support kullanıcı ID'si
        module_number: Modül numarası (1-7)
        
    Returns:
        bool: Yetki varsa True, yoksa False
    """
    try:
        row = await fetch_one(
            "SELECT access FROM support_users WHERE id = $1 AND is_active = TRUE AND (deleted IS NULL OR deleted = FALSE);",
            support_user_id
        )
        
        if not row:
            return False
        
        row_dict = dict(row) if not isinstance(row, dict) else row
        access_list = list(row_dict.get("access", [])) if row_dict.get("access") else []
        
        return module_number in access_list
        
    except Exception:
        return False


async def get_all_support_permissions(
    limit: int = 50,
    offset: int = 0
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Tüm çağrı merkezi üyelerinin yetkilerini getirme servisi
    
    Args:
        limit: Maksimum kayıt sayısı
        offset: Sayfalama offset
        
    Returns:
        Tuple[bool, list | str]: (success, result veya error_message)
    """
    try:
        rows = await fetch_all(
            """
            SELECT id, first_name, last_name, email, phone, is_active, access, created_at, updated_at
            FROM support_users
            WHERE (deleted IS NULL OR deleted = FALSE)
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
            """,
            limit,
            offset
        )
        
        if not rows:
            return True, []
        
        result = []
        for row in rows:
            row_dict = dict(row) if not isinstance(row, dict) else row
            
            # PostgreSQL array'i list'e çevir
            access_list = list(row_dict.get("access", [])) if row_dict.get("access") else []
            
            result.append({
                "id": str(row_dict["id"]),
                "first_name": row_dict["first_name"],
                "last_name": row_dict["last_name"],
                "email": row_dict["email"],
                "phone": row_dict["phone"],
                "is_active": row_dict.get("is_active", True),
                "access": access_list,
                "created_at": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
                "updated_at": row_dict["updated_at"].isoformat() if row_dict.get("updated_at") else None
            })
        
        return True, result
        
    except Exception as e:
        return False, f"Yetkiler getirilirken hata oluştu: {str(e)}"
