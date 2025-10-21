from fastapi import APIRouter, Depends
from app.controllers import city_price_controller as ctrl
from app.models.city_price_model import CityPriceCreate, CityPriceUpdate
from app.controllers.auth_controller import require_roles
from app.models.city_price_model import CityPriceBase

router = APIRouter(prefix="/api/CityPrice", tags=["City Price"])

@router.get("/list", dependencies=[Depends(require_roles(["Admin"]))])
async def list_prices():
    return await ctrl.list_prices()

@router.get("/get/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def get_price(id: int):
    return await ctrl.get_price(id)

@router.post("/create", dependencies=[Depends(require_roles(["Admin"]))])
async def create_price(data: CityPriceBase):
    return await ctrl.create_price(data.model_dump())

@router.put("/update/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_price(id: int, data: CityPriceBase):
    return await ctrl.update_price(id, data.model_dump())

@router.delete("/delete/{id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_price(id: int):
    return await ctrl.delete_price(id)