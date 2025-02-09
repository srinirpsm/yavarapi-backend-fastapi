from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas,auth
from database import get_db
from datetime import datetime 
from routes.auth import get_current_user
from ai_utils import analyze_sentiment, suggest_priority

# Create an APIRouter instance for tasks
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    new_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=task.due_date,
        status="Pending",
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=list[schemas.Task])
def get_tasks(status: str = None, priority: str = None, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    query = db.query(models.Task)

    if status:
        query = query.filter(models.Task.status == status)
    
    if priority:
        query = query.filter(models.Task.priority == priority)

    return query.all()

@router.get("/insights")
def get_tasks(
    status: str = None,
    priority: str = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Fetch all tasks and analyze sentiment + priority dynamically."""

    tasks = db.query(models.Task).all()

    insights = []
    for task in tasks:
        sentiment = analyze_sentiment(task.description)  # ✅ Now returns a dictionary
        priority = suggest_priority(task.description)
        
        insights.append({
            "id": task.id,
            "description": task.description,
            "sentiment": sentiment.get("label", "Neutral"),  # ✅ Now works
            "sentiment_score": sentiment.get("score", 0),  # ✅ Now works
            "priority": priority
        })

    return {"tasks": insights}


@router.get("/{task_id}", response_model=schemas.Task)
def get_task(task_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.title = task_update.title or task.title
    task.description = task_update.description or task.description
    task.priority = task_update.priority or task.priority
    task.due_date = task_update.due_date or task.due_date
    task.status = task_update.status or task.status 

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

@router.patch("/{task_id}/complete", response_model=schemas.Task)
def mark_task_complete(task_id: int, db: Session = Depends(get_db),current_user=Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "Completed"
    db.commit()
    db.refresh(task)
    return task

