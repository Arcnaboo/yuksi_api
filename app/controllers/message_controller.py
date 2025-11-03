from fastapi import HTTPException
from ..services import message_service 

async def new_chat(sender_id,sender_type,receiver_id,receiver_type):
    chat = await message_service.create_chat(sender_id,sender_type,receiver_id,receiver_type)
    if not chat:
        raise HTTPException(status_code=400, detail="Chat creation failed")
    return {"success": True, "data": chat}

async def text(sender_id,sender_type,chat_id,content):
    message = await message_service.send_message(chat_id,sender_id,sender_type,content)
    if not message:
        raise HTTPException(status_code=400, detail="Message sending failed")
    return {"success": True, "data": message}

async def fetch_chats(user_id,user_type):
    chats = await message_service.get_chats_for_user(user_id,user_type)
    return {"success": True, "data": chats}

async def fetch_undelivered(user_id,user_type):
    messages = await message_service.get_undelivered_messages(user_id,user_type)
    return {"success": True, "data": messages}

async def mark_as_read(user_id,user_type,chat_id):
    success = await message_service.mark_messages_read(user_id,user_type,chat_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to mark messages as read")
    return {"success": True, "message": "Messages marked as read"}

async def fetch_history(chat_id, user_id, user_type, limit=50):
    data = await message_service.get_chat_history(chat_id, user_id, user_type, limit)
    return {"success": True, "message": "ok", "data": {"messages": data}}