from fastapi import APIRouter, Body, Request
from ..models.paytr_models import PaymentRequest
from ..controllers import paytr_controller as ctrl

router = APIRouter(prefix="/api/Paytr", tags=["PayTR"])

@router.post("/Init", summary="Create payment token")
def create_payment(req: PaymentRequest = Body(...)):
    return ctrl.init_payment(req)

@router.post("/allback", summary="Handle PayTR callback")
async def callback(request: Request):
    return await ctrl.handle_callback(request)

@router.get("/Ok", summary="Successful payment")
def ok():
    return "Ödeme Başarılı"

@router.get("/Fail", summary="Failed  payment")
def fail():
    return "Ödeme Başarısız"