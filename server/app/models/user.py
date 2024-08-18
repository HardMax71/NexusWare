# /server/app/models/user.py
import time

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    created_at = Column(Integer, default=lambda: int(time.time()))
    last_login = Column(Integer)
    password_reset_token = Column(String(255))
    password_reset_expiration = Column(Integer)

    role = relationship("Role", back_populates="users")
    assigned_tasks = relationship("Task", back_populates="assigned_user")
    task_comments = relationship("TaskComment", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")



    @property
    def permissions(self):
        return self.role.permissions if self.role else []

    @permissions.setter
    def permissions(self, new_permissions):
        if self.role:
            self.role.permissions = new_permissions
        else:
            raise ValueError("User does not have a role assigned. Cannot set permissions.")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(50), unique=True, nullable=False)
    can_read = Column(Boolean, default=False)
    can_write = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), primary_key=True)
