from pydantic import BaseModel, Field, conint, constr
from typing import Optional

class TaskBase(BaseModel):
    title: constr(min_length=3, max_length=80)
    description: Optional[str] = None
    status: str = Field(default="todo", pattern="^(todo|in_progress|done)$")
    priority: conint(ge=1, le=5)

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|done)$")

class User(BaseModel):
    id: int
    role: str = "user"

class StatsResponse(BaseModel):
    total_tasks: int
    by_status: dict[str, int]