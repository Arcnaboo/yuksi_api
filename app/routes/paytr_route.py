from fastapi import APIRouter, Body, Request
from ..models.paytr_models import PaymentRequest
from ..controllers import paytr_controller as ctrl

router = APIRouter(prefix="/api/Paytr", tags=["PayTR"])

@router.post("/Init", summary="Create payment token")
def create_payment(req: PaymentRequest = Body(...)):
    return ctrl.init_payment(req)

@router.post("/Callback", summary="Handle PayTR callback")
async def callback(request: Request):
    return await ctrl.handle_callback(request)
