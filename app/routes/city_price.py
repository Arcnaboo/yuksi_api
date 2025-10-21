from fastapi import APIRouter, Depends
from app.controllers import city_price_controller as ctrl
from app.models.city_price_model import CityPriceCreate, CityPriceUpdate
from app.controllers.auth_controller import require_roles


router = APIRouter(prefix="/api/CityPrice", tags=["City Price"])

@router.post("/create")
async def create_city_price(data: CityPriceCreate, _claims=Depends(require_roles(["Admin"]))):
    return await ctrl.create_city_price(data.dict())

@router.get("/list")
async def list_city_prices(_claims=Depends(require_roles(["Admin"]))):
    return await ctrl.list_city_prices()

@router.put("/update/{id}")
async def update_city_price(id: int, data: CityPriceUpdate, _claims=Depends(require_roles(["Admin"]))):
    return await ctrl.update_city_price(id, {k:v for k,v in data.dict().items() if v is not None})

@router.delete("/delete/{id}")
async def delete_city_price(id: int, _claims=Depends(require_roles(["Admin"]))):
    return await ctrl.delete_city_price(id)
