from fastapi import APIRouter, Path, Depends
from app.models.city_price_model import CityPriceBase
from app.controllers.city_price_controller import *
from app.controllers.auth_controller import require_roles

router = APIRouter(prefix="/api/admin/city-prices", tags=["City Prices"])


@router.get("", dependencies=[Depends(require_roles(["Admin"]))])
async def list_route():
    return await list_prices()


@router.get("/{price_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def get_route(price_id: str = Path(...)):
    return await get_price(price_id)


@router.post("", dependencies=[Depends(require_roles(["Admin"]))])
async def create_route(body: CityPriceBase):
    return await create_price(body.model_dump(by_alias=False))


@router.put("/{price_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def update_route(price_id: str, body: CityPriceBase):
    return await update_price(price_id, body.model_dump(exclude_unset=True, by_alias=False))


@router.delete("/{price_id}", dependencies=[Depends(require_roles(["Admin"]))])
async def delete_route(price_id: str):
    return await delete_price(price_id)
