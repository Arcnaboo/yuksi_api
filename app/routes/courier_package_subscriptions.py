from fastapi import APIRouter, Depends, Path, Query
from app.controllers import courier_package_subscription_controller as ctrl
from app.models.courier_package_subscription_model import CourierPackageSubscriptionCreate, CourierPackageSubscriptionUpdate
from app.controllers.auth_controller import require_roles
from uuid import UUID

router = APIRouter(prefix="/api/courier/package-subscriptions", tags=["Courier Package Subscriptions"])

@router.post(
    "",
    summary="Create Courier Package Subscription",
    description="Creates a new courier package subscription.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def create_subscription(body: CourierPackageSubscriptionCreate):
    return await ctrl.create_subscription(body.dict())

@router.get(
    "",
    summary="List Courier Package Subscriptions",
    description="Lists all courier package subscriptions.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def get_subscriptions(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await ctrl.list_subscriptions(limit, offset)

@router.get(
    "/{subscription_id}",
    summary="Get Courier Package Subscription by UUID",
    description="Returns a single courier package subscription by its UUID.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def get_subscription(subscription_id: UUID = Path(..., description="The UUID of the Subscription")):
    return await ctrl.get_subscription_by_id(subscription_id)

@router.get(
    "courier/{courier_id}",
    summary="Get Courier Package Subscription by Courier ID",
    description="Returns a courier package subscription by the courier's ID.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def get_subscription_by_courier(courier_id: UUID = Path(..., description="The UUID of the Courier")):
    return await ctrl.get_subscription_by_courier_id(courier_id)

@router.put(
    "/{subscription_id}",
    summary="Update Courier Package Subscription",
    description="Updates a courier package subscription.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def update_subscription(
    subscription_id: UUID = Path(..., description="The UUID of the Subscription"),
    body: CourierPackageSubscriptionUpdate = ...,
):
    return await ctrl.update_subscription(subscription_id, body.dict(exclude_unset=True))

@router.delete(
    "/{subscription_id}",
    summary="Delete Courier Package Subscription",
    description="Deletes a courier package subscription.",
    dependencies=[Depends(require_roles(["Admin", "Courier"]))],
)
async def delete_subscription(subscription_id: UUID = Path(..., description="The UUID of the Subscription")):
    return await ctrl.delete_subscription(subscription_id)