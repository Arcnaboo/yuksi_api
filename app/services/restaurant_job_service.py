from typing import Dict, Any, List, Tuple, Optional
from app.utils.database_async import fetch_all, fetch_one, execute
import json
from datetime import date, time


# --- CREATE ---
async def restaurant_create_job(data: Dict[str, Any], restaurant_id: Optional[str]) -> Tuple[bool, str | None]:
    """Restaurant tarafından manuel yük oluşturma servisi"""
    try:
        # Restaurant ID zorunlu kontrolü
        if not restaurant_id:
            return False, "Restaurant ID bulunamadı."
        
        # Paket kontrolü - Restoranın kalan paketi var mı?
        package_info = await fetch_one("""
            SELECT max_package
            FROM restaurant_package_prices
            WHERE restaurant_id = $1
        """, restaurant_id)
        
        if package_info and package_info.get("max_package") is not None:
            max_package = package_info.get("max_package")
            # Teslim edilmiş paket sayısını say
            delivered_result = await fetch_one("""
                SELECT COUNT(*) as delivered_count
                FROM orders
                WHERE restaurant_id = $1
                  AND type = 'paket_servis'
                  AND status = 'teslim_edildi'
            """, restaurant_id)
            delivered_count = delivered_result.get("delivered_count", 0) if delivered_result else 0
            
            # Kalan paket kontrolü
            remaining_packages = max_package - delivered_count
            if remaining_packages <= 0:
                return False, f"Paket hakkınız tükenmiş. Kalan paket: 0, Maksimum paket: {max_package}, Teslim edilen: {delivered_count}"
        
        query = """
        INSERT INTO admin_jobs (
            delivery_type, carrier_type, vehicle_type,
            pickup_address, pickup_coordinates,
            dropoff_address, dropoff_coordinates,
            special_notes, campaign_code,
            extra_services, extra_services_total,
            total_price, payment_method, image_file_ids, 
            created_by_admin, restaurant_id,
            delivery_date, delivery_time
        )
        VALUES (
            $1,$2,$3,$4,$5,$6,$7,
            $8,$9,$10,$11,$12,$13,$14,$15,$16,
            $17,$18
        )
        RETURNING id;
        """

        # deliveryDate ve deliveryTime'i Python datetime objelerine dönüştür
        delivery_date_obj = None
        delivery_time_obj = None
        
        if data.get("deliveryDate"):
            try:
                # DD.MM.YYYY formatını parse et
                date_str = data["deliveryDate"].strip()
                if "." in date_str:
                    parts = date_str.split(".")
                    if len(parts) == 3:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        delivery_date_obj = date(year, month, day)
                    else:
                        delivery_date_obj = None
                else:
                    # YYYY-MM-DD formatını da destekle
                    delivery_date_obj = date.fromisoformat(date_str)
            except (ValueError, TypeError, IndexError):
                delivery_date_obj = None
        
        if data.get("deliveryTime"):
            try:
                # HH:MM formatını time objesine çevir
                time_parts = data["deliveryTime"].split(":")
                if len(time_parts) >= 2:
                    delivery_time_obj = time(int(time_parts[0]), int(time_parts[1]))
                else:
                    delivery_time_obj = None
            except (ValueError, TypeError, IndexError):
                delivery_time_obj = None
        
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
            json.dumps(data.get("imageFileIds", [])),
            False,  # created_by_admin = FALSE
            str(restaurant_id),  # UUID string olarak kaydet
            delivery_date_obj,  # Python date objesi
            delivery_time_obj,  # Python time objesi
        ]

        row = await fetch_one(query, *params)
        if not row:
            return False, "Kayıt başarısız oldu."
        
        job_id = row["id"] if isinstance(row, dict) else row[0]
        
        # Paket sayısını azalt - Yeni bir order oluştur (paket_servis tipinde, teslim_edildi durumunda)
        # Bu order sadece paket sayısını azaltmak için
        if package_info and package_info.get("max_package") is not None:
            from app.services.order_service import generate_order_code
            
            # Order kodu oluştur
            order_code = await generate_order_code()
            
            # Yük için bir order oluştur (paket_servis tipinde, teslim_edildi durumunda)
            # Bu order sadece paket sayısını azaltmak için
            await execute("""
                INSERT INTO orders (
                    restaurant_id, code, type, status, amount, 
                    customer, phone, address, delivery_address,
                    pickup_lat, pickup_lng, dropoff_lat, dropoff_lng,
                    carrier_type, vehicle_type,
                    created_at, updated_at
                )
                VALUES (
                    $1, $2, 'paket_servis', 'teslim_edildi', 0,
                    'Restaurant Yük', '0000000000', 'Yük Teslimatı', 'Yük Teslimatı',
                    0, 0, 0, 0,
                    'kurye', '2_teker_motosiklet',
                    NOW(), NOW()
                )
            """, restaurant_id, order_code)

        return True, job_id

    except Exception as e:
        return False, str(e)


# --- READ (liste) ---
async def restaurant_get_jobs(limit: int = 50, offset: int = 0, delivery_type: str | None = None, restaurant_id: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """Restaurant tarafından yük listesini getirir (sadece kendi kayıtları)"""
    try:
        filters = []
        params = []
        i = 1

        # Restaurant sadece kendi kayıtlarını görsün (ZORUNLU)
        if restaurant_id:
            filters.append(f"restaurant_id = ${i}")
            params.append(str(restaurant_id))
            i += 1
        else:
            # Restaurant ID yoksa boş liste döndür
            return True, []

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
            j.pickup_coordinates AS "pickupCoordinates",
            j.dropoff_address AS "dropoffAddress",
            j.dropoff_coordinates AS "dropoffCoordinates",
            j.special_notes AS "specialNotes",
            j.total_price AS "totalPrice",
            j.payment_method AS "paymentMethod",
            j.created_at AS "createdAt",
            j.image_file_ids AS "imageFileIds",
            j.delivery_date AS "deliveryDate",
            j.delivery_time AS "deliveryTime"
        FROM admin_jobs j
        {where_clause}
        ORDER BY j.created_at DESC
        LIMIT ${i} OFFSET ${i + 1};
        """

        rows = await fetch_all(query, *params)
        
        # Tarih ve saat formatlarını düzenle (DD.MM.YYYY ve HH:MM)
        formatted_rows = []
        for row in rows:
            row_dict = dict(row) if not isinstance(row, dict) else row
            if row_dict.get("deliveryDate"):
                row_dict["deliveryDate"] = row_dict["deliveryDate"].strftime("%d.%m.%Y")
            if row_dict.get("deliveryTime"):
                row_dict["deliveryTime"] = row_dict["deliveryTime"].strftime("%H:%M")
            formatted_rows.append(row_dict)
        
        return True, formatted_rows

    except Exception as e:
        return False, str(e)


# --- UPDATE ---
async def restaurant_update_job(job_id: str, fields: Dict[str, Any], restaurant_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Restaurant tarafından yük güncelleme servisi (sadece kendi kayıtları)"""
    try:
        if not fields:
            return False, "Güncellenecek alan yok."

        # Restaurant ID zorunlu
        if not restaurant_id:
            return False, "Restaurant ID bulunamadı."
        
        # Önce sahiplik kontrolü
        check_query = "SELECT restaurant_id FROM admin_jobs WHERE id = $1;"
        job = await fetch_one(check_query, job_id)
        
        if not job:
            return False, "Kayıt bulunamadı."
        
        # asyncpg Record objesi dictionary gibi davranır
        job_restaurant_id = job.get("restaurant_id") or job["restaurant_id"] if "restaurant_id" in job else None
        
        # UUID karşılaştırması - her ikisini de string'e çevir ve küçük harfe çevir
        job_restaurant_id_str = str(job_restaurant_id).lower().strip() if job_restaurant_id else None
        restaurant_id_str = str(restaurant_id).lower().strip() if restaurant_id else None
        
        # Restaurant sadece kendi kayıtlarını güncelleyebilir
        if not job_restaurant_id_str or not restaurant_id_str:
            return False, f"Bu yükü güncelleme yetkiniz yok. Job restaurant_id: {job_restaurant_id_str}, Your restaurant_id: {restaurant_id_str}"
        
        if job_restaurant_id_str != restaurant_id_str:
            return False, f"Bu yükü güncelleme yetkiniz yok. Job restaurant_id: {job_restaurant_id_str}, Your restaurant_id: {restaurant_id_str}"

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
            "imageFileIds": "image_file_ids",
            "deliveryDate": "delivery_date",
            "deliveryTime": "delivery_time"
        }

        for key, value in fields.items():
            column = mapping.get(key, key.lower())
            if column in ["pickup_coordinates", "dropoff_coordinates", "extra_services", "image_file_ids"]:
                update_fields.append(f"{column} = ${i}")
                params.append(json.dumps(value))
            elif column == "delivery_date":
                # deliveryDate string'ini Python date objesine çevir (DD.MM.YYYY veya YYYY-MM-DD)
                if value:
                    try:
                        date_str = str(value).strip()
                        if "." in date_str:
                            parts = date_str.split(".")
                            if len(parts) == 3:
                                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                                params.append(date(year, month, day))
                            else:
                                params.append(None)
                        else:
                            params.append(date.fromisoformat(date_str))
                    except (ValueError, TypeError, IndexError):
                        params.append(None)
                else:
                    params.append(None)
                update_fields.append(f"{column} = ${i}")
            elif column == "delivery_time":
                # deliveryTime string'ini Python time objesine çevir
                if value:
                    try:
                        time_parts = value.split(":")
                        if len(time_parts) >= 2:
                            params.append(time(int(time_parts[0]), int(time_parts[1])))
                        else:
                            params.append(None)
                    except (ValueError, TypeError, IndexError):
                        params.append(None)
                else:
                    params.append(None)
                update_fields.append(f"{column} = ${i}")
            else:
                update_fields.append(f"{column} = ${i}")
                params.append(value)
            i += 1

        params.append(job_id)
        i += 1
        params.append(restaurant_id_str if restaurant_id_str else restaurant_id)

        query = f"""
            UPDATE admin_jobs
            SET {', '.join(update_fields)}
            WHERE id = ${i-1} AND restaurant_id = ${i};
        """
        result = await execute(query, *params)
        if result.endswith(" 0"):
            return False, "Kayıt bulunamadı."
        return True, None

    except Exception as e:
        return False, str(e)


# --- DELETE ---
async def restaurant_delete_job(job_id: str, restaurant_id: Optional[str]) -> Tuple[bool, Optional[str]]:
    """Restaurant tarafından yük silme servisi (sadece kendi kayıtları)"""
    try:
        # Restaurant ID zorunlu
        if not restaurant_id:
            return False, "Restaurant ID bulunamadı."
        
        # Önce sahiplik kontrolü
        check_query = "SELECT restaurant_id FROM admin_jobs WHERE id = $1;"
        job = await fetch_one(check_query, job_id)
        
        if not job:
            return False, "Silinecek kayıt bulunamadı."
        
        # asyncpg Record objesi dictionary gibi davranır
        job_restaurant_id = job.get("restaurant_id") or job["restaurant_id"] if "restaurant_id" in job else None
        
        # UUID karşılaştırması - her ikisini de string'e çevir ve küçük harfe çevir
        job_restaurant_id_str = str(job_restaurant_id).lower().strip() if job_restaurant_id else None
        restaurant_id_str = str(restaurant_id).lower().strip() if restaurant_id else None
        
        # Restaurant sadece kendi kayıtlarını silebilir
        if not job_restaurant_id_str or not restaurant_id_str:
            return False, f"Bu yükü silme yetkiniz yok. Job restaurant_id: {job_restaurant_id_str}, Your restaurant_id: {restaurant_id_str}"
        
        if job_restaurant_id_str != restaurant_id_str:
            return False, f"Bu yükü silme yetkiniz yok. Job restaurant_id: {job_restaurant_id_str}, Your restaurant_id: {restaurant_id_str}"

        result = await execute("DELETE FROM admin_jobs WHERE id = $1 AND restaurant_id = $2;", job_id, restaurant_id_str if restaurant_id_str else restaurant_id)
        if result.endswith(" 0"):
            return False, "Silinecek kayıt bulunamadı."
        return True, None
    except Exception as e:
        return False, str(e)

