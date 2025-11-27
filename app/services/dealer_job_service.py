from typing import Dict, Any, List, Tuple, Optional
from app.utils.database_async import fetch_all, fetch_one, execute
import json
from datetime import date, time


# --- CREATE ---
async def dealer_create_job(data: Dict[str, Any], dealer_id: str) -> Tuple[bool, str | None]:
    """Bayi tarafından manuel yük oluşturma servisi"""
    try:
        # Araç seçimini işle
        vehicle_product_id = None
        vehicle_type_string = None
        
        if data.get("vehicleProductId"):
            from app.services.vehicle_product_service import get_vehicle_product
            vehicle_product, error = await get_vehicle_product(data["vehicleProductId"])
            if error or not vehicle_product:
                return False, f"Araç ürünü bulunamadı: {error}"
            vehicle_product_id = data["vehicleProductId"]
            vehicle_type_string = vehicle_product.get("productTemplate", "motorcycle")
            
        elif data.get("vehicleTemplate"):
            from app.services.vehicle_product_service import find_vehicle_product_by_selection
            template = data["vehicleTemplate"]
            features = data.get("vehicleFeatures", [])
            capacity_option_id = data.get("capacityOptionId")
            
            vehicle_product, error = await find_vehicle_product_by_selection(
                template,
                features,
                capacity_option_id
            )
            
            if error or not vehicle_product:
                return False, f"Seçilen özelliklere uygun araç bulunamadı: {error}"
            
            vehicle_product_id = vehicle_product["id"]
            vehicle_type_string = template
            
        else:
            vehicle_type_string = data.get("vehicleType", "motorcycle")
        
        # Fiyat hesaplama
        total_price = data.get("totalPrice")
        
        if not total_price:
            from app.services.job_price_service import calculate_job_price
            calculated_price, error = await calculate_job_price(
                vehicle_product_id=vehicle_product_id,
                vehicle_template=vehicle_type_string,
                pickup_coords=data.get("pickupCoordinates"),
                dropoff_coords=data.get("dropoffCoordinates"),
                extra_services_total=data.get("extraServicesTotal", 0)
            )
            
            if error:
                return False, f"Fiyat hesaplanamadı: {error}"
            
            total_price = calculated_price
        
        query = """
        INSERT INTO admin_jobs (
            delivery_type, carrier_type, vehicle_type, vehicle_product_id,
            pickup_address, pickup_coordinates,
            dropoff_address, dropoff_coordinates,
            special_notes, campaign_code,
            extra_services, extra_services_total,
            total_price, payment_method, image_file_ids, 
            created_by_admin, restaurant_id, dealer_id,
            delivery_date, delivery_time
        )
        VALUES (
            $1,$2,$3,$4,$5,$6,$7,
            $8,$9,$10,$11,$12,$13,$14,FALSE,NULL,$15,
            $16,$17
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
            vehicle_type_string,
            str(vehicle_product_id) if vehicle_product_id else None,
            data["pickupAddress"],
            json.dumps(data["pickupCoordinates"]),
            data["dropoffAddress"],
            json.dumps(data["dropoffCoordinates"]),
            data.get("specialNotes"),
            data.get("campaignCode"),
            json.dumps(data.get("extraServices", [])),
            data.get("extraServicesTotal", 0),
            total_price,
            data["paymentMethod"],
            json.dumps(data.get("imageFileIds", [])),
            dealer_id,  # dealer_id
            delivery_date_obj,  # Python date objesi
            delivery_time_obj,  # Python time objesi
        ]

        row = await fetch_one(query, *params)
        if not row:
            return False, "Kayıt başarısız oldu."

        return True, row["id"] if isinstance(row, dict) else row[0]

    except Exception as e:
        return False, str(e)


# --- READ (liste) ---
async def dealer_get_jobs(dealer_id: str, limit: int = 50, offset: int = 0, delivery_type: str | None = None) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """Bayi tarafından yük listesini getirir (sadece o bayinin yükleri)"""
    try:
        filters = []
        params = [dealer_id]
        i = 2

        # Sadece bu bayinin yüklerini getir
        filters.append("dealer_id = $1")

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
async def dealer_update_job(job_id: str, dealer_id: str, fields: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Bayi tarafından yük güncelleme servisi (sadece kendi yüklerini güncelleyebilir)"""
    try:
        # Önce yükün bu bayinin olup olmadığını kontrol et
        check = await fetch_one(
            "SELECT id FROM admin_jobs WHERE id = $1 AND dealer_id = $2;",
            job_id, dealer_id
        )
        if not check:
            return False, "Bu yük size ait değil veya bulunamadı."

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

        params.extend([job_id, dealer_id])

        query = f"""
            UPDATE admin_jobs
            SET {', '.join(update_fields)}
            WHERE id = ${i} AND dealer_id = ${i + 1};
        """
        result = await execute(query, *params)
        if result.endswith(" 0"):
            return False, "Kayıt bulunamadı."
        return True, None

    except Exception as e:
        return False, str(e)


# --- DELETE ---
async def dealer_delete_job(job_id: str, dealer_id: str) -> Tuple[bool, Optional[str]]:
    """Bayi tarafından yük silme servisi (sadece kendi yüklerini silebilir)"""
    try:
        # Önce yükün bu bayinin olup olmadığını kontrol et
        check = await fetch_one(
            "SELECT id FROM admin_jobs WHERE id = $1 AND dealer_id = $2;",
            job_id, dealer_id
        )
        if not check:
            return False, "Bu yük size ait değil veya bulunamadı."

        result = await execute("DELETE FROM admin_jobs WHERE id = $1 AND dealer_id = $2;", job_id, dealer_id)
        if result.endswith(" 0"):
            return False, "Silinecek kayıt bulunamadı."
        return True, None
    except Exception as e:
        return False, str(e)

