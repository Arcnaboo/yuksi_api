from ..services import driver_service

# Deprecated 
async def save_vehicle(driver, req):
    await driver_service.upsert_vehicle(driver["id"], req.make, req.model, req.year, req.plate)
    return {"success": True, "message": "Vehicle saved", "data": {}}

async def upload_documents(driver, license_file, criminal_file, insurance_file):
    base = "https://cdn.yuksi.com/docs"
    if license_file:
        await driver_service.insert_document(driver["id"], "license", f"{base}/{driver['id']}_license.pdf")
    if criminal_file:
        await driver_service.insert_document(driver["id"], "criminal_record", f"{base}/{driver['id']}_criminal.pdf")
    if insurance_file:
        await driver_service.insert_document(driver["id"], "vehicle_insurance", f"{base}/{driver['id']}_insurance.pdf")
    return {"success": True, "message": "Documents uploaded", "data": {}}

async def list_documents(driver):
    rows = await driver_service.list_documents(driver["id"])
    return {"success": True, "message": "Documents list", "data": rows}

async def finalize_profile(driver):
    err = await driver_service.finalize_profile(driver["id"])
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Profile submitted for approval", "data": {}}

async def go_online(driver):
    ok = await driver_service.set_online(driver["id"], True)
    if ok.get("documents_not_approved", False):
        return {"success": False, "message": ok.get("message", "Tüm belgeleriniz onaylanmadan çevrimiçi olamazsınız"), "data": {}}
    if ok.get("subscription_inactive_or_expired", False):
        print("subscription inactive")
        return {"success": False, "message": "Subscription inactive or expired", "data": {}}
    if ok.get("deleted"):
        return {"success": False, "message": "Account inactive or deleted", "data": {}}

    if not ok.get("changed", False):
        return {"success": True, "message": "Already online", "data": {}}
    
    
    return {"success": True, "message": "You are online", "data": {}}

async def go_offline(driver):
    await driver_service.set_online(driver["id"], False)
    return {"success": True, "message": "You are offline", "data": {}}

async def earnings(driver):
    total = await driver_service.earnings(driver["id"])
    return {"success": True, "message": "Total earnings", "data": {"total_earnings": total}}

async def banners():
    rows = await driver_service.get_banners()
    return {"success": True, "message": "Banners", "data": rows}


async def how_many_left_works_hour(driver):
    count = await driver_service.how_many_left_works_hour(driver["id"])
    return {"success": True, "message": "Remaining work hours", "data": {"remaining_hours": count}}