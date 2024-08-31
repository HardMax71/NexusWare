from typing import List

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, relationship

from app.models.chat import Chat, Message
from public_api.shared_schemas import MessageCreate


class CRUDChat:
    def create_chat(self, db: Session, user1_id: int, user2_id: int) -> Chat:
        chat = Chat(user1_id=user1_id, user2_id=user2_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    def get_user_chats(self, db: Session, user_id: int) -> List[Chat]:
        return db.query(Chat).filter(
            or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
        ).all()

    def get_chat(self, db: Session, chat_id: int, user_id: int) -> Chat | None:
        return db.query(Chat).filter(
            and_(Chat.id == chat_id, or_(Chat.user1_id == user_id, Chat.user2_id == user_id))
        ).first()

    def delete_chat(self, db: Session, chat_id: int, user_id: int) -> bool:
        chat = self.get_chat(db, chat_id, user_id)
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False

    def create_message(self, db: Session, chat_id: int, sender_id: int, message: MessageCreate) -> Message:
        db_message = Message(chat_id=chat_id, sender_id=sender_id, content=message.content)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_chat_messages(self, db: Session, chat_id: int, user_id: int) -> List[Message]:
        chat = self.get_chat(db, chat_id, user_id)
        if chat:
            return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()
        return []


chat = CRUDChat()