from ..services import contact_service as svc

async def send_contact(name: str, email: str, phone: str, subject: str, message: str):
    result, err = await svc.create_contact_message(name, email, phone, subject, message)
    if err:
        return {"success": False, "message": err, "data": {}}
    return {"success": True, "message": "Mesaj kaydedildi", "data": result}

async def get_contact_list(limit: int = 50, offset: int = 0):
    result, err = await svc.get_all_contact_messages(limit, offset)
    if err:
        return {"success": False, "message": err, "data": []}
    return {"success": True, "message": "Mesajlar getirildi", "data": result}

async def delete_contact(contact_id : int):
    err = await svc.delete_contact_message(contact_id)
    if err:
        return{"success": False, "message": err , "data":{}}
    return {"success": True, "message": "Mesaj silindi", "data": {}}
     

