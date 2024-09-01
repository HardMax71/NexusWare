from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from .user import UserSanitized

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    id: int
    content: str
    sender_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatCreate(BaseModel):
    user2_id: int

class ChatResponse(BaseModel):
    id: int
    user1: UserSanitized
    user2: UserSanitized
    created_at: datetime
    last_message: MessageResponse | None = None

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

class ChatMessageListResponse(BaseModel):
    messages: List[MessageResponse]