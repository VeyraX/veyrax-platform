from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union, Literal

# Common parameters
class TeamParams(BaseModel):
    team_id: Optional[str] = Field(
        None,
        description="The Team identifier to perform the request on behalf of"
    )
    slug: Optional[str] = Field(
        None,
        description="The Team slug to perform the request on behalf of"
    )

# List Deployments Parameters
class ListDeploymentsParams(TeamParams):
    app: Optional[str] = Field(
        None,
        description="Name of the deployment"
    )
    limit: Optional[int] = Field(
        None,
        description="Maximum number of deployments to list from a request"
    )
    project_id: Optional[str] = Field(
        None,
        description="Filter deployments from the given ID or name"
    )
    target: Optional[str] = Field(
        None,
        description="Filter deployments based on the environment (e.g., production, preview)"
    )
    users: Optional[str] = Field(
        None,
        description="Filter out deployments based on users who have created the deployment"
    )
    since: Optional[int] = Field(
        None,
        description="Get Deployments created after this JavaScript timestamp"
    )
    until: Optional[int] = Field(
        None,
        description="Get Deployments created before this JavaScript timestamp"
    )
    state: Optional[str] = Field(
        None,
        description="Filter deployments based on their state (BUILDING, ERROR, INITIALIZING, QUEUED, READY, CANCELED)"
    )
    rollback_candidate: Optional[bool] = Field(
        None,
        description="Filter deployments based on their rollback candidacy"
    )

# Get Deployment Parameters
class GetDeploymentParams(TeamParams):
    id_or_url: str = Field(
        ...,
        description="The deployment ID or URL to retrieve"
    )
    with_git_repo_info: Optional[bool] = Field(
        None,
        description="Whether to add in gitRepo information"
    )

# Create Deployment Parameters
class GitMetadata(BaseModel):
    remote_url: Optional[str] = Field(None, description="Remote URL of the Git repository")
    commit_author_name: Optional[str] = Field(None, description="Name of the commit author")
    commit_message: Optional[str] = Field(None, description="Commit message")
    commit_ref: Optional[str] = Field(None, description="Commit reference (branch, tag)")
    commit_sha: Optional[str] = Field(None, description="Commit SHA")
    dirty: Optional[bool] = Field(None, description="Whether the working directory has uncommitted changes")

class GitSource(BaseModel):
    type: Literal["github", "gitlab", "bitbucket"] = Field(..., description="Git provider type")
    repo_id: str = Field(..., description="Repository ID or name (e.g. 'username/repo-name')")
    ref: Optional[str] = Field(None, description="Git reference (branch, tag)")
    sha: Optional[str] = Field(None, description="Commit SHA")

class ProjectSettings(BaseModel):
    build_command: Optional[str] = Field(None, description="Build command")
    command_for_ignoring_build_step: Optional[str] = Field(None, description="Command to determine if build can be skipped")
    dev_command: Optional[str] = Field(None, description="Development command")
    framework: str = Field(..., description="Framework preset")
    install_command: Optional[str] = Field(None, description="Install command")
    node_version: Optional[str] = Field(None, description="Node.js version")
    output_directory: Optional[str] = Field(None, description="Output directory")
    root_directory: Optional[str] = Field(None, description="Root directory")
    serverless_function_region: Optional[str] = Field(None, description="Region for serverless functions")
    skip_git_connect_during_link: Optional[bool] = Field(None, description="Skip Git connection during project linking")
    source_files_outside_root_directory: Optional[bool] = Field(None, description="Allow source files outside root directory")

class InlinedFile(BaseModel):
    file: str = Field(..., description="File path")
    data: str = Field(..., description="File content (base64 encoded)")
    encoding: Literal["base64"] = Field("base64", description="Encoding of the file content")

class UploadedFile(BaseModel):
    file: str = Field(..., description="File path")
    sha: str = Field(..., description="SHA1 hash of the file content")
    size: int = Field(..., description="File size in bytes")

class CreateDeploymentParams(TeamParams):
    name: str = Field(..., description="Project name used in the deployment URL")
    project: Optional[str] = Field(None, description="The target project identifier")
    target: Optional[str] = Field(None, description="Environment target (production, preview, etc.)")
    git_source: Optional[GitSource] = Field(None, description="Git repository source")
    force_new: Optional[bool] = Field(False, description="Force a new deployment")
    skip_auto_detection_confirmation: Optional[bool] = Field(False, description="Skip auto detection confirmation")

# Delete Deployment Parameters
class DeleteDeploymentParams(TeamParams):
    url: Optional[str] = Field(
        None,
        description="A Deployment or Alias URL. In case it is passed, the ID will be ignored"
    )

# Cancel Deployment Parameters
class CancelDeploymentParams(TeamParams):
    pass

# Get Deployment Files Parameters
class GetDeploymentFilesParams(TeamParams):
    deployment_id: str = Field(
        ...,
        description="The ID of the deployment to retrieve files for"
    )

# Get Deployment Events Parameters
class GetDeploymentEventsParams(TeamParams):
    id_or_url: str = Field(
        ...,
        description="The unique identifier or hostname of the deployment"
    )
    direction: Optional[Literal["forward", "backward"]] = Field(
        "forward",
        description="Order of the returned events based on the timestamp"
    )
    follow: Optional[int] = Field(
        None,
        description="When enabled (1), this endpoint will return live events as they happen"
    )
    limit: Optional[int] = Field(
        None,
        description="Maximum number of events to return. Provide -1 to return all available logs"
    )
    name: Optional[str] = Field(
        None,
        description="Deployment build ID"
    )
    since: Optional[int] = Field(
        None,
        description="Timestamp for when build logs should be pulled from"
    )
    until: Optional[int] = Field(
        None,
        description="Timestamp for when the build logs should be pulled up until"
    )
    status_code: Optional[str] = Field(
        None,
        description="HTTP status code range to filter events by (e.g., '5xx')"
    )
    delimiter: Optional[int] = Field(
        None,
        description="Delimiter option for the response"
    )
    builds: Optional[int] = Field(
        None,
        description="Builds option for the response"
    )

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
    
    class Config:
        extra = "allow"  # Allow additional fields

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
    
    class Config:
        extra = "allow"  # Allow additional fields

# Update the recursive reference
DeploymentFileResponse.update_forward_refs()

# Deployment Event Response
class DeploymentEventInfo(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    entrypoint: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

class DeploymentEventResponse(BaseModel):
    type: str
    created: int
    date: Optional[int] = None
    deploymentId: Optional[str] = None
    id: Optional[str] = None
    text: Optional[str] = None
    serial: Optional[str] = None
    info: Optional[DeploymentEventInfo] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

# Add Domain to Project Parameters
class AddDomainToProjectParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    name: str = Field(
        ...,
        description="The project domain name"
    )
    git_branch: Optional[str] = Field(
        None,
        description="Git branch to link the project domain"
    )
    custom_environment_id: Optional[str] = Field(
        None,
        description="The unique custom environment identifier within the project"
    )
    redirect: Optional[str] = Field(
        None,
        description="Target destination domain for redirect"
    )
    redirect_status_code: Optional[int] = Field(
        None,
        description="Status code for domain redirect (301, 302, 307, 308)"
    )

# Create Project Parameters
class EnvironmentVariable(BaseModel):
    key: str = Field(..., description="Environment variable key")
    value: str = Field(..., description="Environment variable value")
    target: List[str] = Field(..., description="Environment targets (production, preview, development)")
    type: str = Field(..., description="Environment variable type (system, encrypted, plain)")
    git_branch: Optional[str] = Field(None, description="Git branch for the environment variable")

class GitRepository(BaseModel):
    repo: str = Field(..., description="Repository name")
    type: Literal["github", "gitlab", "bitbucket"] = Field(..., description="Git provider type")

class OidcTokenConfig(BaseModel):
    enabled: bool = Field(..., description="Whether OIDC token generation is enabled")
    issuer_mode: Literal["global", "team"] = Field(..., description="OIDC token issuer mode")

class CreateProjectParams(TeamParams):
    name: str = Field(
        ...,
        description="The desired name for the project"
    )
    build_command: Optional[str] = Field(
        None,
        description="The build command for this project"
    )
    command_for_ignoring_build_step: Optional[str] = Field(
        None,
        description="Command for ignoring build step"
    )
    dev_command: Optional[str] = Field(
        None,
        description="The dev command for this project"
    )
    environment_variables: Optional[List[EnvironmentVariable]] = Field(
        None,
        description="Collection of ENV Variables the Project will use"
    )
    framework: Optional[str] = Field(
        None,
        description="The framework that is being used for this project"
    )
    git_repository: Optional[GitRepository] = Field(
        None,
        description="The Git Repository that will be connected to the project"
    )
    install_command: Optional[str] = Field(
        None,
        description="The install command for this project"
    )
    skip_git_connect_during_link: Optional[bool] = Field(
        None,
        description="Opts-out of the message prompting a CLI user to connect a Git repository"
    )
    output_directory: Optional[str] = Field(
        None,
        description="The output directory of the project"
    )
    public_source: Optional[bool] = Field(
        None,
        description="Specifies whether the source code and logs of the deployments should be public"
    )
    root_directory: Optional[str] = Field(
        None,
        description="The name of a directory or relative path to the source code"
    )
    serverless_function_region: Optional[str] = Field(
        None,
        description="The region to deploy Serverless Functions in this project"
    )
    serverless_function_zero_config_failover: Optional[bool] = Field(
        None,
        description="Specifies whether Zero Config Failover is enabled for this project"
    )
    oidc_token_config: Optional[OidcTokenConfig] = Field(
        None,
        description="OpenID Connect JSON Web Token generation configuration"
    )
    enable_affected_projects_deployments: Optional[bool] = Field(
        None,
        description="Opt-in to skip deployments when there are no changes to the root directory"
    )

# Create Environment Variables Parameters
class EnvVarData(BaseModel):
    key: str = Field(
        ...,
        description="Environment variable key"
    )
    value: str = Field(
        ...,
        description="Environment variable value"
    )
    type: Literal["plain", "secret", "system", "encrypted"] = Field(
        ...,
        description="Environment variable type"
    )
    target: List[str] = Field(
        ...,
        description="Environment targets (production, preview, development)"
    )
    git_branch: Optional[str] = Field(
        None,
        description="Git branch for the environment variable"
    )
    comment: Optional[str] = Field(
        None,
        description="Comment for the environment variable"
    )
    custom_environment_ids: Optional[List[str]] = Field(
        None,
        description="Custom environment IDs"
    )

class CreateEnvVarsParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    env_vars: Union[EnvVarData, List[EnvVarData]] = Field(
        ...,
        description="Environment variable(s) to create"
    )
    upsert: Optional[bool] = Field(
        None,
        description="Allow override of environment variable if it already exists"
    )

# Delete Project Parameters
class DeleteProjectParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )

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
    
    class Config:
        extra = "allow"  # Allow additional fields from the API

class EnvVarErrorResponse(BaseModel):
    error: Dict[str, Any]

class CreateEnvVarsResponse(BaseModel):
    created: Optional[EnvVarCreatedResponse] = None
    failed: Optional[List[EnvVarErrorResponse]] = None

# Edit Environment Variable Parameters
class EditEnvVarParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    env_var_id: str = Field(
        ...,
        description="The unique environment variable identifier"
    )
    key: Optional[str] = Field(
        None,
        description="The name of the environment variable"
    )
    value: Optional[str] = Field(
        None,
        description="The value of the environment variable"
    )
    type: Optional[Literal["plain", "secret", "system", "encrypted", "sensitive"]] = Field(
        None,
        description="The type of environment variable"
    )
    target: Optional[List[str]] = Field(
        None,
        description="The target environment of the environment variable"
    )
    git_branch: Optional[str] = Field(
        None,
        description="If defined, the git branch of the environment variable (must have target=preview)"
    )
    custom_environment_ids: Optional[List[str]] = Field(
        None,
        description="The custom environments that the environment variable should be synced to"
    )
    comment: Optional[str] = Field(
        None,
        description="A comment to add context on what this env var is for"
    )

# Get Project Parameters
class GetProjectParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )

# Get Project Domain Parameters
class GetProjectDomainParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    domain: str = Field(
        ...,
        description="The project domain name"
    )

# Remove Environment Variable Parameters
class RemoveEnvVarParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    env_var_id: str = Field(
        ...,
        description="The unique environment variable identifier"
    )
    custom_environment_id: Optional[str] = Field(
        None,
        description="The unique custom environment identifier within the project"
    )

# List Projects Parameters
class ListProjectsParams(TeamParams):
    from_timestamp: Optional[str] = Field(
        None,
        description="Query only projects updated after the given timestamp"
    )
    git_fork_protection: Optional[str] = Field(
        None,
        description="Specifies whether PRs from Git forks should require a team member's authorization before it can be deployed"
    )
    limit: Optional[str] = Field(
        None,
        description="Limit the number of projects returned"
    )
    search: Optional[str] = Field(
        None,
        description="Search projects by the name field"
    )
    repo: Optional[str] = Field(
        None,
        description="Filter results by repo. Also used for project count"
    )
    repo_id: Optional[str] = Field(
        None,
        description="Filter results by Repository ID"
    )
    repo_url: Optional[str] = Field(
        None,
        description="Filter results by Repository URL"
    )
    exclude_repos: Optional[str] = Field(
        None,
        description="Filter results by excluding those projects that belong to a repo"
    )
    edge_config_id: Optional[str] = Field(
        None,
        description="Filter results by connected Edge Config ID"
    )
    edge_config_token_id: Optional[str] = Field(
        None,
        description="Filter results by connected Edge Config Token ID"
    )
    deprecated: Optional[bool] = Field(
        None,
        description="Filter by deprecated status"
    )

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
    
    class Config:
        extra = "allow"

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
    
    class Config:
        extra = "allow" 

class ProjectResponse(BaseModel):
    id: str
    name: str
    account_id: str
    created_at: int
    updated_at: int
    framework: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    pagination: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

# Project Domains Response
class ProjectDomainsResponse(BaseModel):
    domains: List[ProjectDomainResponse]
    pagination: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

# Update ApiResponse to include new response types
class ApiResponse(BaseModel):
    data: Union[
        DeploymentResponse,
        DeploymentListResponse,
        DeleteDeploymentResponse,
        List[DeploymentFileResponse],
        List[DeploymentEventResponse],
        AddDomainResponse,
        Dict[str, Any],  # For project creation response
        CreateEnvVarsResponse,
        EnvVarResponse,
        List[EnvVarResponse],
        ProjectResponse,
        ProjectDomainResponse,
        ProjectDomainsResponse,
        Dict[str, str]   # For empty responses like delete project
    ]
    component: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        description="UI components configuration for rendering results"
    )

class GetProjectDomainsParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    production: Optional[bool] = Field(
        None,
        description="Filters only production domains when set to true"
    )
    target: Optional[Literal["production", "preview"]] = Field(
        None,
        description="Filters on the target of the domain"
    )
    custom_environment_id: Optional[str] = Field(
        None,
        description="The unique custom environment identifier within the project"
    )
    git_branch: Optional[str] = Field(
        None,
        description="Filters domains based on specific branch"
    )
    redirects: Optional[bool] = Field(
        None,
        description="Excludes redirect project domains when 'false'. Includes redirect project domains when 'true' (default)"
    )
    redirect: Optional[str] = Field(
        None,
        description="Filters domains based on their redirect target"
    )
    verified: Optional[bool] = Field(
        None,
        description="Filters domains based on their verification status"
    )
    limit: Optional[int] = Field(
        None,
        description="Maximum number of domains to list from a request (max 100)"
    )
    since: Optional[int] = Field(
        None,
        description="Get domains created after this JavaScript timestamp"
    )
    until: Optional[int] = Field(
        None,
        description="Get domains created before this JavaScript timestamp"
    )
    order: Optional[Literal["ASC", "DESC"]] = Field(
        None,
        description="Domains sort order by createdAt"
    )

# Verify Project Domain Parameters
class VerifyProjectDomainParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    domain: str = Field(
        ...,
        description="The domain name you want to verify"
    )

# Update Project Parameters
class UpdateProjectParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    auto_expose_system_envs: Optional[bool] = Field(
        None,
        description="Whether to automatically expose system environment variables"
    )
    build_command: Optional[str] = Field(
        None,
        description="The build command for this project"
    )
    dev_command: Optional[str] = Field(
        None,
        description="The dev command for this project"
    )
    framework: Optional[str] = Field(
        None,
        description="The framework that is being used for this project"
    )
    git_fork_protection: Optional[bool] = Field(
        None,
        description="Specifies whether PRs from Git forks should require a team member's authorization"
    )
    install_command: Optional[str] = Field(
        None,
        description="The install command for this project"
    )
    name: Optional[str] = Field(
        None,
        description="The desired name for the project. Must be lowercase, up to 100 characters, and can include letters, digits, '.', '_', '-', but cannot contain '---'."
    )
    node_version: Optional[str] = Field(
        None,
        description="The Node.js version for this project"
    )
    output_directory: Optional[str] = Field(
        None,
        description="The output directory of the project"
    )
    public_source: Optional[bool] = Field(
        None,
        description="Specifies whether the source code and logs of the deployments should be public"
    )
    root_directory: Optional[str] = Field(
        None,
        description="The name of a directory or relative path to the source code"
    )
    serverless_function_region: Optional[str] = Field(
        None,
        description="The region to deploy Serverless Functions in this project"
    )

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

# Project Domains Response
class ProjectDomainsResponse(BaseModel):
    domains: List[ProjectDomainResponse]
    pagination: Optional[Dict[str, Any]] = None

class GetProjectEnvVarsParams(TeamParams):
    project_id_or_name: str = Field(
        ...,
        description="The unique project identifier or the project name"
    )
    decrypt: Optional[bool] = Field(
        None,
        description="Whether to decrypt the environment variable values"
    )
    custom_environment_id: Optional[str] = Field(
        None,
        description="The unique custom environment identifier within the project"
    )
    git_branch: Optional[str] = Field(
        None,
        description="The git branch to filter environment variables by"
    )
