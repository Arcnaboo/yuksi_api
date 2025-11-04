from fastapi import HTTPException, status
from datetime import datetime
from ..utils.database_async import fetch_all, fetch_one
from ..models.restaurant_menu_model import CreateMenuReq, UpdateMenuReq, MenuResponse

TABLE = "restaurant_menus"

# -------------------------------
# CREATE
# -------------------------------
async def create(restaurant_id: str, req: CreateMenuReq):
    query = f"""
        INSERT INTO {TABLE} (name, info, price, image_url, restaurant_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, info, price, image_url, restaurant_id;
    """
    row = await fetch_one(query, req.name, req.info, req.price, req.image_url, restaurant_id)
    if not row:
        raise HTTPException(status_code=500, detail="Menü oluşturulamadı.")
    data = dict(row)
    data["id"] = str(data["id"])
    data["restaurant_id"] = str(data["restaurant_id"])
    return MenuResponse(**data)

# -------------------------------
# GET ALL
# -------------------------------
async def get_all(restaurant_id: str):
    query = f"""
        SELECT id, name, info, price, image_url, restaurant_id
        FROM {TABLE}
        WHERE restaurant_id = $1
        ORDER BY created_at DESC;
    """
    rows = await fetch_all(query, restaurant_id)
    return [MenuResponse(**{**dict(row), "id": str(row["id"]), "restaurant_id": str(row["restaurant_id"])}) for row in rows]

# -------------------------------
# GET ONE
# -------------------------------
async def get_one(restaurant_id: str, menu_id: str):
    query = f"""
        SELECT id, name, info, price, image_url, restaurant_id
        FROM {TABLE}
        WHERE id = $1 AND restaurant_id = $2;
    """
    row = await fetch_one(query, menu_id, restaurant_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı.")
    data = dict(row)
    data["id"] = str(data["id"])
    data["restaurant_id"] = str(data["restaurant_id"])
    return MenuResponse(**data)

# -------------------------------
# UPDATE
# -------------------------------
async def update(restaurant_id: str, menu_id: str ,req: UpdateMenuReq):
    # Menü var mı kontrolü
    check_query = f"SELECT id FROM {TABLE} WHERE id = $1 AND restaurant_id = $2;"
    exists = await fetch_one(check_query, menu_id, restaurant_id)
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı.")

    query = f"""
        UPDATE {TABLE}
        SET 
            name = $1,
            info = $2,
            price = $3,
            image_url = $4,
            updated_at = $5
        WHERE id = $6 AND restaurant_id = $7
        RETURNING id, name, info, price, image_url, restaurant_id;
    """
    row = await fetch_one(
        query,
        req.name,
        req.info,
        req.price,
        req.image_url,
        datetime.utcnow(),
        menu_id,
        restaurant_id,
    )
    if not row:
        raise HTTPException(status_code=500, detail="Menü güncellenemedi.")
    data = dict(row)
    data["id"] = str(data["id"])
    data["restaurant_id"] = str(data["restaurant_id"])
    return MenuResponse(**data)
# -------------------------------
# DELETE
# -------------------------------
async def delete(restaurant_id: str, menu_id: str):
    query = f"""
        DELETE FROM {TABLE}
        WHERE id = $1 AND restaurant_id = $2
        RETURNING id;
    """
    row = await fetch_one(query, menu_id, restaurant_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı veya silinemedi.")
    return {"detail": "Menü başarıyla silindi."}
