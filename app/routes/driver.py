from fastapi import APIRouter, UploadFile, File, Depends
from ..models.driver_model import VehicleReq
from ..controllers import auth_controller, driver_controller

router = APIRouter(prefix="/driver", tags=["Driver"])

@router.post("/vehicle")
def save_vehicle(req: VehicleReq, driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.save_vehicle(driver, req)

@router.post("/documents/upload")
def upload_docs(
    license: UploadFile | None = File(None),
    criminal_record: UploadFile | None = File(None),
    vehicle_insurance: UploadFile | None = File(None),
    driver=Depends(auth_controller.get_current_driver),
):
    return driver_controller.upload_documents(driver, license, criminal_record, vehicle_insurance)

@router.get("/documents")
def list_docs(driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.list_documents(driver)

@router.post("/profile/submit")
def finalize_profile(driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.finalize_profile(driver)

@router.post("/status/online")
def go_online(driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.go_online(driver)

@router.post("/status/offline")
def go_offline(driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.go_offline(driver)

@router.get("/earnings")
def earnings(driver=Depends(auth_controller.get_current_driver)):
    return driver_controller.earnings(driver)

@router.get("/banners")
def banners():
    return driver_controller.banners()
