from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas import TaskCreate, TaskResponse, TaskStatusUpdate
from app.dependencies import get_current_user, get_storage, User
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task_data = task.model_dump()
    task_data["owner_id"] = current_user.id
    return storage.create(task_data)

@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    status: Optional[str] = Query(None, pattern="^(todo|in_progress|done)$"),
    min_priority: Optional[int] = Query(None, ge=1, le=5),
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    return storage.get_all(current_user.id, status, min_priority)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_one(task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.update_status(task_id, current_user.id, update.status)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    if not storage.delete(task_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None