from ..services import payments_service

def start_payment(driver, job_id: str):
    data, err = payments_service.start_payment_session(driver["id"], job_id)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Payment session started", "data": data}

def payment_status(driver, payment_id: str):
    row = payments_service.get_payment_status(driver["id"], payment_id)
    if not row:
        return {"success": False, "message": "Payment not found", "data": {}}
    return {"success": True, "message": "Payment status", "data": dict(row)}
