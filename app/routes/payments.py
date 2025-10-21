from fastapi import APIRouter, Depends, Form
from ..controllers import auth_controller, payments_controller

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/start")
async def start(job_id: str = Form(...), driver=Depends(auth_controller.get_current_driver)):
    return await payments_controller.start_payment(driver, job_id)

@router.get("/status")
async def status(payment_id: str, driver=Depends(auth_controller.get_current_driver)):
    return await payments_controller.payment_status(driver, payment_id)
