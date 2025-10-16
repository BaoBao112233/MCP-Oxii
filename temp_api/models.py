from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4


# Database Models (in-memory for simplicity)
class TaskDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    plan_id: str
    order_no: int
    title: str
    description: str
    max_retries: int = 2
    status: str = "pending"
    execution_result: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PlanDB(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: int
    title: str
    goal_text: Optional[str] = None
    trigger: str = "SYSTEM"
    priority: int = 1
    status: str = "created"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tasks: List[TaskDB] = []


# API Request/Response Models
class TaskCreate(BaseModel):
    order_no: int
    title: str
    description: str
    max_retries: int = 2


class PlanCreate(BaseModel):
    session_id: int
    title: str
    goal_text: Optional[str] = None
    trigger: str = Field(default="SYSTEM")
    priority: int = Field(default=1)
    tasks: List[TaskCreate] = []


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    execution_result: Optional[str] = None


class PlanUpdate(BaseModel):
    status: Optional[str] = None
    goal_text: Optional[str] = None


# Response Models
class TaskResponse(BaseModel):
    id: str
    order_no: int
    title: str
    description: str
    max_retries: int
    status: str = "pending"
    execution_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PlanResponse(BaseModel):
    id: str
    title: str
    goal_text: Optional[str]
    trigger: str
    priority: int
    status: str
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponse]


class InsertPlansResponse(BaseModel):
    affected_rows: int
    returning: List[PlanResponse]


class ApiResponse(BaseModel):
    data: Dict[str, Any]