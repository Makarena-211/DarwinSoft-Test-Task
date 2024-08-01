from fastapi import APIRouter, HTTPException, Depends, status
import schemas
from sqlalchemy.orm import Session
from database import get_db
import models
import auth
from datetime import timedelta, datetime
from typing import List

router = APIRouter()

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
    tasks = db.query(models.Task).all()
    return tasks

@router.post('/post', response_model=schemas.TaskBase)
def create_tasks(task:schemas.CreateTask, db:Session=Depends(get_db), current_user: models.User = Depends(auth.get_current_admin_user)):
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
    return new_task

@router.delete('/delete/{task_id}')
def delete_task(task_id: int, db:Session=Depends(get_db), current_user: models.User = Depends(auth.get_current_admin_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task")
    
    if task.owner_id != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

@router.put('/update/{task_id}', response_model=schemas.TaskBase)
def update_tasks(update_task: schemas.TaskBase, task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin_user)):
    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    task = task_query.first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    if task.owner_id != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail='Not enough permissions')
    task_data = update_task.dict(exclude_unset=True)
    task_query.update(task_data, synchronize_session=False)
    db.commit()
    
    return task_query.first()

@router.post('/tasks/{task_id}/permissions', response_model=schemas.PermissionBase)
def grant_permission(task_id:int, permission:schemas.PermissionBase, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_admin_user)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_permission = models.Permission(**permission.dict(), task_id=task_id)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.post('/register', response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
         raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username = user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
