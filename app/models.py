import psycopg2
from sqlalchemy import Column, Date, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship
from database import Base
import uuid
import enum


class RoleEnum(enum.Enum):
    admin = 'admin'
    user = 'user'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)

    tasks = relationship('Task', back_populates='owner')
    permissions = relationship('Permission', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False, index=True)
    deadline = Column(Date, index=True)
    done = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='tasks')
    permissions = relationship('Permission', back_populates='task')

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)

    user = relationship('User', back_populates='permissions')
    task = relationship('Task', back_populates='permissions')

