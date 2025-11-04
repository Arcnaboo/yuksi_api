from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime
from ..utils.database_async import fetch_all, fetch_one
from ..models.restaurant_menu_model import CreateMenuReq, UpdateMenuReq, MenuResponse

TABLE = "restaurant_menus"

# -------------------------------
# CREATE
# -------------------------------
async def create(req: CreateMenuReq):
    query = f"""
        INSERT INTO {TABLE} (name, menu_info, price, image_url, restaurant_id)
        VALUES (:name, :menu_info, :price, :image_url, :restaurant_id)
        RETURNING id, name, menu_info AS info, price, image_url, restaurant_id AS restourant_id, created_at, updated_at;
    """
    values = {
        "name": req.name,
        "menu_info": req.info,
        "price": req.price,
        "image_url": req.image_url,
        "restaurant_id": req.restourant_id
    }
    row = await fetch_one(query, values)
    if not row:
        raise HTTPException(status_code=500, detail="Menü oluşturulamadı.")
    return MenuResponse(**row)

# -------------------------------
# GET ALL
# -------------------------------
async def get_all(restaurant_id: UUID):
    query = f"""
        SELECT id, name, menu_info AS info, price, image_url, restaurant_id AS restourant_id, created_at, updated_at
        FROM {TABLE}
        WHERE restaurant_id = :restaurant_id
        ORDER BY created_at DESC;
    """
    rows = await fetch_all(query, {"restaurant_id": restaurant_id})
    return [MenuResponse(**row) for row in rows]

# -------------------------------
# GET ONE
# -------------------------------
async def get_one(restaurant_id: UUID, menu_id: UUID):
    query = f"""
        SELECT id, name, menu_info AS info, price, image_url, restaurant_id AS restourant_id, created_at, updated_at
        FROM {TABLE}
        WHERE id = :menu_id AND restaurant_id = :restaurant_id;
    """
    row = await fetch_one(query, {"menu_id": menu_id, "restaurant_id": restaurant_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı.")
    return MenuResponse(**row)

# -------------------------------
# UPDATE
# -------------------------------
async def update(req: UpdateMenuReq):
    # mevcut menü var mı kontrolü
    check_query = f"SELECT id FROM {TABLE} WHERE id = :id AND restaurant_id = :restaurant_id;"
    exists = await fetch_one(check_query, {"id": req.id, "restaurant_id": req.restourant_id})
    if not exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı.")

    query = f"""
        UPDATE {TABLE}
        SET 
            name = :name,
            menu_info = :menu_info,
            price = :price,
            image_url = :image_url,
            updated_at = :updated_at
        WHERE id = :id AND restaurant_id = :restaurant_id
        RETURNING id, name, menu_info AS info, price, image_url, restaurant_id AS restourant_id, created_at, updated_at;
    """
    values = {
        "id": req.id,
        "name": req.name,
        "menu_info": req.info,
        "price": req.price,
        "image_url": req.image_url,
        "restaurant_id": req.restourant_id,
        "updated_at": datetime.utcnow()
    }
    row = await fetch_one(query, values)
    if not row:
        raise HTTPException(status_code=500, detail="Menü güncellenemedi.")
    return MenuResponse(**row)

# -------------------------------
# DELETE
# -------------------------------
async def delete(restaurant_id: UUID, menu_id: UUID):
    query = f"""
        DELETE FROM {TABLE}
        WHERE id = :menu_id AND restaurant_id = :restaurant_id
        RETURNING id;
    """
    row = await fetch_one(query, {"menu_id": menu_id, "restaurant_id": restaurant_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menü bulunamadı veya silinemedi.")
    return {"detail": "Menü başarıyla silindi."}
