from fastapi import APIRouter, Depends, Form
from ..models.jobs_model import JobStatusUpdateReq
from ..controllers import auth_controller, jobs_controller

router = APIRouter(prefix="/driver/jobs")

@router.get("/available")
def available_jobs(driver=Depends(auth_controller.get_current_driver)):
    return jobs_controller.available_jobs()

@router.post("/accept")
def accept_job(job_id: str = Form(...), driver=Depends(auth_controller.get_current_driver)):
    return jobs_controller.accept_job(driver, job_id)

@router.post("/update")
def update_job(req: JobStatusUpdateReq, driver=Depends(auth_controller.get_current_driver)):
    return jobs_controller.update_job(driver, req.job_id, req.status)

@router.get("")
def my_jobs(driver=Depends(auth_controller.get_current_driver)):
    return jobs_controller.my_jobs(driver)
