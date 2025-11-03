from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class NewChatReq(BaseModel):
    receiver_id: UUID
    receiver_type: str 

class SendMessageReq(BaseModel):
    chat_id: UUID
    content: str


class ChatResponse(BaseModel):
    chat_id: UUID
    participants : list[str]
    created_at: str

class MessageResponse(BaseModel):
    message_id: UUID
    sender_type: str
    content: str
    sent_at:str
    delivered_at: Optional[str] = None
    read_at: Optional[str] = None

class ReadMessagesReq(BaseModel):
    chat_id: UUID

class ChatHistoryResponse(BaseModel):
    messages: list[MessageResponse]

