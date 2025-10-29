from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from app.utils.database_async import fetch_one, fetch_all, execute

# -------- Companies --------

async def create_company(data: Dict[str, Any]) -> Tuple[bool, str | Dict[str, Any]]:
    try:
        row = await fetch_one("""
            INSERT INTO companies (
                company_tracking_no, assigned_kilometers, special_commission_rate,
                is_visible, can_receive_payments, city_id, state_id, location,
                company_name, company_phone, description
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            RETURNING id;
        """,
        data["companyTrackingNo"],
        data["assignedKilometers"],
        data["specialCommissionRate"],
        data["isVisible"],
        data["canReceivePayments"],
        data["cityId"],
        data["stateId"],
        data["location"],
        data["companyName"],
        data["companyPhone"],
        data["description"]
        )
        return True, {"id": str(row["id"]) if isinstance(row, dict) else str(row[0])}
    except Exception as e:
        return False, str(e)


async def list_companies(limit: int, offset: int, city_id: int | None, status: str | None) -> Tuple[bool, List[Dict[str, Any]] | str]:
    try:
        filters = []
        params: List[Any] = []
        i = 1
        if city_id is not None:
            filters.append(f"c.city_id = ${i}")
            params.append(city_id); i += 1
        if status is not None:
            filters.append(f"c.status = ${i}")
            params.append(status); i += 1
        where = f"WHERE {' AND '.join(filters)}" if filters else ""
        params.extend([limit, offset])

        rows = await fetch_all(f"""
            SELECT
                c.id,
                c.company_tracking_no AS "companyTrackingNo",
                c.company_name AS "companyName",
                c.company_phone AS "companyPhone",
                c.city_id AS "cityId",
                c.state_id AS "stateId",
                c.special_commission_rate AS "specialCommissionRate",
                c.assigned_kilometers AS "assignedKilometers",
                c.consumed_kilometers AS "consumedKilometers",
                c.can_receive_payments AS "canReceivePayments",
                c.is_visible AS "isVisible",
                (c.assigned_kilometers - c.consumed_kilometers) AS "remainingKilometers",
                c.status AS "status"
            FROM companies c
            {where}
            ORDER BY c.created_at DESC
            LIMIT ${i} OFFSET ${i+1};
        """, *params)
        return True, rows
    except Exception as e:
        return False, str(e)


async def get_company(company_id: str) -> Tuple[bool, Dict[str, Any] | str]:
    try:
        row = await fetch_one("""
            SELECT
                c.id,
                c.company_tracking_no AS "companyTrackingNo",
                c.company_name AS "companyName",
                c.company_phone AS "companyPhone",
                c.city_id AS "cityId",
                c.state_id AS "stateId",
                c.special_commission_rate AS "specialCommissionRate",
                c.assigned_kilometers AS "assignedKilometers",
                c.consumed_kilometers AS "consumedKilometers",
                c.is_visible AS "isVisible",
                C.can_receive_payments AS "canReceivePayments",
                (c.assigned_kilometers - c.consumed_kilometers) AS "remainingKilometers",
                c.status AS "status",
                c.is_visible AS "isVisible",
                c.can_receive_payments AS "canReceivePayments",
                c.location AS "location",
                c.description AS "description"
            FROM companies c
            WHERE c.id = $1;
        """, company_id)
        if not row:
            return False, "Company not found"
        return True, dict(row)
    except Exception as e:
        return False, str(e)


async def update_company(company_id: str, fields: Dict[str, Any]) -> Tuple[bool, str | None]:
    try:
        if not fields:
            return False, "No fields to update"

        mapping = {
            "companyTrackingNo": "company_tracking_no",
            "assignedKilometers": "assigned_kilometers",
            "consumedKilometers": "consumed_kilometers",
            "specialCommissionRate": "special_commission_rate",
            "isVisible": "is_visible",
            "canReceivePayments": "can_receive_payments",
            "cityId": "city_id",
            "stateId": "state_id",
            "location": "location",
            "companyName": "company_name",
            "companyPhone": "company_phone",
            "description": "description",
            "status": "status"
        }

        sets: List[str] = []
        params: List[Any] = []
        i = 1
        for k, v in fields.items():
            col = mapping.get(k, None)
            if not col: 
                continue
            sets.append(f"{col} = ${i}")
            params.append(v)
            i += 1

        if not sets:
            return False, "No valid fields to update"

        params.append(company_id)
        result = await execute(f"""
            UPDATE companies
            SET {', '.join(sets)}
            WHERE id = ${i};
        """, *params)

        if result.endswith(" 0"):
            return False, "Company not found"
        return True, None
    except Exception as e:
        return False, str(e)


async def delete_company(company_id: str) -> Tuple[bool, str | None]:
    
    try:
        result = await execute("DELETE FROM companies WHERE id = $1;", company_id)
        if result.endswith(" 0"):
            return False, "Company not found"
        return True, None
    except Exception as e:
        return False, str(e)



# -------- Managers --------

async def add_manager(company_id: str, data: Dict[str, Any]) -> Tuple[bool, str | Dict[str, Any]]:
    try:
        row = await fetch_one("""
            INSERT INTO company_managers (company_id, name_surname, email, phone)
            VALUES ($1,$2,$3,$4)
            RETURNING id;
        """, company_id, data["nameSurname"], data["email"], data["phone"])
        return True, {"id": str(row["id"]) if isinstance(row, dict) else str(row[0])}
    except Exception as e:
        return False, str(e)


async def list_managers(company_id: str) -> Tuple[bool, List[Dict[str, Any]] | str]:
    try:
        rows = await fetch_all("""
            SELECT id, name_surname AS "nameSurname", email, phone, created_at AS "createdAt"
            FROM company_managers
            WHERE company_id = $1
            ORDER BY created_at DESC;
        """, company_id)
        return True, rows
    except Exception as e:
        return False, str(e)


async def update_manager(company_id: str, manager_id: str, fields: Dict[str, Any]) -> Tuple[bool, str | None]:
    try:
        if not fields:
            return False, "No fields to update"
        mapping = {"nameSurname": "name_surname", "email": "email", "phone": "phone"}
        sets, params = [], []
        i = 1
        for k, v in fields.items():
            col = mapping.get(k)
            if not col:
                continue
            sets.append(f"{col} = ${i}")
            params.append(v); i += 1
        if not sets:
            return False, "No valid fields to update"

        params.extend([manager_id, company_id])
        res = await execute(f"""
            UPDATE company_managers
            SET {', '.join(sets)}
            WHERE id = ${i} AND company_id = ${i+1};
        """, *params)
        if res.endswith(" 0"):
            return False, "Manager not found"
        return True, None
    except Exception as e:
        return False, str(e)


async def delete_manager(company_id: str, manager_id: str) -> Tuple[bool, str | None]:
    try:
        res = await execute("""
            DELETE FROM company_managers
            WHERE id = $1 AND company_id = $2;
        """, manager_id, company_id)
        if res.endswith(" 0"):
            return False, "Manager not found"
        return True, None
    except Exception as e:
        return False, str(e)
