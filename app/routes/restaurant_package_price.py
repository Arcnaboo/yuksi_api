from fastapi import APIRouter, Depends
from app.controllers.auth_controller import require_roles
from app.controllers import restaurant_package_price_controller as ctrl
from app.models.restaurant_package_price_model import RestaurantPackagePriceBase
from uuid import UUID


router = APIRouter(prefix="/api/PackagePrice", tags=["Package Price"])

# 🔹 Admin - Fiyat ekle/güncelle
@router.post("/save", dependencies=[Depends(require_roles(["Admin"]))])
async def save_package_price(data: RestaurantPackagePriceBase):
    return await ctrl.create_or_update_price(data.model_dump())


# 📋 Admin - List all package prices
@router.get("/list", dependencies=[Depends(require_roles(["Admin"]))])
async def list_package_prices():
    from app.utils.database import db_cursor
    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT 
                    id,
                    restaurant_id,
                    unit_price,
                    min_package,
                    max_package,
                    note,
                    updated_at
                FROM restaurant_package_prices
                ORDER BY updated_at DESC;
            """)
            rows = cur.fetchall()

        return {
            "success": True,
            "message": "Package prices fetched successfully",
            "data": rows
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}

@router.put("/update/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_price(id: UUID, data: RestaurantPackagePriceBase):
    from app.utils.database import db_cursor
    try:
        with db_cursor() as cur:
            cur.execute("""
                UPDATE restaurant_package_prices
                SET unit_price = %s,
                    min_package = %s,
                    max_package = %s,
                    note = %s,
                    updated_at = now()
                WHERE id = %s
                RETURNING id;
            """, (
                data.unit_price, data.min_package, data.max_package, data.note, str(id)
            ))
            result = cur.fetchone()
        return {
            "success": True,
            "message": "Price updated successfully",
            "data": {"id": str(result[0])}
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}


# 🗑️ Delete restaurant package price
@router.delete("/delete/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_package_price(id: UUID):
    from app.utils.database import db_cursor
    try:
        with db_cursor() as cur:
            cur.execute("""
                DELETE FROM restaurant_package_prices
                WHERE id = %s
                RETURNING id;
            """, (str(id),))
            deleted = cur.fetchone()
        if not deleted:
            return {"success": False, "message": "Record not found", "data": {}}
        return {
            "success": True,
            "message": "Package price deleted successfully",
            "data": {"id": str(id)}
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}



@router.get("/my-price", dependencies=[Depends(require_roles(["Restaurant"]))])
async def get_my_price(claims: dict = Depends(require_roles(["Restaurant"]))):
    from app.utils.database import db_cursor
    restaurant_id = claims.get("userId")  # token'dan geliyor

    try:
        with db_cursor(dict_cursor=True) as cur:
            cur.execute("""
                SELECT 
                    id,
                    restaurant_id,
                    unit_price,
                    min_package,
                    max_package,
                    note,
                    updated_at
                FROM restaurant_package_prices
                WHERE restaurant_id = %s;
            """, (restaurant_id,))
            price = cur.fetchone()

        if not price:
            return {
                "success": False,
                "message": "No package price found for this restaurant",
                "data": {}
            }

        return {
            "success": True,
            "message": "Package price fetched successfully",
            "data": price
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": {}}