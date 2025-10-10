from pydantic import BaseModel

class JobStatusUpdateReq(BaseModel):
    job_id: str
    status: str  # picked_up | arrived | delivered
