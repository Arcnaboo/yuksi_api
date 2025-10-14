from typing import Optional, Tuple, List, Dict, Any
from ..utils.database import db_cursor
from ..utils.security import hash_pwd


def restaurant_register(
    email: str,
    password: str,
    phone: str,
    country_id: int,
    name: str,
    contact_person: str,
    tax_number: str,
    address_line1: str,
    address_line2: str,
    state_id: int,  # .NET'teki cityId
    city_id: int,   # .NET'teki districtId
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Restaurant kayıt işlemi.
    Returns: (restaurant_data, error_message)
    """
    with db_cursor() as cur:
        # Email kontrolü
        cur.execute("SELECT id FROM restaurants WHERE email=%s", (email,))
        if cur.fetchone():
            return None, "Email already registered"

        # Geo kontrolü (opsiyonel - yoksa uyarı ver ama devam et)
        try:
            cur.execute("SELECT 1 FROM countries WHERE id=%s", (country_id,))
            if not cur.fetchone():
                print(f"[WARNING] Country {country_id} not found in database")
            
            cur.execute("SELECT 1 FROM states WHERE id=%s", (state_id,))
            if not cur.fetchone():
                print(f"[WARNING] State {state_id} not found in database")
                
            cur.execute("SELECT 1 FROM cities WHERE id=%s", (city_id,))
            if not cur.fetchone():
                print(f"[WARNING] City {city_id} not found in database")
        except Exception as e:
            print(f"[WARNING] Geo validation failed: {e}")

        # Password hash
        pwd_hash = hash_pwd(password)

        # Insert restaurant
        cur.execute(
            """
            INSERT INTO restaurants (
                email, password_hash, phone, country_id, name, 
                contact_person, tax_number, address_line1, address_line2,
                state_id, city_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, name, contact_person, tax_number, phone, 
                      address_line1, address_line2
            """,
            (
                email, pwd_hash, phone, country_id, name,
                contact_person, tax_number, address_line1, address_line2,
                state_id, city_id
            )
        )
        row = cur.fetchone()

        # Tuple'ı dict'e çevir
        restaurant_data = {
            "id": str(row[0]),
            "email": row[1],
            "name": row[2],
            "contactPerson": row[3],
            "taxNumber": row[4],
            "phone": row[5],
            "fullAddress": f"{row[6] or ''} {row[7] or ''}".strip()
        }

        return restaurant_data, None


def list_restaurants(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Tüm restoranları listeler.
    Returns: List of restaurant dicts
    """
    sql = """
    SELECT 
        id,
        email,
        name,
        contact_person,
        tax_number,
        phone,
        address_line1,
        address_line2
    FROM restaurants
    ORDER BY created_at DESC
    LIMIT %s OFFSET %s
    """
    
    with db_cursor(dict_cursor=True) as cur:
        cur.execute(sql, (limit, offset))
        rows = cur.fetchall()
        
        # fullAddress ekle
        result = []
        for row in rows:
            result.append({
                "id": str(row["id"]),
                "email": row["email"],
                "name": row["name"],
                "contactPerson": row["contact_person"],
                "taxNumber": row["tax_number"],
                "phone": row["phone"],
                "fullAddress": f"{row['address_line1'] or ''} {row['address_line2'] or ''}".strip()
            })
        
        return result

