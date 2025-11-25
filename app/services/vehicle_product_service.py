from typing import Dict, Any, List, Tuple, Optional
from uuid import UUID
from app.utils.database_async import fetch_one, fetch_all, execute
import json


# === CREATE ===
async def create_vehicle_product(data: Dict[str, Any]) -> Tuple[Optional[UUID], Optional[str]]:
    """Yeni araç ürünü oluştur"""
    try:
        # 1. productCode benzersizlik kontrolü
        existing = await fetch_one(
            "SELECT id FROM vehicle_products WHERE product_code = $1",
            data["productCode"]
        )
        if existing:
            return None, "Bu productCode zaten kullanılıyor"
        
        # 2. Ana ürünü oluştur
        product_query = """
            INSERT INTO vehicle_products (
                product_name, product_code, product_template, vehicle_features, is_active
            )
            VALUES ($1, $2, $3, $4, TRUE)
            RETURNING id;
        """
        
        vehicle_features_json = json.dumps(data.get("vehicleFeatures", []))
        
        product_row = await fetch_one(
            product_query,
            data["productName"],
            data["productCode"],
            data["productTemplate"],
            vehicle_features_json
        )
        
        if not product_row:
            return None, "Araç ürünü oluşturulamadı"
        
        product_id = product_row["id"]
        
        # 3. Kapasite seçeneklerini oluştur
        capacity_options = data.get("capacityOptions", [])
        if not capacity_options:
            return None, "En az 1 kapasite seçeneği gereklidir"
        
        # Kapasite çakışma kontrolü (application level - ek güvenlik)
        for i, opt1 in enumerate(capacity_options):
            for j, opt2 in enumerate(capacity_options):
                if i != j:
                    min1, max1 = opt1["minWeight"], opt1["maxWeight"]
                    min2, max2 = opt2["minWeight"], opt2["maxWeight"]
                    if not (max1 <= min2 or max2 <= min1):
                        return None, f"Kapasite baremleri çakışıyor: ({min1}-{max1} kg) ve ({min2}-{max2} kg)"
        
        capacity_query = """
            INSERT INTO vehicle_capacity_options (
                vehicle_product_id, min_weight, max_weight, label
            )
            VALUES ($1, $2, $3, $4);
        """
        
        for opt in capacity_options:
            await execute(
                capacity_query,
                str(product_id),
                opt["minWeight"],
                opt["maxWeight"],
                opt["label"]
            )
        
        return product_id, None
        
    except Exception as e:
        return None, str(e)


# === LIST ===
async def list_vehicle_products(
    template: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Araç ürünlerini listele"""
    try:
        filters = []
        params = []
        i = 1
        
        if template:
            filters.append(f"vp.product_template = ${i}")
            params.append(template)
            i += 1
        
        if is_active is not None:
            filters.append(f"vp.is_active = ${i}")
            params.append(is_active)
            i += 1
        
        where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
        
        query = f"""
            SELECT 
                vp.id,
                vp.product_name,
                vp.product_code,
                vp.product_template,
                vp.vehicle_features,
                vp.is_active,
                vp.created_at,
                vp.updated_at,
                COUNT(vco.id) as capacity_count
            FROM vehicle_products vp
            LEFT JOIN vehicle_capacity_options vco ON vco.vehicle_product_id = vp.id
            {where_clause}
            GROUP BY vp.id
            ORDER BY vp.created_at DESC;
        """
        
        rows = await fetch_all(query, *params)
        
        result = []
        for row in rows:
            result.append({
                "id": row["id"],
                "productName": row["product_name"],
                "productCode": row["product_code"],
                "productTemplate": row["product_template"],
                "vehicleFeatures": row["vehicle_features"] if isinstance(row["vehicle_features"], list) else json.loads(row["vehicle_features"] or "[]"),
                "isActive": row["is_active"],
                "capacityCount": row["capacity_count"] or 0,
                "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
                "updatedAt": row["updated_at"].isoformat() if row["updated_at"] else None
            })
        
        return result, None
        
    except Exception as e:
        return None, str(e)


# === GET BY ID ===
async def get_vehicle_product(product_id: UUID) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Araç ürünü detayını getir (kapasite seçenekleri dahil)"""
    try:
        # Ana ürün bilgisi
        product_query = """
            SELECT 
                id, product_name, product_code, product_template,
                vehicle_features, is_active, created_at, updated_at
            FROM vehicle_products
            WHERE id = $1;
        """
        
        product_row = await fetch_one(product_query, str(product_id))
        
        if not product_row:
            return None, "Araç ürünü bulunamadı"
        
        # Kapasite seçenekleri
        capacity_query = """
            SELECT id, min_weight, max_weight, label
            FROM vehicle_capacity_options
            WHERE vehicle_product_id = $1
            ORDER BY min_weight ASC;
        """
        
        capacity_rows = await fetch_all(capacity_query, str(product_id))
        
        capacity_options = []
        for cap_row in capacity_rows:
            capacity_options.append({
                "id": cap_row["id"],
                "minWeight": float(cap_row["min_weight"]),
                "maxWeight": float(cap_row["max_weight"]),
                "label": cap_row["label"]
            })
        
        result = {
            "id": product_row["id"],
            "productName": product_row["product_name"],
            "productCode": product_row["product_code"],
            "productTemplate": product_row["product_template"],
            "vehicleFeatures": product_row["vehicle_features"] if isinstance(product_row["vehicle_features"], list) else json.loads(product_row["vehicle_features"] or "[]"),
            "isActive": product_row["is_active"],
            "capacityOptions": capacity_options,
            "createdAt": product_row["created_at"].isoformat() if product_row["created_at"] else None,
            "updatedAt": product_row["updated_at"].isoformat() if product_row["updated_at"] else None
        }
        
        return result, None
        
    except Exception as e:
        return None, str(e)


# === UPDATE ===
async def update_vehicle_product(
    product_id: UUID,
    data: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """Araç ürününü güncelle"""
    try:
        # Mevcut ürünü kontrol et
        existing = await fetch_one(
            "SELECT id FROM vehicle_products WHERE id = $1",
            str(product_id)
        )
        if not existing:
            return False, "Araç ürünü bulunamadı"
        
        # productCode benzersizlik kontrolü (eğer değiştiriliyorsa)
        if data.get("productCode"):
            existing_code = await fetch_one(
                "SELECT id FROM vehicle_products WHERE product_code = $1 AND id != $2",
                data["productCode"],
                str(product_id)
            )
            if existing_code:
                return False, "Bu productCode zaten kullanılıyor"
        
        # Ana ürün güncellemeleri
        update_fields = []
        params = []
        i = 1
        
        if data.get("productName") is not None:
            update_fields.append(f"product_name = ${i}")
            params.append(data["productName"])
            i += 1
        
        if data.get("productCode") is not None:
            update_fields.append(f"product_code = ${i}")
            params.append(data["productCode"])
            i += 1
        
        if data.get("productTemplate") is not None:
            update_fields.append(f"product_template = ${i}")
            params.append(data["productTemplate"])
            i += 1
        
        if data.get("vehicleFeatures") is not None:
            update_fields.append(f"vehicle_features = ${i}")
            params.append(json.dumps(data["vehicleFeatures"]))
            i += 1
        
        if data.get("isActive") is not None:
            update_fields.append(f"is_active = ${i}")
            params.append(data["isActive"])
            i += 1
        
        if update_fields:
            update_fields.append(f"updated_at = NOW()")
            params.append(str(product_id))
            
            update_query = f"""
                UPDATE vehicle_products
                SET {', '.join(update_fields)}
                WHERE id = ${i};
            """
            await execute(update_query, *params)
        
        # Kapasite seçenekleri güncelleme (eğer gönderilmişse)
        if data.get("capacityOptions") is not None:
            capacity_options = data["capacityOptions"]
            
            # Çakışma kontrolü
            for i, opt1 in enumerate(capacity_options):
                for j, opt2 in enumerate(capacity_options):
                    if i != j:
                        min1, max1 = opt1["minWeight"], opt1["maxWeight"]
                        min2, max2 = opt2["minWeight"], opt2["maxWeight"]
                        if not (max1 <= min2 or max2 <= min1):
                            return False, f"Kapasite baremleri çakışıyor: ({min1}-{max1} kg) ve ({min2}-{max2} kg)"
            
            # Eski kapasite seçeneklerini sil
            await execute(
                "DELETE FROM vehicle_capacity_options WHERE vehicle_product_id = $1",
                str(product_id)
            )
            
            # Yeni kapasite seçeneklerini ekle
            capacity_query = """
                INSERT INTO vehicle_capacity_options (
                    vehicle_product_id, min_weight, max_weight, label
                )
                VALUES ($1, $2, $3, $4);
            """
            
            for opt in capacity_options:
                await execute(
                    capacity_query,
                    str(product_id),
                    opt["minWeight"],
                    opt["maxWeight"],
                    opt["label"]
                )
        
        return True, None
        
    except Exception as e:
        return False, str(e)


# === DELETE ===
async def delete_vehicle_product(product_id: UUID) -> Tuple[bool, Optional[str]]:
    """Araç ürününü sil (aktif yüklerde kullanılıyorsa silinemez)"""
    try:
        # Aktif yük kontrolü
        active_jobs = await fetch_one(
            "SELECT COUNT(*) as count FROM admin_jobs WHERE vehicle_product_id = $1",
            str(product_id)
        )
        
        if active_jobs and active_jobs.get("count", 0) > 0:
            return False, "Bu araç tipi aktif yüklerde kullanılıyor, silinemez"
        
        # Silme işlemi (CASCADE ile capacity_options da silinir)
        result = await execute(
            "DELETE FROM vehicle_products WHERE id = $1",
            str(product_id)
        )
        
        if "0" in result:
            return False, "Araç ürünü bulunamadı"
        
        return True, None
        
    except Exception as e:
        return False, str(e)


# === FIND VEHICLE BY TEMPLATE AND FEATURES ===
async def find_vehicle_product_by_selection(
    template: str,
    features: List[str],
    capacity_option_id: Optional[UUID] = None
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Araç tipi, özellikler ve kapasiteye göre vehicle_product bulur"""
    try:
        features_json = json.dumps(features)
        
        if capacity_option_id:
            # Kapasite ID'si ile birlikte ara
            query = """
                SELECT DISTINCT vp.*
                FROM vehicle_products vp
                JOIN vehicle_capacity_options vco ON vco.vehicle_product_id = vp.id
                WHERE vp.product_template = $1
                  AND vp.vehicle_features @> $2::jsonb
                  AND vco.id = $3
                  AND vp.is_active = TRUE
                LIMIT 1;
            """
            row = await fetch_one(query, template, features_json, str(capacity_option_id))
        else:
            # Sadece template ve features ile ara
            query = """
                SELECT *
                FROM vehicle_products
                WHERE product_template = $1
                  AND vehicle_features @> $2::jsonb
                  AND is_active = TRUE
                LIMIT 1;
            """
            row = await fetch_one(query, template, features_json)
        
        if not row:
            return None, "Seçilen özelliklere uygun araç bulunamadı"
        
        return dict(row), None
        
    except Exception as e:
        return None, str(e)

