from typing import Optional, Dict, Any, List, Union
from .client import N8nClient
from .schema import (
    ApiResponse,
    User,
    UsersList,
    Execution,
    ExecutionsList,
    ListUsersParams,
    GetUserParams,
    CreateUsersParams,
    DeleteUserParams,
    UpdateUserRoleParams,
    ListExecutionsParams,
    GetExecutionParams,
    DeleteExecutionParams,
    SuccessResponse,
    Workflow,
    WorkflowsList,
    ListWorkflowsParams,
    GetWorkflowParams,
    CreateWorkflowParams,
    UpdateWorkflowParams,
    DeleteWorkflowParams,
    ActivateWorkflowParams,
    CopyWorkflowParams,
    Tag,
    TagsList,
    CredentialData,
    CreateCredentialParams,
    DeleteCredentialParams,
    Credential,
    CredentialsList,
    ListCredentialsParams,
    CredentialTypeSchema,
    GetCredentialTypeParams,
    CreateTagParams,
    DeleteTagParams,
    UpdateTagParams,
    PullOptions,
    PullResult,
    Variable,
    CreateVariableParams,
    DeleteVariableParams,
    VariablesList,
    ListVariablesParams,
    Project,
    ProjectsList,
    CreateProjectParams,
    UpdateProjectParams,
    DeleteProjectParams,
    ListProjectsParams
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class N8nService:
    def __init__(self, client: N8nClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
    
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "n8n"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)
    
    # Users operations
    def list_users(self, params: ListUsersParams) -> ApiResponse:
        """List all users"""
        cursor = params.cursor
        response = self.client.list_users(cursor)
        
        # Always normalize to our standard response format
        users = response.get("data", []) if isinstance(response, dict) else response
        users_list = UsersList(
            data=[User(**user) for user in users],
            nextCursor=response.get("nextCursor") if isinstance(response, dict) else None
        )
            
        return self.prepare_response(users_list, "N8nUsersList")
    
    def get_user(self, params: GetUserParams) -> ApiResponse:
        """Get a user by ID"""
        user_id = params.id
        response = self.client.get_user(user_id)
        validated = User(**response)
        return self.prepare_response(validated, "N8nUserCard")
    
    def create_users(self, params: CreateUsersParams) -> ApiResponse:
        """Create multiple users"""
        params_dict = params.model_dump(exclude_none=True)
        response = self.client.create_users(params_dict)
        
        # Normalize response to UsersList regardless of single or multiple users
        users = [response] if not isinstance(response, list) else response
        users_list = UsersList(data=[User(**user) for user in users])
        return self.prepare_response(users_list, "N8nUsersList")
    
    def delete_user(self, params: DeleteUserParams) -> ApiResponse:
        """Delete a user by ID"""
        user_id = params.id
        self.client.delete_user(user_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
    
    def update_user_role(self, params: UpdateUserRoleParams) -> ApiResponse:
        """Update a user's global role"""
        user_id = params.id
        role = params.role
        response = self.client.update_user_role(user_id, role)
        validated = User(**response)
        return self.prepare_response(validated, "N8nUserCard")
    
    # Executions operations
    def list_executions(self, params: ListExecutionsParams) -> ApiResponse:
        """List all executions"""
        cursor = params.cursor
        workflow_id = params.workflowId
        response = self.client.list_executions(cursor, workflow_id)
        
        executions = response.get("data", [])
        executions_list = ExecutionsList(
            data=[Execution(**execution) for execution in executions],
            nextCursor=response.get("nextCursor")
        )
            
        return self.prepare_response(executions_list, "N8nExecutionsList")
    
    def get_execution(self, params: GetExecutionParams) -> ApiResponse:
        """Get an execution by ID"""
        execution_id = params.id
        response = self.client.get_execution(execution_id)
        validated = Execution(**response)
        return self.prepare_response(validated, "N8nExecutionCard")
    
    def delete_execution(self, params: DeleteExecutionParams) -> ApiResponse:
        """Delete an execution by ID"""
        execution_id = params.id
        self.client.delete_execution(execution_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
        
    # Workflow operations
    def list_workflows(self, params: ListWorkflowsParams) -> ApiResponse:
        """List all workflows"""
        cursor = params.cursor
        tags = params.tags
        active = params.active
        response = self.client.list_workflows(cursor, tags, active)
        
        workflows = response.get("data", []) if isinstance(response, dict) else response
        workflows_list = WorkflowsList(
            data=[Workflow(**workflow) for workflow in workflows],
            nextCursor=response.get("nextCursor") if isinstance(response, dict) else None
        )
            
        return self.prepare_response(workflows_list, "N8nWorkflowsList")
    
    def get_workflow(self, params: GetWorkflowParams) -> ApiResponse:
        """Get a workflow by ID"""
        workflow_id = params.id
        response = self.client.get_workflow(workflow_id)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")
    
    def create_workflow(self, params: CreateWorkflowParams) -> ApiResponse:
        """Create a new workflow"""
        workflow_data = params.workflow
        response = self.client.create_workflow(workflow_data)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")
    
    def update_workflow(self, params: UpdateWorkflowParams) -> ApiResponse:
        """Update a workflow"""
        workflow_id = params.id
        workflow_data = params.workflow
        response = self.client.update_workflow(workflow_id, workflow_data)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")
    
    def delete_workflow(self, params: DeleteWorkflowParams) -> ApiResponse:
        """Delete a workflow by ID"""
        workflow_id = params.id
        self.client.delete_workflow(workflow_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
    
    def activate_workflow(self, params: ActivateWorkflowParams) -> ApiResponse:
        """Activate or deactivate a workflow"""
        workflow_id = params.id
        active = params.active
        response = self.client.activate_workflow(workflow_id, active)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")
    
    def copy_workflow(self, params: CopyWorkflowParams) -> ApiResponse:
        """Copy a workflow"""
        workflow_id = params.id
        destination_project_id = params.destinationProjectId
        response = self.client.copy_workflow(workflow_id, destination_project_id)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")
    
    def list_tags(self) -> ApiResponse:
        """List all workflow tags"""
        response = self.client.list_tags()
        tags = [Tag(**tag) for tag in response]
        tags_list = TagsList(tags=tags)
        return self.prepare_response(tags_list, "N8nTagsList")

    def deactivate_workflow(self, params: GetWorkflowParams) -> ApiResponse:
        """Deactivate a workflow using the dedicated endpoint"""
        workflow_id = params.id
        response = self.client.deactivate_workflow(workflow_id)
        validated = Workflow(**response)
        return self.prepare_response(validated, "N8nWorkflowCard")

    # Credential operations
    def list_credentials(self, params: ListCredentialsParams) -> ApiResponse:
        """List all credentials"""
        cursor = params.cursor
        cred_type = params.type
        response = self.client.list_credentials(cursor, cred_type)
        
        credentials = response.get("data", []) if isinstance(response, dict) else response
        credentials_list = CredentialsList(
            data=[Credential(**credential) for credential in credentials],
            nextCursor=response.get("nextCursor") if isinstance(response, dict) else None
        )
            
        return self.prepare_response(credentials_list, "N8nCredentialsList")
    
    def create_credential(self, params: CreateCredentialParams) -> ApiResponse:
        """Create a new credential"""
        data = params.model_dump(exclude_none=True)
        response = self.client.create_credential(data)
        validated = Credential(**response)
        return self.prepare_response(validated, "N8nCredentialCard")
    
    def delete_credential(self, params: DeleteCredentialParams) -> ApiResponse:
        """Delete a credential by ID"""
        credential_id = params.id
        self.client.delete_credential(credential_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
    
    def get_credential_type(self, params: GetCredentialTypeParams) -> ApiResponse:
        """Get credential type schema"""
        cred_type = params.type
        response = self.client.get_credential_type(cred_type)
        validated = CredentialTypeSchema(**response)
        return self.prepare_response(validated, None)
    
    # Additional Tag operations
    def create_tag(self, params: CreateTagParams) -> ApiResponse:
        """Create a new tag"""
        name = params.name
        response = self.client.create_tag(name)
        validated = Tag(**response)
        return self.prepare_response(validated, "N8nTagCard")
    
    def delete_tag(self, params: DeleteTagParams) -> ApiResponse:
        """Delete a tag by ID"""
        tag_id = params.id
        self.client.delete_tag(tag_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
    
    def update_tag(self, params: UpdateTagParams) -> ApiResponse:
        """Update a tag"""
        tag_id = params.id
        name = params.name
        response = self.client.update_tag(tag_id, name)
        validated = Tag(**response)
        return self.prepare_response(validated, "N8nTagCard")

    # Source Control operations
    def pull_from_source_control(self, params: PullOptions) -> ApiResponse:
        """Pull changes from the remote repository"""
        data = params.model_dump(exclude_none=True)
        response = self.client.pull_from_source_control(data)
        validated = PullResult(**response)
        return self.prepare_response(validated, "N8nPullResult")
    
    # Variable operations
    def list_variables(self, params: ListVariablesParams) -> ApiResponse:
        """List all variables"""
        cursor = params.cursor
        limit = params.limit
        response = self.client.list_variables(cursor, limit)
        
        variables = response.get("data", []) if isinstance(response, dict) else response
        variables_list = VariablesList(
            data=[Variable(**variable) for variable in variables],
            nextCursor=response.get("nextCursor") if isinstance(response, dict) else None
        )
            
        return self.prepare_response(variables_list, "N8nVariablesList")
    
    def create_variable(self, params: CreateVariableParams) -> ApiResponse:
        """Create a new variable"""
        data = params.model_dump(exclude_none=True)
        response = self.client.create_variable(data)
        validated = Variable(**response)
        return self.prepare_response(validated, "N8nVariableCard")
    
    def delete_variable(self, params: DeleteVariableParams) -> ApiResponse:
        """Delete a variable by ID"""
        variable_id = params.id
        self.client.delete_variable(variable_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)

    # Project operations
    def list_projects(self, params: ListProjectsParams) -> ApiResponse:
        """List all projects"""
        cursor = params.cursor
        limit = params.limit
        response = self.client.list_projects(cursor, limit)
        
        projects = response.get("data", []) if isinstance(response, dict) else response
        projects_list = ProjectsList(
            data=[Project(**project) for project in projects],
            nextCursor=response.get("nextCursor") if isinstance(response, dict) else None
        )
            
        return self.prepare_response(projects_list, "N8nProjectsList")
    
    def create_project(self, params: CreateProjectParams) -> ApiResponse:
        """Create a new project"""
        data = params.model_dump(exclude_none=True)
        response = self.client.create_project(data)
        validated = Project(**response)
        return self.prepare_response(validated, "N8nProjectCard")
    
    def update_project(self, params: UpdateProjectParams) -> ApiResponse:
        """Update a project"""
        project_id = params.id
        name = params.name
        self.client.update_project(project_id, name)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
    
    def delete_project(self, params: DeleteProjectParams) -> ApiResponse:
        """Delete a project by ID"""
        project_id = params.id
        self.client.delete_project(project_id)
        success_response = SuccessResponse(success=True)
        return self.prepare_response(success_response, None)
