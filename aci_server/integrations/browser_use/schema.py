from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

# Task status enum
TaskStatus = Literal["created", "running", "finished", "stopped", "paused", "failed"]

# Input schemas
class RunTaskParams(BaseModel):
    task: str
    save_browser_data: Optional[bool] = False

class TaskIdParams(BaseModel):
    task_id: str

# Output schemas
class Step(BaseModel):
    id: str
    step: int
    evaluation_previous_goal: Optional[str] = None
    next_goal: Optional[str] = None

class Cookie(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    domain: Optional[str] = None
    path: Optional[str] = None
    expires: Optional[float] = None
    httpOnly: Optional[bool] = None
    secure: Optional[bool] = None
    sameSite: Optional[str] = None

class BrowserData(BaseModel):
    cookies: Optional[List[Cookie]] = None

class TaskDetail(BaseModel):
    id: str
    task: str
    output: Optional[str] = None
    status: TaskStatus
    created_at: str
    steps: List[Step]
    live_url: Optional[str] = None
    finished_at: Optional[str] = None
    browser_data: Optional[BrowserData] = None

class TaskMedia(BaseModel):
    recordings: Optional[List[str]] = None

# API Response models
class RunTaskResponse(BaseModel):
    data: Dict[str, str]
    message: Optional[str] = None

class StopTaskResponse(BaseModel):
    data: Any
    message: Optional[str] = None

class PauseTaskResponse(BaseModel):
    data: Any
    message: Optional[str] = None

class ResumeTaskResponse(BaseModel):
    data: Any
    message: Optional[str] = None

class GetTaskResponse(BaseModel):
    data: TaskDetail
    message: Optional[str] = None

class GetTaskStatusResponse(BaseModel):
    data: TaskStatus
    message: Optional[str] = None

class GetTaskMediaResponse(BaseModel):
    data: TaskMedia
    message: Optional[str] = None

class ListTasksResponse(BaseModel):
    data: List[TaskDetail]
    message: Optional[str] = None

class Balance(BaseModel):
    balance: int

# Additional response models
class CheckBalanceResponse(BaseModel):
    data: Balance
    message: Optional[str] = None

class MeResponse(BaseModel):
    data: bool
    message: Optional[str] = None

class PingResponse(BaseModel):
    data: Any
    message: Optional[str] = None

# Update ApiResponse to include new types
class ApiResponse(BaseModel):
    data: Union[Dict[str, str], TaskDetail, TaskStatus, TaskMedia, List[TaskDetail], Balance, bool, Any]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None