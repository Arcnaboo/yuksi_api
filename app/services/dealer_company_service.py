from typing import List, Dict, Any, Tuple, Optional
from app.utils.database_async import fetch_one, fetch_all, execute
from app.services import company_service


async def dealer_create_and_link_company(
    dealer_id: str,
    company_tracking_no: str,
    assigned_kilometers: int,
    special_commission_rate: float,
    is_visible: bool,
    can_receive_payments: bool,
    city_id: int,
    state_id: int,
    location: str,
    company_name: str,
    company_phone: str,
    description: str,
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Bayi için yeni şirket oluşturur ve bayisine bağlar.
    Returns: (success, data, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, None, "Bayi bulunamadı"
        
        # Şirket oluştur
        company_data = {
            "companyTrackingNo": company_tracking_no,
            "assignedKilometers": assigned_kilometers,
            "specialCommissionRate": special_commission_rate,
            "isVisible": is_visible,
            "canReceivePayments": can_receive_payments,
            "cityId": city_id,
            "stateId": state_id,
            "location": location,
            "companyName": company_name,
            "companyPhone": company_phone,
            "description": description
        }
        
        success, result = await company_service.create_company(company_data)
        
        if not success:
            return False, None, result
        
        company_id = result.get("id")
        if not company_id:
            return False, None, "Şirket oluşturulamadı"
        
        # Şimdi bayisine bağla
        link_success, link_err = await dealer_link_existing_company(dealer_id, company_id)
        if not link_success:
            return False, None, f"Şirket oluşturuldu ancak bayisine bağlanamadı: {link_err}"
        
        return True, result, None
        
    except Exception as e:
        return False, None, str(e)


async def dealer_link_existing_company(
    dealer_id: str,
    company_id: str,
) -> Tuple[bool, Optional[str]]:
    """
    Mevcut bir şirketi bayisine bağlar.
    Returns: (success, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Şirket kontrolü
        company = await fetch_one("SELECT id, company_name FROM companies WHERE id = $1", company_id)
        if not company:
            return False, "Şirket bulunamadı"
        
        # Şirket zaten başka bir bayide mi kontrol et
        existing = await fetch_one(
            "SELECT dealer_id FROM dealer_companies WHERE company_id = $1",
            company_id
        )
        if existing:
            existing_dealer_id = str(existing.get("dealer_id"))
            if existing_dealer_id == dealer_id:
                return False, "Bu şirket zaten bu bayisine bağlı"
            else:
                return False, "Bu şirket başka bir bayide bağlı"
        
        # Bağla
        await execute(
            "INSERT INTO dealer_companies (dealer_id, company_id) VALUES ($1, $2)",
            dealer_id, company_id
        )
        
        return True, None
        
    except Exception as e:
        # Unique constraint hatası
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            return False, "Bu şirket zaten bir bayide bağlı"
        return False, str(e)


async def dealer_get_companies(
    dealer_id: str,
    limit: int = 50,
    offset: int = 0
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    Bayinin bağlı olduğu şirketleri listeler.
    Returns: (success, data_or_error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Şirketleri getir
        rows = await fetch_all("""
            SELECT 
                c.id,
                c.company_tracking_no,
                c.company_name,
                c.company_phone,
                c.city_id,
                c.state_id,
                c.special_commission_rate,
                c.assigned_kilometers,
                c.consumed_kilometers,
                c.is_visible,
                c.can_receive_payments,
                c.location,
                c.description,
                c.status,
                c.created_at,
                dc.created_at as linked_at,
                ci.name as city_name,
                s.name as state_name,
                co.name as country_name
            FROM dealer_companies dc
            INNER JOIN companies c ON c.id = dc.company_id
            LEFT JOIN cities ci ON ci.id = c.city_id
            LEFT JOIN states s ON s.id = c.state_id
            LEFT JOIN countries co ON co.id = s.country_id
            WHERE dc.dealer_id = $1
            ORDER BY dc.created_at DESC
            LIMIT $2 OFFSET $3
        """, dealer_id, limit, offset)
        
        result = []
        if rows:
            for row in rows:
                row_dict = dict(row)
                # UUID'leri string'e çevir
                if row_dict.get("id"):
                    row_dict["id"] = str(row_dict["id"])
                result.append({
                    "id": row_dict["id"],
                    "companyTrackingNo": row_dict.get("company_tracking_no"),
                    "companyName": row_dict.get("company_name"),
                    "companyPhone": row_dict.get("company_phone"),
                    "cityId": row_dict.get("city_id"),
                    "stateId": row_dict.get("state_id"),
                    "cityName": row_dict.get("city_name"),
                    "stateName": row_dict.get("state_name"),
                    "countryName": row_dict.get("country_name"),
                    "specialCommissionRate": float(row_dict["special_commission_rate"]) if row_dict.get("special_commission_rate") is not None else None,
                    "assignedKilometers": row_dict.get("assigned_kilometers"),
                    "consumedKilometers": row_dict.get("consumed_kilometers"),
                    "remainingKilometers": (row_dict.get("assigned_kilometers") or 0) - (row_dict.get("consumed_kilometers") or 0),
                    "isVisible": row_dict.get("is_visible"),
                    "canReceivePayments": row_dict.get("can_receive_payments"),
                    "location": row_dict.get("location"),
                    "description": row_dict.get("description"),
                    "status": row_dict.get("status"),
                    "createdAt": row_dict["created_at"].isoformat() if row_dict.get("created_at") else None,
                    "linkedAt": row_dict["linked_at"].isoformat() if row_dict.get("linked_at") else None
                })
        
        return True, result
        
    except Exception as e:
        return False, str(e)


async def dealer_get_company_detail(
    dealer_id: str,
    company_id: str
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Bayinin kendisine ait bir şirketin detaylı profilini getirir.
    Returns: (success, profile_data_or_none, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, None, "Bayi bulunamadı"
        
        # Şirketin bayinin kendisine ait olup olmadığını kontrol et
        link = await fetch_one(
            "SELECT id FROM dealer_companies WHERE dealer_id = $1 AND company_id = $2",
            dealer_id, company_id
        )
        if not link:
            return False, None, "Bu şirket bu bayisine bağlı değil"
        
        # Şirket detayını getir
        success, company_data = await company_service.get_company(company_id)
        
        if not success:
            return False, None, company_data or "Şirket bulunamadı"
        
        # Linked at bilgisini ekle
        link_info = await fetch_one(
            "SELECT created_at FROM dealer_companies WHERE dealer_id = $1 AND company_id = $2",
            dealer_id, company_id
        )
        
        if link_info:
            company_data["linkedAt"] = link_info["created_at"].isoformat() if link_info.get("created_at") else None
        
        return True, company_data, None
        
    except Exception as e:
        return False, None, str(e)


async def dealer_update_company(
    dealer_id: str,
    company_id: str,
    fields: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    Bayinin kendisine ait bir şirketi günceller.
    Returns: (success, error_message)
    """
    try:
        # Bayi kontrolü
        dealer = await fetch_one("SELECT id FROM dealers WHERE id = $1", dealer_id)
        if not dealer:
            return False, "Bayi bulunamadı"
        
        # Şirketin bayinin kendisine ait olup olmadığını kontrol et
        link = await fetch_one(
            "SELECT id FROM dealer_companies WHERE dealer_id = $1 AND company_id = $2",
            dealer_id, company_id
        )
        if not link:
            return False, "Bu şirket bu bayisine bağlı değil"
        
        # Şirketi güncelle
        success, error = await company_service.update_company(company_id, fields)
        
        if not success:
            return False, error or "Şirket güncellenemedi"
        
        return True, None
        
    except Exception as e:
        return False, str(e)

