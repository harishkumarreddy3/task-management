from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.taskmanager.core import db_dependency, user_dependency
from src.taskmanager.service import (
    get_task_service,
    get_all_task_service,
    create_task_service,
    delete_task_service,
    update_task_service     
)

router = APIRouter(prefix="/taskmanager", tags=["taskmanager"])

# ---------- SCHEMAS ----------
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    priority: str
    is_completed: bool = False
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass   

class TaskUpdate(TaskBase):
    pass   
# ---------- ROUTES ----------

@router.get("/{task_id}")
def get_task(db: db_dependency, user: user_dependency, task_id: int):
    return get_task_service(db, user["id"], task_id)


@router.get("/tasks")
def get_tasks(db: db_dependency, user: user_dependency):
    return get_all_task_service(db, user["id"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(db: db_dependency, user: user_dependency, task:TaskCreate):
    return create_task_service(db, user["id"], task)

@router.patch("/{task_id}")
def update_task(db: db_dependency, user: user_dependency, task_id: int, task:TaskUpdate):
    return update_task_service(db, user["id"], task_id, task)

@router.put("/{task_id}")
def update_task_put(db: db_dependency, user: user_dependency, task_id: int, task:TaskUpdate):
    return update_task_service(db, user["id"], task_id, task)

@router.delete("/{task_id}")
def delete_task(db: db_dependency, user: user_dependency, task_id: int):
    return delete_task_service(db, user["id"], task_id)