from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import get_db
import models, auth, schemas
from datetime import timedelta, datetime
from typing import List, Optional

router = APIRouter()

def check_permissions(db:Session, user_id:int, permission_required:str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role == models.RoleEnum.admin:
        return True
    permissions = db.query(models.Permission).filter(models.Permission.user_id == user_id).first()
    if not permissions or not getattr(permissions, permission_required):
        raise HTTPException(status_code=403, detail=f"You don't have permission to {permission_required.replace('_', ' ')} tasks")

@router.post('/token', response_model=schemas.Token)  
def login_for_access_token(db: Session = Depends(get_db), form_data: auth.OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data = {'sub':user.username}, expires_delta=access_token_expires)
    return {'access_token':access_token, 'token_type':'bearer'}

@router.get('/tasks', response_model=List[schemas.TaskBase])  
def get_tasks(db: Session=Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    check_permissions(db, current_user.id, 'can_read')
    tasks = db.query(models.Task).all()
    return tasks

@router.post('/post', response_model=schemas.TaskBase) 
def create_tasks(task:schemas.CreateTask, db:Session=Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):

    check_permissions(db, current_user.id, 'can_write')

    new_task = models.Task(
        name = task.name,
        description = task.description,
        deadline = task.deadline,
        done = task.done,
        owner_id = current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    existing_permission = db.query(models.Permission).filter(models.Permission.user_id == current_user.id,  models.Permission.task_id == None).first()
    if existing_permission:
        existing_permission.task_id = new_task.id
    else:
        new_permission = models.Permission(
                task_id=new_task.id,
                user_id=current_user.id,
                can_read=True,
                can_write=True,
                can_update=False,
                can_delete=False)
        db.add(new_permission)
    db.commit()
    return new_task

@router.delete('/delete/{task_id}')
def delete_task(task_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    check_permissions(db, current_user.id, 'can_delete')
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task")
    
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

@router.put('/update/{task_id}', response_model=schemas.TaskBase)
def update_tasks(update_task: schemas.TaskBase, task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    check_permissions(db, current_user.id, 'can_update')
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    task_data = update_task.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.put('/tasks/{id}/permissions', response_model=schemas.PermissionBase) 
def update_permission(id: int, permission: schemas.PermissionBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin_user)):
    db_permission = db.query(models.Permission).filter(models.Permission.id == id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    db_permission.can_read = permission.can_read
    db_permission.can_update = permission.can_update
    db_permission.can_delete = permission.can_delete
    db_permission.can_write = permission.can_write

    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.post('/register')
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)): 
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
         raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username = user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    create_user_permissions(db, new_user.id, new_user.role)
    return new_user


def create_user_permissions(db: Session, user_id: int, role: models.RoleEnum): 
    if role == models.RoleEnum.user:
        new_permission = models.Permission(
            user_id=user_id,
            can_read=True,
            can_update=False,
            can_delete=False,
            can_write=False
        )
        db.add(new_permission)
        db.commit()