from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union, Literal

# Common parameters
class TeamParams(BaseModel):
    team_id: Optional[str] = None
    slug: Optional[str] = None

# List Deployments Parameters
class ListDeploymentsParams(TeamParams):
    app: Optional[str] = None
    limit: Optional[int] = None
    project_id: Optional[str] = None
    target: Optional[str] = None
    users: Optional[str] = None
    since: Optional[int] = None
    until: Optional[int] = None
    state: Optional[str] = None
    rollback_candidate: Optional[bool] = None

# Get Deployment Parameters
class GetDeploymentParams(TeamParams):
    id_or_url: str
    with_git_repo_info: Optional[bool] = None

# Create Deployment Parameters
class InlinedFile(BaseModel):
    file: str
    data: str
    encoding: Literal["base64"] = "base64"

class UploadedFile(BaseModel):
    file: str
    sha: str
    size: int

class GitMetadata(BaseModel):
    remote_url: Optional[str] = None
    commit_author_name: Optional[str] = None
    commit_message: Optional[str] = None
    commit_ref: Optional[str] = None
    commit_sha: Optional[str] = None
    dirty: Optional[bool] = None

class GitSource(BaseModel):
    type: Literal["github", "gitlab", "bitbucket"]
    repo_id: Union[str, int] = Field(..., description="Numerical ID of the repository, not the 'username/repo-name' format")
    ref: Optional[str] = None
    sha: Optional[str] = None

class ProjectSettings(BaseModel):
    build_command: Optional[str] = None
    command_for_ignoring_build_step: Optional[str] = None
    dev_command: Optional[str] = None
    framework: Optional[str] = None
    install_command: Optional[str] = None
    node_version: Optional[str] = None
    output_directory: Optional[str] = None
    root_directory: Optional[str] = None
    serverless_function_region: Optional[str] = None
    skip_git_connect_during_link: Optional[bool] = None
    source_files_outside_root_directory: Optional[bool] = None

class CreateDeploymentParams(TeamParams):
    name: str
    target: Optional[str] = None
    git_source: Optional[GitSource] = None
    project: Optional[str] = None
    files: Optional[List[InlinedFile]] = None
    project_settings: Optional[ProjectSettings] = None
    meta: Optional[Dict[str, Any]] = None
    force_new: Optional[bool] = True
    skip_auto_detection_confirmation: Optional[bool] = None

# Delete Deployment Parameters
class DeleteDeploymentParams(TeamParams):
    url: Optional[str] = None
    deployment_id: str

# Cancel Deployment Parameters
class CancelDeploymentParams(TeamParams):
    deployment_id: str

# Get Deployment Events Parameters
class GetDeploymentEventsParams(TeamParams):
    id_or_url: str
    direction: Optional[Literal["forward", "backward"]] = "forward"
    follow: Optional[int] = None
    limit: Optional[int] = None
    name: Optional[str] = None
    since: Optional[int] = None
    until: Optional[int] = None
    status_code: Optional[str] = None
    delimiter: Optional[int] = None
    builds: Optional[int] = None

# Response Models
class Creator(BaseModel):
    uid: Optional[str] = None
    username: Optional[str] = None
    avatar: Optional[str] = None

class Team(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    avatar: Optional[str] = None

class ProjectInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    framework: Optional[str] = None

class DeploymentGitSource(BaseModel):
    type: str
    repo_id: Optional[Union[str, int]] = None
    ref: Optional[str] = None
    sha: Optional[str] = None
    pr_id: Optional[str] = None

class DeploymentResponse(BaseModel):
    id: str
    name: str
    url: Optional[str] = None
    created_at: int
    creator: Optional[Creator] = None
    team: Optional[Team] = None
    project: Optional[ProjectInfo] = None
    target: Optional[str] = None
    ready_state: str
    state: Optional[str] = None
    type: str
    git_source: Optional[DeploymentGitSource] = None
    meta: Optional[Dict[str, Any]] = None

class DeploymentListResponse(BaseModel):
    deployments: List[DeploymentResponse]
    pagination: Optional[Dict[str, Any]] = None

class DeleteDeploymentResponse(BaseModel):
    uid: str
    state: str

class DeploymentFileResponse(BaseModel):
    name: str
    type: str
    uid: str
    children: Optional[List['DeploymentFileResponse']] = None
    content_type: Optional[str] = None
    mode: Optional[int] = None
    symlink: Optional[str] = None

# Update the recursive reference
DeploymentFileResponse.update_forward_refs()

# Deployment Event Response
class DeploymentEventInfo(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    entrypoint: Optional[str] = None

class DeploymentEventResponse(BaseModel):
    type: str
    created: int
    date: Optional[int] = None
    deploymentId: Optional[str] = None
    id: Optional[str] = None
    text: Optional[str] = None
    serial: Optional[str] = None
    info: Optional[DeploymentEventInfo] = None

# Add Domain to Project Parameters
class AddDomainToProjectParams(TeamParams):
    project_id_or_name: str
    name: str
    git_branch: Optional[str] = None
    custom_environment_id: Optional[str] = None
    redirect: Optional[str] = None
    redirect_status_code: Optional[int] = None

# Create Project Parameters
class EnvironmentVariable(BaseModel):
    key: str
    value: str
    target: List[str]
    type: str
    git_branch: Optional[str] = None

class GitRepository(BaseModel):
    repo: str
    type: Literal["github", "gitlab", "bitbucket"]

class OidcTokenConfig(BaseModel):
    enabled: bool
    issuer_mode: Literal["global", "team"]

class CreateProjectParams(TeamParams):
    name: str
    build_command: Optional[str] = None
    command_for_ignoring_build_step: Optional[str] = None
    dev_command: Optional[str] = None
    environment_variables: Optional[List[EnvironmentVariable]] = None
    framework: Optional[str] = None
    git_repository: Optional[GitRepository] = None
    install_command: Optional[str] = None
    skip_git_connect_during_link: Optional[bool] = None
    output_directory: Optional[str] = None
    public_source: Optional[bool] = None
    root_directory: Optional[str] = None
    serverless_function_region: Optional[str] = None
    serverless_function_zero_config_failover: Optional[bool] = None
    oidc_token_config: Optional[OidcTokenConfig] = None
    enable_affected_projects_deployments: Optional[bool] = None

# Create Environment Variables Parameters
class EnvVarData(BaseModel):
    key: str
    value: str
    type: Literal["plain", "secret", "system", "encrypted"]
    target: List[str]
    git_branch: Optional[str] = None
    comment: Optional[str] = None
    custom_environment_ids: Optional[List[str]] = None

class CreateEnvVarsParams(TeamParams):
    project_id_or_name: str
    env_vars: Union[EnvVarData, List[EnvVarData]]
    upsert: Optional[bool] = None

# Delete Project Parameters
class DeleteProjectParams(TeamParams):
    project_id_or_name: str

# Response Models for new endpoints
class DomainVerification(BaseModel):
    type: str
    domain: str
    value: str
    reason: Optional[str] = None

class AddDomainResponse(BaseModel):
    name: str
    apex_name: str
    project_id: str
    redirect: Optional[str] = None
    redirect_status_code: Optional[int] = None
    git_branch: Optional[str] = None
    custom_environment_id: Optional[str] = None
    updated_at: int
    created_at: int
    verified: bool
    verification: List[DomainVerification]

class EnvVarCreatedResponse(BaseModel):
    target: List[str]
    type: str
    id: str
    key: str
    value: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    git_branch: Optional[str] = None
    comment: Optional[str] = None
    custom_environment_ids: Optional[List[str]] = None
    system: Optional[bool] = None

class EnvVarErrorResponse(BaseModel):
    error: Dict[str, Any]

class CreateEnvVarsResponse(BaseModel):
    created: Optional[EnvVarCreatedResponse] = None
    failed: Optional[List[EnvVarErrorResponse]] = None

# Edit Environment Variable Parameters
class EditEnvVarParams(TeamParams):
    project_id_or_name: str
    env_var_id: str
    key: Optional[str] = None
    value: Optional[str] = None
    type: Optional[Literal["plain", "secret", "system", "encrypted", "sensitive"]] = None
    target: Optional[List[str]] = None
    git_branch: Optional[str] = None
    custom_environment_ids: Optional[List[str]] = None
    comment: Optional[str] = None

# Get Project Parameters
class GetProjectParams(TeamParams):
    project_id_or_name: str

# Get Project Domain Parameters
class GetProjectDomainParams(TeamParams):
    project_id_or_name: str
    domain: str

# Remove Environment Variable Parameters
class RemoveEnvVarParams(TeamParams):
    project_id_or_name: str
    env_var_id: str
    custom_environment_id: Optional[str] = None

# List Projects Parameters
class ListProjectsParams(TeamParams):
    from_timestamp: Optional[str] = None
    git_fork_protection: Optional[str] = None
    limit: Optional[str] = None
    search: Optional[str] = None
    repo: Optional[str] = None
    repo_id: Optional[str] = None
    repo_url: Optional[str] = None
    exclude_repos: Optional[str] = None
    edge_config_id: Optional[str] = None
    edge_config_token_id: Optional[str] = None
    deprecated: Optional[bool] = None

# Response Models for new endpoints
class EnvVarResponse(BaseModel):
    target: List[str]
    type: str
    id: str
    key: str
    value: Optional[str] = None
    created_at: int
    updated_at: int
    git_branch: Optional[str] = None
    comment: Optional[str] = None
    custom_environment_ids: Optional[List[str]] = None

class ProjectDomainResponse(BaseModel):
    name: str
    apex_name: str
    project_id: str
    redirect: Optional[str] = None
    redirect_status_code: Optional[int] = None
    git_branch: Optional[str] = None
    custom_environment_id: Optional[str] = None
    updated_at: int
    created_at: int
    verified: bool
    verification: List[DomainVerification]

# Добавим модель для информации о репозитории в ответе проекта
class ProjectGitRepository(BaseModel):
    type: str
    repo: Optional[str] = None
    repo_id: Optional[Union[str, int]] = None
    provider_repo_id: Optional[Union[str, int]] = None
    org: Optional[str] = None
    owner: Optional[str] = None
    slug: Optional[str] = None
    private: Optional[bool] = None
    branch: Optional[str] = None

# Обновим модель ProjectResponse, чтобы включить информацию о репозитории
class ProjectResponse(BaseModel):
    id: str
    name: str
    account_id: str
    created_at: int
    updated_at: int
    framework: Optional[str] = None
    git: Optional[ProjectGitRepository] = None  # Добавляем поле для информации о репозитории

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    pagination: Optional[Dict[str, Any]] = None

# Project Domains Response
class ProjectDomainsResponse(BaseModel):
    domains: List[ProjectDomainResponse]
    pagination: Optional[Dict[str, Any]] = None

class GetProjectDomainsParams(TeamParams):
    project_id_or_name: str
    production: Optional[bool] = None
    target: Optional[Literal["production", "preview"]] = None
    custom_environment_id: Optional[str] = None
    git_branch: Optional[str] = None
    redirects: Optional[bool] = None
    redirect: Optional[str] = None
    verified: Optional[bool] = None
    limit: Optional[int] = None
    since: Optional[int] = None
    until: Optional[int] = None
    order: Optional[Literal["ASC", "DESC"]] = None

# Verify Project Domain Parameters
class VerifyProjectDomainParams(TeamParams):
    project_id_or_name: str
    domain: str

# Update Project Parameters
class UpdateProjectParams(TeamParams):
    project_id_or_name: str
    auto_expose_system_envs: Optional[bool] = None
    build_command: Optional[str] = None
    dev_command: Optional[str] = None
    framework: Optional[str] = None
    git_fork_protection: Optional[bool] = None
    install_command: Optional[str] = None
    name: Optional[str] = None
    node_version: Optional[str] = None
    output_directory: Optional[str] = None
    public_source: Optional[bool] = None
    root_directory: Optional[str] = None
    serverless_function_region: Optional[str] = None

    @validator('name')
    def validate_project_name(cls, v):
        if v is None:
            return v
            
        if len(v) > 100:
            raise ValueError("Project name must be up to 100 characters long")
            
        if v != v.lower():
            raise ValueError("Project name must be lowercase")
            
        import re
        if not re.match(r'^[a-z0-9._-]+$', v):
            raise ValueError("Project name can only include lowercase letters, digits, and the characters '.', '_', '-'")
            
        if '---' in v:
            raise ValueError("Project name cannot contain the sequence '---'")
            
        return v

class GetProjectEnvVarsParams(TeamParams):
    project_id_or_name: str
    decrypt: Optional[bool] = None
    custom_environment_id: Optional[str] = None
    git_branch: Optional[str] = None

# Добавляем новую модель для ответа на удаление проекта
class DeleteProjectResponse(BaseModel):
    status: str
    message: str

# Добавляем новую модель для стандартизации ответов с сообщениями
class StatusMessageResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ApiResponse(BaseModel):
    data: Union[
        DeploymentResponse,
        DeploymentListResponse,
        DeleteDeploymentResponse,
        List[DeploymentFileResponse],
        List[DeploymentEventResponse],
        AddDomainResponse,
        ProjectResponse,
        ProjectListResponse,
        CreateEnvVarsResponse,
        EnvVarResponse,
        List[EnvVarResponse],
        ProjectDomainResponse,
        ProjectDomainsResponse,
        DeleteProjectResponse,
        StatusMessageResponse,
        Dict[str, str],
        Dict[str, Any]
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None