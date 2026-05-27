from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import require_admin, get_storage, User
from app.storage import TaskStorage
from app.schemas import StatsResponse
from collections import Counter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=StatsResponse)
def get_stats(admin: User = Depends(require_admin), storage: TaskStorage = Depends(get_storage)):
    tasks = storage.admin_get_all()
    total = len(tasks)
    status_counter = Counter(t.status for t in tasks)
    return StatsResponse(total_tasks=total, by_status=dict(status_counter))

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(task_id: int, admin: User = Depends(require_admin), storage: TaskStorage = Depends(get_storage)):
    if not storage.admin_delete(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return None