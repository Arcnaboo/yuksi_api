from ..services import driver_service

def save_vehicle(driver, req):
    driver_service.upsert_vehicle(driver["id"], req.make, req.model, req.year, req.plate)
    return {"success": True, "message": "Vehicle saved", "data": {}}

def upload_documents(driver, license_file, criminal_file, insurance_file):
    base = "https://cdn.yuksi.com/docs"
    if license_file:
        driver_service.insert_document(driver["id"], "license", f"{base}/{driver['id']}_license.pdf")
    if criminal_file:
        driver_service.insert_document(driver["id"], "criminal_record", f"{base}/{driver['id']}_criminal.pdf")
    if insurance_file:
        driver_service.insert_document(driver["id"], "vehicle_insurance", f"{base}/{driver['id']}_insurance.pdf")
    return {"success": True, "message": "Documents uploaded", "data": {}}

def list_documents(driver):
    rows = driver_service.list_documents(driver["id"])
    return {"success": True, "message": "Documents list", "data": rows}

def finalize_profile(driver):
    err = driver_service.finalize_profile(driver["id"])
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Profile submitted for approval", "data": {}}

def go_online(driver):
    driver_service.set_online(driver["id"], True)
    return {"success": True, "message": "You are online", "data": {}}

def go_offline(driver):
    driver_service.set_online(driver["id"], False)
    return {"success": True, "message": "You are offline", "data": {}}

def earnings(driver):
    total = driver_service.earnings(driver["id"])
    return {"success": True, "message": "Total earnings", "data": {"total_earnings": total}}

def banners():
    rows = driver_service.get_banners()
    return {"success": True, "message": "Banners", "data": rows}
