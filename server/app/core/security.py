# /server/app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Dict
import uuid
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.utcnow() + expires_delta
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": subject,
        "type": token_type,
        "jti": str(uuid.uuid4())
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_access_token(subject: str) -> str:
    return create_token(
        subject,
        "access_token",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str) -> str:
    return create_token(
        subject,
        "refresh_token",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    return create_token(
        email,
        "password_reset",
        timedelta(hours=1)
    )
