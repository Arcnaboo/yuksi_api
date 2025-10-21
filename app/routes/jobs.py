from fastapi import APIRouter, Depends, Form
from ..models.jobs_model import JobStatusUpdateReq
from ..controllers import auth_controller, jobs_controller

router = APIRouter(prefix="/driver/jobs", tags=["Jobs"])

@router.get("/available")
async def available_jobs(driver=Depends(auth_controller.get_current_driver)):
    return await jobs_controller.available_jobs()

@router.post("/accept")
async def accept_job(job_id: str = Form(...), driver=Depends(auth_controller.get_current_driver)):
    return await jobs_controller.accept_job(driver, job_id)

@router.post("/update")
async def update_job(req: JobStatusUpdateReq, driver=Depends(auth_controller.get_current_driver)):
    return await jobs_controller.update_job(driver, req.job_id, req.status)

@router.get("")
async def my_jobs(driver=Depends(auth_controller.get_current_driver)):
    return await jobs_controller.my_jobs(driver)
