from typing import Dict, Any, Union
from uuid import UUID
from app.utils.database import db_cursor
from app.services.courier_package_service import get_package_by_id
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

async def create_subscription(data: dict) -> Dict[str, Any]:
    try:
        get_package = await get_package_by_id(data["package_id"])
        if not get_package["success"]:
            return {"success": False, "message": "Invalid package ID", "data": {}}
        
        duration_days = get_package["data"].get("durationdays")
        if duration_days is None:
            return {"success": False, "message": "Package missing duration (days)", "data": {}}

        duration_days = int(duration_days)
        now_tr = datetime.now(ZoneInfo("Europe/Istanbul")).replace(microsecond=0)
        calc_end_date = now_tr + timedelta(days=duration_days)
        params = {
            "courier_id": data["courier_id"],   
            "package_id": data["package_id"],
            "now_tr": now_tr,
            "calc_end_date": calc_end_date
        }
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                INSERT INTO courier_package_subscriptions (courier_id, package_id, start_date, end_date, is_active)
                VALUES (%(courier_id)s, %(package_id)s, %(now_tr)s, %(calc_end_date)s, TRUE)
                RETURNING id;
            """, params)
            row = cur.fetchone()
        return {"success": True, "message": "Subscription created successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
    

async def list_subscriptions(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    s.id           AS "subscriptionId",
                    s.courier_id   AS "courierId",
                    s.package_id   AS "packageId",
                    s.start_date   AS "startDate",
                    s.end_date     AS "endDate",
                    s.is_active    AS "isActive",
                    s.created_at   AS "createdAt",
                    p.package_name  AS "packageName",
                    p.description   AS "packageDescription",
                    p.price         AS "packagePrice",
                    p.duration_days AS "packageDurationDays"
                FROM courier_package_subscriptions AS s
                JOIN courier_packages AS p ON p.id = s.package_id
                ORDER BY s.created_at DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            rows = cur.fetchall() or []
        return {"success": True, "message": "Subscriptions fetched successfully", "data": rows}
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}
    

async def get_subscription_by_id(subscription_id: Union[str, UUID]) -> Dict[str, Any]:   
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    s.id            AS "subscriptionId",
                    s.courier_id    AS "courierId",
                    s.package_id    AS "packageId",
                    s.start_date    AS "startDate",
                    s.end_date      AS "endDate",
                    s.is_active     AS "isActive",
                    s.created_at    AS "createdAt",
                    p.package_name  AS "packageName",
                    p.description   AS "packageDescription",
                    p.price         AS "packagePrice",
                    p.duration_days AS "packageDurationDays"
                FROM courier_package_subscriptions AS s
                LEFT JOIN courier_packages AS p
                       ON p.id = s.package_id
                WHERE s.id = %s;
            """, (str(subscription_id),))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Subscription not found", "data": {}}
        return {"success": True, "message": "Subscription fetched", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
    


async def get_subscription_by_courier_id(courier_id: Union[str, UUID]) -> Dict[str, Any]:   
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT
                    s.id            AS "subscriptionId",
                    s.courier_id    AS "courierId",
                    s.package_id    AS "packageId",
                    s.start_date    AS "startDate",
                    s.end_date      AS "endDate",
                    s.is_active     AS "isActive",
                    s.created_at    AS "createdAt",
                    p.package_name  AS "packageName",
                    p.description   AS "packageDescription",
                    p.price         AS "packagePrice",
                    p.duration_days AS "packageDurationDays"
                FROM courier_package_subscriptions AS s
                LEFT JOIN courier_packages AS p
                       ON p.id = s.package_id
                WHERE s.courier_id = %s
                ORDER BY s.created_at DESC
                LIMIT 1;
            """, (str(courier_id),))
            row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Subscription not found for the given courier", "data": {}}
        return {"success": True, "message": "Subscription fetched", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
    
    

async def update_subscription(subscription_id: UUID, fields: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if "is_active" not in fields:
            return {"success": False, "message": "Only is_active can be updated", "data": {}}

        is_active = fields["is_active"]
        fields["subscription_id"] = subscription_id
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT id, courier_id, is_active
                FROM courier_package_subscriptions
                WHERE id = %(id)s
                FOR UPDATE
            """, {"id": str(subscription_id)})
            current = cur.fetchone()
            if not current:
                return {"success": False, "message": "Subscription not found", "data": {}}
            cur.execute("""
                UPDATE courier_package_subscriptions
                SET is_active = %(is_active)s
                WHERE id = %(id)s
                RETURNING id, courier_id, package_id, start_date, end_date, is_active, created_at
            """, {"is_active": is_active, "id": current["id"]})
            row = cur.fetchone()
        return {"success": True, "message": "Subscription updated successfully", "data": row}
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}
    

async def delete_subscription(subscription_id: UUID) -> Dict[str, Any]:
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                UPDATE courier_package_subscriptions
                SET deleted_at = NOW(),
                    is_active  = FALSE
                WHERE id = %s::uuid
                RETURNING id, courier_id, package_id, start_date, end_date, is_active, created_at, deleted_at;
            """, (str(subscription_id),))
            row = cur.fetchone()

        if not row:
            return {"success": False, "message": "Subscription not found", "data": {}}

        return {"success": True, "message": "Subscription deleted successfully", "data": row}

    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}