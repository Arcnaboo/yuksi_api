from ..services import jobs_service

async def available_jobs():
    rows = await jobs_service.list_available_jobs()
    return {"success": True, "message": "Available jobs", "data": rows}

async def accept_job(driver, job_id: str):
    ok = await jobs_service.accept_job(driver["id"], job_id)
    if not ok:
        return {"success": False, "message": "Job no longer available", "data": {}}
    return {"success": True, "message": "Job accepted", "data": {}}

async def update_job(driver, job_id: str, status: str):
    ok, err = await jobs_service.update_job_status(driver["id"], job_id, status)
    if not ok:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Job updated", "data": {}}

async def my_jobs(driver):
    rows = await jobs_service.my_jobs(driver["id"])
    return {"success": True, "message": "My jobs", "data": rows}
