# /server/app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)

    role = relationship("Role", back_populates="users")


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions")


class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(50), unique=True, nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer,
                     ForeignKey("roles.role_id"),
                     primary_key=True)
    permission_id = Column(Integer,
                           ForeignKey("permissions.permission_id"),
                           primary_key=True)
