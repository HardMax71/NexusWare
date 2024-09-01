from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import chat as chat_crud
from app.models.user import User
from public_api.shared_schemas import ChatCreate, ChatResponse, ChatListResponse, MessageCreate, \
    ChatMessageListResponse, MessageResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def create_chat(
        chat: ChatCreate,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    if chat.user2_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot create chat with yourself")
    db_chat = chat_crud.create_chat(db, current_user.id, chat.user2_id)
    return ChatResponse.model_validate(db_chat)


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
        chat_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    chat = chat_crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatResponse.model_validate(chat)


@router.get("/", response_model=ChatListResponse)
def get_user_chats(
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    chats = chat_crud.get_user_chats(db, current_user.id)
    return ChatListResponse(chats=[ChatResponse.model_validate(chat) for chat in chats])


@router.delete("/{chat_id}")
def delete_chat(
        chat_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    if chat_crud.delete_chat(db, chat_id, current_user.id):
        return {"message": "Chat deleted successfully"}
    raise HTTPException(status_code=404, detail="Chat not found")


@router.post("/{chat_id}/messages", response_model=ChatResponse)
def create_message(
        chat_id: int,
        message: MessageCreate,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    chat = chat_crud.get_chat(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat_crud.create_message(db, chat_id, current_user.id, message)
    return ChatResponse.model_validate(chat)


@router.get("/{chat_id}/messages", response_model=ChatMessageListResponse)
def get_chat_messages(
        chat_id: int,
        db: Session = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    messages = chat_crud.get_chat_messages(db, chat_id, current_user.id)
    return ChatMessageListResponse(messages=[MessageResponse.model_validate(message) for message in messages])
