from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# User schema

# Status schemas
class Status(BaseModel):
    name: str
    isDefaultStatus: bool
    isResolvedStatus: bool

class GetStatusesParams(BaseModel):
    workspaceId: Optional[str] = Field(None, description="Get statuses for a particular workspace")

# User schema
class User(BaseModel):
    id: str = Field(..., description="The user ID")
    name: Optional[str] = Field(None, description="The name of the user")
    email: str = Field(..., description="The email of the user")

# Comment schemas
class CreateCommentParams(BaseModel):
    taskId: str = Field(..., description="The task on which to place a comment")
    content: str = Field(..., description="Github Flavored Markdown representing the comment")

class Comment(BaseModel):
    id: str
    taskId: str = Field(..., description="The id of the task to which the comment belongs")
    content: str = Field(..., description="The HTML contents of the comment")
    createdAt: str = Field(..., description="When the comment was created")
    creator: User

class GetCommentsParams(BaseModel):
    taskId: str = Field(..., description="The task for which all comments should be returned")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class CommentsMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class GetCommentsResponse(BaseModel):
    meta: Optional[CommentsMeta] = Field(default_factory=dict)
    comments: List[Comment]

# Project schemas
class ProjectStatus(BaseModel):
    name: str = Field(..., description="The name of the status")
    isDefaultStatus: bool = Field(..., description="Whether this status is a default status for the workspace")
    isResolvedStatus: bool = Field(..., description="Whether this is a resolved (terminated) status for the workspace")

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = Field("", description="The HTML contents of the description")
    workspaceId: Optional[str] = Field(None, description="The id of the workspace")
    status: Optional[ProjectStatus] = Field(None, description="The status of the project")
    color: Optional[str] = Field(None, description="Color associated with the project")

class CreateProjectParams(BaseModel):
    name: str = Field(..., description="The name of the project")
    workspaceId: str = Field(..., description="The workspace to which the project belongs")
    description: Optional[str] = Field(None, description="The description of the project. HTML input accepted")
    labels: Optional[List[str]] = Field(None, description="The list of labels by name the project should have")
    priority: Optional[str] = Field("MEDIUM", description="Defaults to MEDIUM. Options are ASAP, HIGH, MEDIUM, and LOW")

class GetProjectParams(BaseModel):
    id: str = Field(..., description="The ID of the project to return")

class ListProjectsParams(BaseModel):
    workspaceId: Optional[str] = Field(None, description="The workspace for which all projects should be returned")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class ProjectsMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class ListProjectsResponse(BaseModel):
    meta: Optional[ProjectsMeta] = Field(default_factory=dict)
    projects: List[Project]

# Label schema
class Label(BaseModel):
    name: str = Field(..., description="The name of the label")

# Workspace schema
class Workspace(BaseModel):
    id: str
    name: str
    teamId: Optional[str] = Field(None, description="The id of the team")
    type: str = Field(..., description="Whether the workspace is a team or individual type")
    labels: Any = Field(default_factory=list)
    statuses: Optional[List[Status]] = Field(default_factory=list)

# Task schemas
class TaskStatus(BaseModel):
    name: str = Field(..., description="The name of the status")
    isDefaultStatus: bool = Field(..., description="Whether this status is a default status for the workspace")
    isResolvedStatus: bool = Field(..., description="Whether this is a resolved (terminated) status for the workspace")

class ProjectRef(BaseModel):
    id: str
    status: Optional[ProjectStatus] = None

# Recurring Task schemas
class CreateRecurringTaskParams(BaseModel):
    frequency: str = Field(..., description="Frequency in which the task should be scheduled. Examples: 'weekly_any_day', 'weekly_specific_days_[MO]', 'daily_every_day', 'monthly_15', etc.")
    deadlineType: str = Field("SOFT", description="'HARD' or 'SOFT' are the two values allowed")
    duration: Optional[Union[int, str]] = Field(None, description="An integer greater than 0 or 'REMINDER' for a reminder task")
    startingOn: Optional[str] = Field(None, description="ISO 8601 Date for when the task starts")
    idealTime: Optional[str] = Field(None, description="Should be in the form of 'HH:00|30 am|pm'. Examples: '12:30 am', '8:00 am', '3:30 pm'")
    schedule: Optional[str] = Field("Work Hours", description="Schedule the task must adhere to")
    name: str = Field(..., description="The name of the recurring task")
    workspaceId: str = Field(..., description="The workspace in which to create the recurring task")
    description: Optional[str] = Field(None, description="The description of the task")
    priority: Optional[str] = Field("MEDIUM", description="'HIGH' or 'MEDIUM' (which is the default)")
    assigneeId: str = Field(..., description="To whom the recurring task should be assigned")

class RecurringTask(BaseModel):
    id: str
    name: str
    description: Optional[str] = Field("", description="The HTML contents of the description")
    workspace: Optional[Workspace] = Field(None)
    creator: Optional[User] = Field(None)
    assignee: Optional[User] = Field(None)
    project: Optional[ProjectRef] = None
    status: Optional[TaskStatus] = Field(None)
    priority: Optional[str] = Field(None, description="Valid options are ASAP, HIGH, MEDIUM, or LOW")
    labels: Optional[List[Label]] = Field(default_factory=list, description="An array of labels")

class DeleteRecurringTaskParams(BaseModel):
    id: str = Field(..., description="ID of the recurring task to delete")

class ListRecurringTasksParams(BaseModel):
    workspaceId: str = Field(..., description="The workspace for which all recurring tasks should be returned")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class RecurringTasksMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class ListRecurringTasksResponse(BaseModel):
    meta: Optional[RecurringTasksMeta] = Field(default_factory=dict)
    tasks: List[RecurringTask]

# Schedule schemas
class ScheduleTimeBlock(BaseModel):
    start: str = Field(..., description="When the schedule starts, formatted HH:MM")
    end: str = Field(..., description="When the schedule ends, formatted HH:MM")

class ScheduleDetails(BaseModel):
    monday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Monday schedule blocks")
    tuesday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Tuesday schedule blocks")
    wednesday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Wednesday schedule blocks")
    thursday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Thursday schedule blocks")
    friday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Friday schedule blocks")
    saturday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Saturday schedule blocks")
    sunday: Optional[List[ScheduleTimeBlock]] = Field(None, description="Sunday schedule blocks")

class Schedule(BaseModel):
    name: str
    isDefaultTimezone: bool
    timezone: str = Field(..., description="The timezone of the schedule")
    schedule: ScheduleDetails

class GetSchedulesParams(BaseModel):
    # No parameters required
    pass

# User schemas (extending the existing User model)
class ListUsersParams(BaseModel):
    teamId: Optional[str] = Field(None, description="The ID of the team for which all members will be returned")
    workspaceId: Optional[str] = Field(None, description="The ID of the workspace for which all members will be returned")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class UsersMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class ListUsersResponse(BaseModel):
    meta: Optional[UsersMeta] = Field(default_factory=dict)
    users: List[User]

# Workspace schemas (complete definition)
class Workspace(BaseModel):
    id: str
    name: str
    teamId: Optional[str] = Field(None, description="The id of the team")
    type: str = Field(..., description="Whether the workspace is a team or individual type")
    labels: Any = Field(default_factory=list)
    statuses: Optional[List[Status]] = Field(default_factory=list)

class ListWorkspacesParams(BaseModel):
    ids: Optional[List[str]] = Field(None, description="Expand details of specific workspaces")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class WorkspacesMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class ListWorkspacesResponse(BaseModel):
    meta: Optional[WorkspacesMeta] = Field(default_factory=dict)
    workspaces: List[Workspace]

# Create wrapper models for list responses that don't have one
class SchedulesListResponse(BaseModel):
    schedules: List[Schedule]

class StatusesListResponse(BaseModel):
    statuses: List[Status]

# Auto Scheduling Schema
class AutoScheduled(BaseModel):
    startDate: Optional[str] = Field(None, description="ISO 8601 Date which is trimmed to the start of the day passed")
    deadlineType: str = Field("SOFT", description="HARD, SOFT, or NONE are valid options")
    schedule: str = Field("Work Hours", description="Schedule the task must adhere to. Schedule MUST be 'Work Hours' if scheduling the task for another user")

# Task Schemas
class CreateTaskParams(BaseModel):
    name: str = Field(..., description="Title of the task")
    workspaceId: str = Field(..., description="The workspace in which to create the task")
    dueDate: Optional[str] = Field(None, description="ISO 8601 Due date on the task. REQUIRED for scheduled tasks")
    duration: Optional[Union[str, int]] = Field(None, description="A duration can be one of the following... 'NONE', 'REMINDER', or an integer greater than 0")
    status: Optional[str] = Field(None, description="Defaults to workspace default status")
    autoScheduled: Optional[Union[AutoScheduled, None]] = Field(None, description="Set values to turn auto scheduling on, set value to null if you want to turn auto scheduling off")
    projectId: Optional[str] = Field(None)
    description: Optional[str] = Field(None, description="Github Flavored Markdown for the input")
    priority: Optional[str] = Field(None, description="ASAP, HIGH, MEDIUM, and LOW are valid values")
    labels: Optional[List[str]] = Field(None, description="The names of the labels to be added to the task")
    assigneeId: Optional[str] = Field(None, description="The user id the task should be assigned to")

class Task(BaseModel):
    id: str
    name: str
    description: Optional[str] = Field("", description="The HTML contents of the description")
    duration: Optional[Union[str, int]] = Field(None, description="An integer greater than 0, 'NONE', or 'REMINDER'")
    dueDate: Optional[str] = Field(None, description="When is the task due")
    deadlineType: Optional[str] = Field(None, description="Values are HARD, SOFT (default) or NONE")
    parentRecurringTaskId: Optional[str] = Field(None, description="If this is an instance of a recurring task, this field will be the parent recurring task id")
    completed: Optional[bool] = Field(None, description="Whether the task is completed or not")
    creator: Optional[User] = Field(None)
    project: Optional[ProjectRef] = None
    workspace: Optional[Workspace] = Field(None)
    status: Optional[TaskStatus] = Field(None)
    priority: Optional[str] = Field(None, description="Valid options are ASAP, HIGH, MEDIUM, or LOW")
    labels: Optional[List[Label]] = Field(default_factory=list, description="An array of labels")
    assignees: Optional[List[User]] = Field(default_factory=list, description="An array of assignees")
    scheduledStart: Optional[str] = Field(None, description="The time that motion has scheduled this task to start")
    createdTime: Optional[str] = Field(None, description="The time that the task was created")
    scheduledEnd: Optional[str] = Field(None, description="The time that motion has scheduled this task to end")
    schedulingIssue: Optional[bool] = Field(None, description="Returns true if Motion was unable to schedule this task")

class DeleteTaskParams(BaseModel):
    id: str = Field(..., description="ID of the task to delete")

class GetTaskParams(BaseModel):
    id: str = Field(..., description="The id of the task to fetch")

class ListTasksParams(BaseModel):
    assigneeId: Optional[str] = Field(None, description="Limit tasks returned to a specific assignee")
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    includeAllStatuses: Optional[bool] = Field(None, description="Limit tasks returned by statuses that exist on tasks")
    label: Optional[str] = Field(None, description="Limit tasks returned by label on the task")
    name: Optional[str] = Field(None, description="Limit tasks returned to those that contain this string. Case in-sensitive")
    projectId: Optional[str] = Field(None, description="Limit tasks returned to a given project")
    status: Optional[List[str]] = Field(None, description="Limit tasks returned by statuses that exist on tasks")
    workspaceId: Optional[str] = Field(None, description="The id of the workspace you want tasks from")

class TasksMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")
    pageSize: Optional[int] = Field(None, description="The number of results in this response")

class ListTasksResponse(BaseModel):
    meta: Optional[TasksMeta] = Field(default_factory=dict)
    tasks: List[Task]

class MoveTaskParams(BaseModel):
    id: str = Field(..., description="The id of the task to move")
    workspaceId: str = Field(..., description="The workspace to move the task to")

class UnassignTaskParams(BaseModel):
    id: str = Field(..., description="The id of the task to unassign")

class UpdateTaskParams(BaseModel):
    id: str = Field(..., description="The id of the task to update")
    name: Optional[str] = Field(None, description="Title of the task")
    workspaceId: Optional[str] = Field(None)
    dueDate: Optional[str] = Field(None, description="ISO 8601 Due date on the task")
    duration: Optional[Union[str, int]] = Field(None, description="A duration can be one of the following... 'NONE', 'REMINDER', or an integer greater than 0")
    status: Optional[str] = Field(None, description="Task status")
    autoScheduled: Optional[Union[AutoScheduled, None]] = Field(None, description="Set values to turn auto scheduling on, set value to null if you want to turn auto scheduling off")
    projectId: Optional[str] = Field(None)
    description: Optional[str] = Field(None, description="Github Flavored Markdown for the input")
    priority: Optional[str] = Field(None, description="ASAP, HIGH, MEDIUM, and LOW are valid values")
    labels: Optional[List[str]] = Field(None, description="The names of the labels to be added to the task")
    assigneeId: Optional[str] = Field(None, description="The user id the task should be assigned to")

class EmptyRequestBody(BaseModel):
    """Empty request body for endpoints that don't require any inputs"""
    pass

class SuccessResponse(BaseModel):
    """Standard response for successful operations"""
    success: bool = True
    message: Optional[str] = None

class ApiResponse(BaseModel):
    data: Union[
        Comment,
        GetCommentsResponse,
        Project,
        ListProjectsResponse,
        RecurringTask,
        ListRecurringTasksResponse,
        SchedulesListResponse,
        StatusesListResponse,
        ListUsersResponse,
        User,
        ListWorkspacesResponse,
        Dict[str, Any],
        Task,
        ListTasksResponse,
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
