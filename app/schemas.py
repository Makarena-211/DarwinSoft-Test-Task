from pydantic import BaseModel
from datetime import date
from uuid import UUID
import enum
from typing import Optional

class RoleEnum(str, enum.Enum):
    admin = 'admin'
    user = 'user'

class TaskBase(BaseModel):
    name: str
    description: str
    deadline: date
    done: bool
    
    class Config:
        orm_mode = True

class CreateTask(TaskBase):
    class Config:
        orm_true = True

class UserBase(BaseModel):
    username: str
    password: str
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    class Config:
        orm_mode = True
    
class UserResponse(BaseModel):
    id:int
    username: str
    role: str
    
    class Config:
        orm_mode = True

class PermissionBase(BaseModel):
    task_id: Optional[int] = None
    user_id: int
    can_read: bool = True
    can_update: bool
    can_delete: bool
    can_write: bool

    class Config:
        orm_mode = True

class CreatePermission(PermissionBase):
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str