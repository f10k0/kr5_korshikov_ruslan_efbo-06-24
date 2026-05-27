from typing import Dict, List, Optional
from app.schemas import TaskResponse

class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, dict] = {}
        self._next_id = 1

    def create(self, task_data: dict) -> TaskResponse:
        task_id = self._next_id
        self._next_id += 1
        task = {"id": task_id, **task_data}
        self._tasks[task_id] = task
        return TaskResponse(**task)

    def get_all(self, owner_id: int, status: Optional[str] = None, min_priority: Optional[int] = None) -> List[TaskResponse]:
        result = []
        for task in self._tasks.values():
            if task["owner_id"] != owner_id:
                continue
            if status and task["status"] != status:
                continue
            if min_priority is not None and task["priority"] < min_priority:
                continue
            result.append(TaskResponse(**task))
        return result

    def get_one(self, task_id: int, owner_id: int) -> Optional[TaskResponse]:
        task = self._tasks.get(task_id)
        if task and task["owner_id"] == owner_id:
            return TaskResponse(**task)
        return None

    def update_status(self, task_id: int, owner_id: int, new_status: str) -> Optional[TaskResponse]:
        task = self._tasks.get(task_id)
        if not task or task["owner_id"] != owner_id:
            return None
        task["status"] = new_status
        return TaskResponse(**task)

    def delete(self, task_id: int, owner_id: int) -> bool:
        task = self._tasks.get(task_id)
        if not task or task["owner_id"] != owner_id:
            return False
        del self._tasks[task_id]
        return True

    def admin_get_all(self) -> List[TaskResponse]:
        return [TaskResponse(**t) for t in self._tasks.values()]

    def admin_delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear(self):
        self._tasks.clear()
        self._next_id = 1

storage = TaskStorage()