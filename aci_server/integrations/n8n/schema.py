from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# User schemas
class User(BaseModel):
    id: Optional[str] = Field(None, description="The user ID")
    email: str = Field(..., description="The email of the user")
    firstName: Optional[str] = Field(None, description="The first name of the user")
    lastName: Optional[str] = Field(None, description="The last name of the user")
    isPending: Optional[bool] = Field(None, description="Whether the user has a pending invitation")
    createdAt: Optional[str] = Field(None, description="When the user was created")
    updatedAt: Optional[str] = Field(None, description="When the user was last updated")
    role: Optional[str] = Field(None, description="The role of the user")

class CreateUsersParams(BaseModel):
    users: List[Dict[str, Any]] = Field(..., description="List of users to create")

class ListUsersParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")

class GetUserParams(BaseModel):
    id: str = Field(..., description="The ID of the user to retrieve")

class DeleteUserParams(BaseModel):
    id: str = Field(..., description="The ID of the user to delete")

class UpdateUserRoleParams(BaseModel):
    id: str = Field(..., description="The ID of the user to update")
    role: str = Field(..., description="New role to assign to the user")

class ListUsersMeta(BaseModel):
    nextCursor: Optional[str] = Field(None, description="Make the same query with the new cursor to get more results")

class UsersList(BaseModel):
    data: List[User]
    nextCursor: Optional[str] = Field(None, description="Cursor for pagination")

# Execution schemas
class Execution(BaseModel):
    id: Union[int, str]
    data: Dict[str, Any] = Field(default_factory=dict)
    finished: Optional[bool] = None
    mode: Optional[str] = None
    retryOf: Optional[Union[int, str]] = None
    retrySuccessId: Optional[str] = None
    startedAt: Optional[str] = None
    stoppedAt: Optional[str] = None
    workflowId: Optional[Union[int, str]] = None
    waitTill: Optional[str] = None
    customData: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ListExecutionsParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    workflowId: Optional[Union[int, str]] = Field(None, description="Filter executions by workflow ID")

class GetExecutionParams(BaseModel):
    id: Union[int, str] = Field(..., description="The ID of the execution to retrieve")

class DeleteExecutionParams(BaseModel):
    id: Union[int, str] = Field(..., description="The ID of the execution to delete")

class ExecutionsList(BaseModel):
    data: List[Execution]
    nextCursor: Optional[str] = Field(None, description="Cursor for pagination")

# Success response for delete operations
class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

# Empty request body
class EmptyRequestBody(BaseModel):
    """Empty request body for endpoints that don't require any inputs"""
    pass

# Node schemas
class NodeCredential(BaseModel):
    id: str
    name: str

class NodePosition(RootModel):
    root: List[int]
    
    def model_dump(self, *args, **kwargs):
        return self.root

class Node(BaseModel):
    id: str
    name: str
    webhookId: Optional[str] = None
    disabled: Optional[bool] = None
    notesInFlow: Optional[bool] = None
    notes: Optional[str] = None
    type: str
    typeVersion: int
    executeOnce: Optional[bool] = None
    alwaysOutputData: Optional[bool] = None
    retryOnFail: Optional[bool] = None
    maxTries: Optional[int] = None
    waitBetweenTries: Optional[int] = None
    continueOnFail: Optional[bool] = None
    onError: Optional[str] = None
    position: List[int]
    parameters: Dict[str, Any] = Field(default_factory=dict)
    credentials: Optional[Dict[str, NodeCredential]] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class Connection(BaseModel):
    node: str
    type: str
    index: int

class ConnectionMain(RootModel):
    root: List[Connection]
    
    def model_dump(self, *args, **kwargs):
        return self.root

class WorkflowSettings(BaseModel):
    saveExecutionProgress: Optional[bool] = None
    saveManualExecutions: Optional[bool] = None
    saveDataErrorExecution: Optional[str] = None
    saveDataSuccessExecution: Optional[str] = None
    executionTimeout: Optional[int] = None
    errorWorkflow: Optional[str] = None
    timezone: Optional[str] = None
    executionOrder: Optional[str] = None

class StaticData(BaseModel):
    lastId: Optional[int] = None
    # Add other static data fields as needed

class Tag(BaseModel):
    id: str
    name: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

# Workflow schemas
class Workflow(BaseModel):
    id: Optional[str] = None
    name: str
    active: Optional[bool] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    nodes: List[Node]
    connections: Dict[str, List[Connection]]
    settings: Optional[WorkflowSettings] = None
    staticData: Optional[StaticData] = None
    tags: Optional[List[Tag]] = None

class WorkflowsList(BaseModel):
    data: List[Workflow]
    nextCursor: Optional[str] = None

# Workflow operation params
class ListWorkflowsParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    tags: Optional[List[str]] = Field(None, description="Filter workflows by tags")
    active: Optional[bool] = Field(None, description="Filter workflows by active status")

class GetWorkflowParams(BaseModel):
    id: str = Field(..., description="The ID of the workflow to retrieve")

class CreateWorkflowParams(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="The workflow to create")

class UpdateWorkflowParams(BaseModel):
    id: str = Field(..., description="The ID of the workflow to update")
    workflow: Dict[str, Any] = Field(..., description="The updated workflow data")

class DeleteWorkflowParams(BaseModel):
    id: str = Field(..., description="The ID of the workflow to delete")

class ActivateWorkflowParams(BaseModel):
    id: str = Field(..., description="The ID of the workflow to activate")
    active: bool = Field(..., description="Set to true to activate, false to deactivate")

# Additional schemas
class CopyWorkflowParams(BaseModel):
    id: str = Field(..., description="The ID of the workflow to copy")
    destinationProjectId: Optional[str] = Field(None, description="The ID of the project to copy to")

class TagsList(BaseModel):
    tags: List[Tag]

# Credential schemas
class CredentialData(RootModel):
    root: Dict[str, Any]
    
    def model_dump(self, *args, **kwargs):
        return self.root

class CreateCredentialParams(BaseModel):
    name: str = Field(..., description="Name of the credential")
    type: str = Field(..., description="Type of the credential (e.g., 'github')")
    data: Dict[str, Any] = Field(..., description="Credential data, structure depends on the type")

class DeleteCredentialParams(BaseModel):
    id: str = Field(..., description="The ID of the credential to delete")

class Credential(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    # data field is omitted in response for security reasons

class CredentialsList(BaseModel):
    data: List[Credential]
    nextCursor: Optional[str] = None

class ListCredentialsParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    type: Optional[str] = Field(None, description="Filter credentials by type")

class CredentialTypeSchema(BaseModel):
    additionalProperties: bool = False
    type: str
    properties: Dict[str, Any]
    required: List[str]

class GetCredentialTypeParams(BaseModel):
    type: str = Field(..., description="The credential type to retrieve the schema for")

# Tag operation params (beyond what's already defined)
class CreateTagParams(BaseModel):
    name: str = Field(..., description="Name of the tag")

class DeleteTagParams(BaseModel):
    id: str = Field(..., description="The ID of the tag to delete")

class UpdateTagParams(BaseModel):
    id: str = Field(..., description="The ID of the tag to update")
    name: str = Field(..., description="New name for the tag")

# Source Control schemas
class PullOptions(BaseModel):
    force: Optional[bool] = Field(False, description="Force pull changes")
    variables: Optional[Dict[str, str]] = Field(None, description="Variables to include in the pull")

class PullResult(BaseModel):
    variables: Optional[Dict[str, List[str]]] = None
    credentials: Optional[List[Dict[str, str]]] = None
    workflows: Optional[List[Dict[str, str]]] = None
    tags: Optional[Dict[str, Any]] = None

# Variable schemas
class Variable(BaseModel):
    id: Optional[str] = None
    key: str
    value: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class CreateVariableParams(BaseModel):
    key: str = Field(..., description="Variable key")
    value: str = Field(..., description="Variable value")

class DeleteVariableParams(BaseModel):
    id: str = Field(..., description="The ID of the variable to delete")

class VariablesList(BaseModel):
    data: List[Variable]
    nextCursor: Optional[str] = None

class ListVariablesParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    limit: Optional[int] = Field(100, description="The maximum number of items to return (max 250)")

# Project schemas
class Project(BaseModel):
    id: Optional[str] = None
    name: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class CreateProjectParams(BaseModel):
    name: str = Field(..., description="Name of the project")

class UpdateProjectParams(BaseModel):
    id: str = Field(..., description="The ID of the project to update")
    name: str = Field(..., description="New name for the project")

class DeleteProjectParams(BaseModel):
    id: str = Field(..., description="The ID of the project to delete")

class ProjectsList(BaseModel):
    data: List[Project]
    nextCursor: Optional[str] = None

class ListProjectsParams(BaseModel):
    cursor: Optional[str] = Field(None, description="Use if a previous request returned a cursor. Will page through results")
    limit: Optional[int] = Field(100, description="The maximum number of items to return (max 250)")

# Update the API Response model to include new types
class ApiResponse(BaseModel):
    data: Union[
        User,
        UsersList,
        Execution,
        ExecutionsList,
        Workflow,
        WorkflowsList,
        Credential,
        CredentialsList,
        CredentialTypeSchema,
        Tag,
        TagsList,
        Variable,
        VariablesList,
        Project,
        ProjectsList,
        PullResult,
        SuccessResponse,
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )
