# /server/app/crud/token.py
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models import Token


class CRUDToken:
    def create_user_tokens(self, db: Session, user_id: int) -> Token:
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))

        now = datetime.utcnow()
        token = Token(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
            refresh_token_expires_at=int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    def get_by_access_token(self, db: Session, access_token: str) -> Token | None:
        return db.query(Token).filter(Token.access_token == access_token, Token.is_active.is_(True)).first()

    def get_by_refresh_token(self, db: Session, refresh_token: str) -> Token | None:
        return db.query(Token).filter(Token.refresh_token == refresh_token, Token.is_active.is_(True)).first()

    def revoke_all_user_tokens(self, db: Session, user_id: int) -> None:
        db.query(Token).filter(Token.user_id == user_id).update({"is_active": False})
        db.commit()

    def revoke_token(self, db: Session, token: Token) -> None:
        token.is_active = False
        db.add(token)
        db.commit()


token = CRUDToken()
