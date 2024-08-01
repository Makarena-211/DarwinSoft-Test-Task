from pydantic import BaseModel
from datetime import date
from uuid import UUID

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
    
class UserResponse(UserBase):
    id:int
    role: str
    class Config:
        orm_mode = True

class PermissionBase(BaseModel):
    task_id: int
    user_id: int
    can_read: bool
    can_update: bool

    class Config:
        orm_mode = True

class CreatePermission(PermissionBase):
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str