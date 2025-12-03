from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.taskmanager.model import Task

def get_task_service(db : Session, user_id : int, task_id : int):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_all_task_service(db:Session, user_id : int):
    return db.qury(Task).filter(Task.user_id == user_id).all()


def create_task_service(db : Session, user_id : int, task):
    newtask = Task(
        user_id = user_id,
        title = task.title,
        description = task.description,
        category = task.category,
        priority = task.priority,
        is_completed = task.is_completed,
        due_date = task.due_date
    )
    db.add(newtask)
    db.commit()
    db.refresh(newtask)
    return newtask


def update_task_service(db : Session, user_id : int, task_id : int, task_data):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = task_data.title
    task.description = task_data.description
    task.category = task_data.category
    task.priority = task_data.priority
    task.is_completed = task_data.is_completed
    task.due_date = task_data.due_date
    
    db.commit()
    db.refresh(task)
    return task


def delete_task_service(db : Session, user_id : int, task_id : int):
    workout = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not workout:
        raise HTTPException(status_code = 404, detail = "Task not found")
    db.delete(workout)
    db.commit()
    return {"message" : "Task delete successfully" }