from pydantic import BaseModel
from typing import Optional

class SupportTicketCreate(BaseModel):
    subject: str
    message: str

class SupportTicketReply(BaseModel):
    reply: str
