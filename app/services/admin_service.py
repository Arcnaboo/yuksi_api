from typing import Any, Dict, Literal, Optional, Tuple
from ..utils.security import hash_pwd
import app.utils.database_async as db

JOB_TYPE_FILTERS = {
    "Restaurant": "restaurant_id IS NOT NULL",
    "Dealer": "dealer_id IS NOT NULL",
    "Corporate": "corporate_id IS NOT NULL",
}

async def register_admin(first_name: str, last_name: str, email: str, password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Yeni admin kaydı oluşturur (birden fazla admin eklenebilir)"""
    try:
        pwd_hash = hash_pwd(password)

        query = """
            INSERT INTO system_admins (first_name, last_name, email, password_hash)
            VALUES ($1, $2, $3, $4)
            RETURNING id, first_name, last_name, email, created_at;
        """
        row = await db.fetch_one(query, first_name, last_name, email.lower(), pwd_hash)

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
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "created_at": row[4],
            }

        return data, None

    except Exception as e:
        return None, str(e)

async def get_all_jobs(
    limit: int = 50,
    offset: int = 0,
    delivery_type: str | None = None,
    job_type: Literal["User", "Restaurant", "Dealer", "Corporate"] | None = None
) -> Tuple[Optional[list], Optional[str]]:
    try:
        filters = []
        params = []
        i = 1

        if delivery_type:
            filters.append(f"j.delivery_type = ${i}")
            params.append(delivery_type)
            i += 1

        job_filter_sql = ""
        if job_type and job_type != "User":
            job_filter = JOB_TYPE_FILTERS.get(job_type)
            if job_filter:
                filters.append(job_filter)

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

        params.extend([limit, offset])

        jobs: list[dict[str, Any]] = []

        if job_type == "User":
            user_query = f"""
                SELECT
                    j.id,
                    j.delivery_type AS "deliveryType",
                    j.carrier_type AS "carrierType",
                    j.vehicle_type AS "vehicleType",
                    j.pickup_address AS "pickupAddress",
                    j.dropoff_address AS "dropoffAddress",
                    j.special_notes AS "specialNotes",
                    j.total_price AS "totalPrice",
                    j.payment_method AS "paymentMethod",
                    j.created_at AS "createdAt",
                    j.image_file_ids AS "imageFileIds",
                    j.delivery_date AS "deliveryDate",
                    j.delivery_time AS "deliveryTime",
                    j.pickup_coordinates AS "pickupCoordinates",
                    j.dropoff_coordinates AS "dropoffCoordinates"
                FROM user_jobs j
                {where_clause}
                ORDER BY j.created_at DESC
                LIMIT ${i} OFFSET ${i + 1};
            """

            user_rows = await db.fetch_all(user_query, *params)
            return user_rows, None

        admin_query = f"""
            SELECT
                j.id,
                j.delivery_type AS "deliveryType",
                j.carrier_type AS "carrierType",
                j.vehicle_type AS "vehicleType",
                j.pickup_address AS "pickupAddress",
                j.dropoff_address AS "dropoffAddress",
                j.special_notes AS "specialNotes",
                j.total_price AS "totalPrice",
                j.payment_method AS "paymentMethod",
                j.created_at AS "createdAt",
                j.image_file_ids AS "imageFileIds",
                j.delivery_date AS "deliveryDate",
                j.delivery_time AS "deliveryTime",
                j.pickup_coordinates AS "pickupCoordinates",
                j.dropoff_coordinates AS "dropoffCoordinates"
            FROM admin_jobs j
            {where_clause}
            ORDER BY j.created_at DESC
            LIMIT ${i} OFFSET ${i + 1};
        """

        admin_rows = await db.fetch_all(admin_query, *params)

        user_rows = []
        if job_type is None:
            user_query = f"""
                SELECT
                    j.id,
                    j.delivery_type AS "deliveryType",
                    j.carrier_type AS "carrierType",
                    j.vehicle_type AS "vehicleType",
                    j.pickup_address AS "pickupAddress",
                    j.dropoff_address AS "dropoffAddress",
                    j.special_notes AS "specialNotes",
                    j.total_price AS "totalPrice",
                    j.payment_method AS "paymentMethod",
                    j.created_at AS "createdAt",
                    j.image_file_ids AS "imageFileIds",
                    j.delivery_date AS "deliveryDate",
                    j.delivery_time AS "deliveryTime",
                    j.pickup_coordinates AS "pickupCoordinates",
                    j.dropoff_coordinates AS "dropoffCoordinates"
                FROM user_jobs j
                ORDER BY j.created_at DESC
                LIMIT ${i} OFFSET ${i + 1};
            """
            user_rows = await db.fetch_all(user_query, *params)

        combined_rows = admin_rows + user_rows
        combined_rows.sort(key=lambda x: x["createdAt"], reverse=True)

        return combined_rows[:limit], None

    except Exception as e:
        return None, str(e)
