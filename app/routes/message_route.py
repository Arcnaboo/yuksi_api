from fastapi import APIRouter, Depends,Query
from uuid import UUID
from ..controllers import message_controller
from ..controllers.auth_controller import get_current_driver
from ..models.message_model import NewChatReq, SendMessageReq, ReadMessagesReq

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/new_chat")
async def new_chat(request: NewChatReq, user=Depends(get_current_driver)):
    return await message_controller.new_chat(user["id"], "driver", request.receiver_id, request.receiver_type)

@router.post("/text")
async def text(request: SendMessageReq, user=Depends(get_current_driver)):
    return await message_controller.text(user["id"], "driver", request.chat_id, request.content)

@router.get("/my_chats")
async def my_chats(user=Depends(get_current_driver)):
    return await message_controller.fetch_chats(user["id"], "driver")

@router.get("/undelivered")
async def undelivered(user=Depends(get_current_driver)):
    return await message_controller.fetch_undelivered(user["id"], "driver")

@router.post("/read")
async def mark_read(request: ReadMessagesReq, user=Depends(get_current_driver)):
    return await message_controller.mark_as_read(user["id"], "driver", request.chat_id)

@router.get("/history")
async def history(
    chat_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    user = Depends(get_current_driver),
):
    return await message_controller.fetch_history(str(chat_id), user["id"], "driver", limit)