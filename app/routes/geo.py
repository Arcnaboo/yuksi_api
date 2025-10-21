from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.geo_service import (
    list_countries, list_states_by_country, list_cities_by_state,
    get_country_by_id, get_state_by_id
)
from app.models.geo_model import CountryOut, StateOut, CityOut


router = APIRouter(prefix="/geo", tags=["Geo"])

@router.get("/countries", response_model=List[CountryOut], summary="Ülkeleri listele")
async def get_countries(q: Optional[str] = Query(None, description="İsme göre arama"),
                  limit: int = Query(50, ge=1, le=200),
                  offset: int = Query(0, ge=0)):
    return await list_countries(q=q, limit=limit, offset=offset)

@router.get("/states", response_model=List[StateOut], summary="Bir ülkenin eyalet/illerini listele")
async def get_states(country_id: int = Query(..., description="Country ID"),
               q: Optional[str] = Query(None),
               limit: int = Query(100, ge=1, le=500),
               offset: int = Query(0, ge=0)):
    # ülke var mı?
    if not get_country_by_id(country_id):
        raise HTTPException(status_code=404, detail="Country not found")
    return await list_states_by_country(country_id, q=q, limit=limit, offset=offset)

@router.get("/cities", response_model=List[CityOut], summary="Bir ilin şehirlerini/ilçelerini listele")
async def get_cities(state_id: int = Query(..., description="State ID"),
               q: Optional[str] = Query(None),
               limit: int = Query(100, ge=1, le=1000),
               offset: int = Query(0, ge=0)):
    # state var mı?
    if not get_state_by_id(state_id):
        raise HTTPException(status_code=404, detail="State not found")
    return await list_cities_by_state(state_id, q=q, limit=limit, offset=offset)
