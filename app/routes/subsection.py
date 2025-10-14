from fastapi import APIRouter, Path, Body
from ..models.subsection_model import (
    CreateSubSectionRequest,
    UpdateSubSectionRequest,
)
from ..controllers import subsection_controller as ctrl

router = APIRouter(prefix="/api/SubSection", tags=["SubSection"])

@router.get("/", summary="Get all subsections")
def get_all():
    return ctrl.get_all()

@router.get("/{id}", summary="Get subsection by ID")
def get_by_id(id: int = Path(...)):
    return ctrl.get_by_id(id)

@router.post("/", summary="Create new subsection")
def create(req: CreateSubSectionRequest = Body(...)):
    return ctrl.create(req)

@router.put("/{id}", summary="Update subsection")
def update(id: int = Path(...), req: UpdateSubSectionRequest = Body(...)):
    return ctrl.update(id, req)

@router.delete("/{id}", summary="Delete subsection")
def delete(id: int = Path(...)):
    return ctrl.delete(id)
