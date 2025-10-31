from typing import Dict, Any, List, Tuple, Optional
from app.utils.database_async import fetch_all, fetch_one, execute
import json


# --- CREATE ---
async def admin_create_job(data: Dict[str, Any]) -> Tuple[bool, str | None]:
    """Admin tarafından manuel yük oluşturma servisi"""
    try:
        query = """
        INSERT INTO admin_jobs (
            delivery_type, carrier_type, vehicle_type,
            pickup_address, pickup_coordinates,
            dropoff_address, dropoff_coordinates,
            special_notes, campaign_code,
            extra_services, extra_services_total,
            total_price, payment_method, image_file_ids, created_by_admin
        )
        VALUES (
            $1,$2,$3,$4,$5,$6,$7,
            $8,$9,$10,$11,$12,$13,$14,TRUE
        )
        RETURNING id;
        """

        params = [
            data["deliveryType"],
            data["carrierType"],
            data["vehicleType"],
            data["pickupAddress"],
            json.dumps(data["pickupCoordinates"]),
            data["dropoffAddress"],
            json.dumps(data["dropoffCoordinates"]),
            data.get("specialNotes"),
            data.get("campaignCode"),
            json.dumps(data.get("extraServices", [])),
            data.get("extraServicesTotal", 0),
            data["totalPrice"],
            data["paymentMethod"],
            json.dumps(data.get("imageFileIds", [])),  # ✅ artık "imageFileIds"
        ]

        row = await fetch_one(query, *params)
        if not row:
            return False, "Kayıt başarısız oldu."

        return True, row["id"] if isinstance(row, dict) else row[0]

    except Exception as e:
        return False, str(e)


# --- READ (liste) ---
async def admin_get_jobs(limit: int = 50, offset: int = 0, delivery_type: str | None = None) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """Admin tarafından yük listesini getirir"""
    try:
        filters = []
        params = []
        i = 1

        if delivery_type:
            filters.append(f"delivery_type = ${i}")
            params.append(delivery_type)
            i += 1

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        params.extend([limit, offset])

        query = f"""
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
            j.image_file_ids AS "imageFileIds"
        FROM admin_jobs j
        {where_clause}
        ORDER BY j.created_at DESC
        LIMIT ${i} OFFSET ${i + 1};
        """

        rows = await fetch_all(query, *params)
        return True, rows

    except Exception as e:
        return False, str(e)


# --- READ RESTAURANT JOBS (Admin görünümü) ---
async def admin_get_restaurant_jobs(
    limit: int = 50, 
    offset: int = 0, 
    delivery_type: str | None = None,
    restaurant_id: str | None = None
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """Admin tarafından tüm restaurantların yüklerini getirir"""
    try:
        filters = []
        params = []
        i = 1

        # Sadece restaurant tarafından oluşturulan yükler (restaurant_id NULL olmayan)
        filters.append("restaurant_id IS NOT NULL")
        
        if restaurant_id:
            filters.append(f"j.restaurant_id = ${i}")
            params.append(str(restaurant_id))
            i += 1

        if delivery_type:
            filters.append(f"j.delivery_type = ${i}")
            params.append(delivery_type)
            i += 1

        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        params.extend([limit, offset])

        query = f"""
        SELECT
            j.id,
            j.delivery_type AS "deliveryType",
            j.carrier_type AS "carrierType",
            j.vehicle_type AS "vehicleType",
            j.pickup_address AS "pickupAddress",
            j.pickup_coordinates AS "pickupCoordinates",
            j.dropoff_address AS "dropoffAddress",
            j.dropoff_coordinates AS "dropoffCoordinates",
            j.special_notes AS "specialNotes",
            j.total_price AS "totalPrice",
            j.payment_method AS "paymentMethod",
            j.created_at AS "createdAt",
            j.image_file_ids AS "imageFileIds",
            j.restaurant_id AS "restaurantId",
            r.name AS "restaurantName",
            r.email AS "restaurantEmail"
        FROM admin_jobs j
        LEFT JOIN restaurants r ON j.restaurant_id = r.id
        {where_clause}
        ORDER BY j.created_at DESC
        LIMIT ${i} OFFSET ${i + 1};
        """

        rows = await fetch_all(query, *params)
        return True, rows

    except Exception as e:
        return False, str(e)


# --- UPDATE ---
async def admin_update_job(job_id: str, fields: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Admin tarafından yük güncelleme servisi"""
    try:
        if not fields:
            return False, "Güncellenecek alan yok."

        update_fields = []
        params = []
        i = 1

        mapping = {
            "deliveryType": "delivery_type",
            "carrierType": "carrier_type",
            "vehicleType": "vehicle_type",
            "pickupAddress": "pickup_address",
            "pickupCoordinates": "pickup_coordinates",
            "dropoffAddress": "dropoff_address",
            "dropoffCoordinates": "dropoff_coordinates",
            "specialNotes": "special_notes",
            "campaignCode": "campaign_code",
            "extraServices": "extra_services",
            "extraServicesTotal": "extra_services_total",
            "totalPrice": "total_price",
            "paymentMethod": "payment_method",
            "imageFileIds": "image_file_ids"
        }

        for key, value in fields.items():
            column = mapping.get(key, key.lower())
            if column in ["pickup_coordinates", "dropoff_coordinates", "extra_services", "image_file_ids"]:
                update_fields.append(f"{column} = ${i}")
                params.append(json.dumps(value))
            else:
                update_fields.append(f"{column} = ${i}")
                params.append(value)
            i += 1

        params.append(job_id)

        query = f"""
            UPDATE admin_jobs
            SET {', '.join(update_fields)}
            WHERE id = ${i};
        """
        result = await execute(query, *params)
        if result.endswith(" 0"):
            return False, "Kayıt bulunamadı."
        return True, None

    except Exception as e:
        return False, str(e)


# --- DELETE ---
async def admin_delete_job(job_id: str) -> Tuple[bool, Optional[str]]:
    """Admin tarafından yük silme servisi"""
    try:
        result = await execute("DELETE FROM admin_jobs WHERE id = $1;", job_id)
        if result.endswith(" 0"):
            return False, "Silinecek kayıt bulunamadı."
        return True, None
    except Exception as e:
        return False, str(e)
