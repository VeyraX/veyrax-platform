from typing import Optional, Dict, Any, List, Union
from .client import VercelClient
from .schema import (
    DeploymentResponse, DeploymentListResponse, DeleteDeploymentResponse,
    DeploymentFileResponse, ApiResponse, ListDeploymentsParams, GetDeploymentParams,
    CreateDeploymentParams, DeleteDeploymentParams, CancelDeploymentParams,
    GetDeploymentFilesParams, GetDeploymentEventsParams, DeploymentEventResponse,
    AddDomainToProjectParams, CreateProjectParams, CreateEnvVarsParams, DeleteProjectParams,
    AddDomainResponse, EnvVarCreatedResponse, EnvVarErrorResponse, CreateEnvVarsResponse,
    EditEnvVarParams, GetProjectParams, GetProjectDomainParams, RemoveEnvVarParams,
    ListProjectsParams, EnvVarResponse, ProjectDomainResponse, GetProjectDomainsParams,
    VerifyProjectDomainParams, UpdateProjectParams, ProjectDomainsResponse,
    GetProjectEnvVarsParams
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class VercelService:
    def __init__(self, client: VercelClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[DeploymentResponse, DeploymentListResponse, DeleteDeploymentResponse, List[DeploymentFileResponse]], component_name: str = None) -> ApiResponse:
        tool_name = "vercel"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_deployments(self, params: Optional[ListDeploymentsParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.list_deployments(params_dict)
        
        deployments = []
        for item in response.get('deployments', []):
            deployment = self._convert_to_deployment_response(item)
            deployments.append(deployment)
            
        deployment_list = DeploymentListResponse(
            deployments=deployments,
            pagination=response.get('pagination')
        )
        
        return ApiResponse(data=deployment_list)

    def get_deployment(self, id_or_url: str, params: Optional[GetDeploymentParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.get_deployment(id_or_url, params_dict)
        
        deployment = self._convert_to_deployment_response(response)
        return ApiResponse(data=deployment)

    def create_deployment(self, params: CreateDeploymentParams) -> ApiResponse:
        params_dict = params.dict(exclude_none=True)
        
        data = {}
        for key, value in params_dict.items():
            if key in ["team_id", "slug"]:
                continue 
            
            if isinstance(value, dict):
                camel_case_dict = {}
                for k, v in value.items():
                    parts = k.split('_')
                    camel_k = parts[0] + ''.join(x.title() for x in parts[1:])
                    camel_case_dict[camel_k] = v
                
                if key == "git_source":
                    data["gitSource"] = camel_case_dict
                else:
                    parts = key.split('_')
                    camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
                    data[camel_key] = camel_case_dict
            else:
                parts = key.split('_')
                camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
                data[camel_key] = value
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.create_deployment(data)
        
        deployment = self._convert_to_deployment_response(response)
        return ApiResponse(data=deployment)

    def delete_deployment(self, deployment_id: str, params: Optional[DeleteDeploymentParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.delete_deployment(deployment_id, params_dict)
        
        delete_response = DeleteDeploymentResponse(
            uid=response.get('uid', ''),
            state=response.get('state', '')
        )
        
        return ApiResponse(data=delete_response)

    def cancel_deployment(self, deployment_id: str, params: Optional[CancelDeploymentParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.cancel_deployment(deployment_id, params_dict)
        
        deployment = self._convert_to_deployment_response(response)
        return ApiResponse(data=deployment)

    def get_deployment_files(self, deployment_id: str, params: Optional[GetDeploymentFilesParams] = None) -> ApiResponse:
        """List deployment files"""
        params_dict = params.dict(exclude_none=True) if params else {}
        response = self.client.get_deployment_files(deployment_id, params_dict)
        
        files = []
        for item in response:
            file = DeploymentFileResponse(
                name=item.get('name', ''),
                type=item.get('type', ''),
                uid=item.get('uid', ''),
                children=item.get('children'),
                content_type=item.get('contentType'),
                mode=item.get('mode'),
                symlink=item.get('symlink')
            )
            files.append(file)
            
        return ApiResponse(data=files)

    def get_deployment_events(self, id_or_url: str, params: Optional[GetDeploymentEventsParams] = None) -> ApiResponse:
        params_dict = params.dict(exclude_none=True) if params else {}
        
        if 'id_or_url' in params_dict:
            del params_dict['id_or_url']
            
        response = self.client.get_deployment_events(id_or_url, params_dict)
        
        events = []
        for item in response:
            event_data = {
                "type": item.get("type", ""),
                "created": item.get("created", 0),
                "date": item.get("date"),
                "deploymentId": item.get("deploymentId"),
                "id": item.get("id"),
                "serial": item.get("serial"),
                "info": item.get("info")
            }
            
            if "text" in item and item["text"] is not None:
                event_data["text"] = item["text"]
            elif "payload" in item and "text" in item["payload"]:
                event_data["text"] = item["payload"]["text"]
            else:
                event_data["text"] = f"[{item.get('type', 'event')}]"
            
            event = DeploymentEventResponse(**event_data)
            events.append(event)
            
        return ApiResponse(data=events)

    def _convert_to_deployment_response(self, item: Dict[str, Any]) -> DeploymentResponse:
        creator = None
        if 'creator' in item:
            creator = {
                'uid': item['creator'].get('uid'),
                'username': item['creator'].get('username'),
                'avatar': item['creator'].get('avatar')
            }
        
        team = None
        if 'team' in item:
            team = {
                'id': item['team'].get('id'),
                'name': item['team'].get('name'),
                'slug': item['team'].get('slug'),
                'avatar': item['team'].get('avatar')
            }
        
        project = None
        if 'project' in item:
            project = {
                'id': item['project'].get('id'),
                'name': item['project'].get('name'),
                'framework': item['project'].get('framework')
            }
        
        git_source = None
        if 'gitSource' in item:
            git_source = {
                'type': item['gitSource'].get('type', ''),
                'repo_id': item['gitSource'].get('repoId'),
                'ref': item['gitSource'].get('ref'),
                'sha': item['gitSource'].get('sha'),
                'pr_id': item['gitSource'].get('prId')
            }
        
        return DeploymentResponse(
            id=item.get('id', ''),
            name=item.get('name', ''),
            url=item.get('url'),
            created_at=item.get('createdAt'),
            creator=creator,
            team=team,
            project=project,
            target=item.get('target'),
            ready_state=item.get('readyState', ''),
            state=item.get('state'),
            type=item.get('type', ''),
            git_source=git_source,
            meta=item.get('meta')
        )

    def add_domain_to_project(self, params: AddDomainToProjectParams) -> ApiResponse:
        project_id_or_name = params.project_id_or_name
        
        data = {
            "name": params.name
        }
        
        if params.git_branch is not None:
            data["gitBranch"] = params.git_branch
        
        if params.custom_environment_id is not None:
            data["customEnvironmentId"] = params.custom_environment_id
        
        if params.redirect is not None:
            data["redirect"] = params.redirect
        
        if params.redirect_status_code is not None:
            data["redirectStatusCode"] = params.redirect_status_code
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.add_domain_to_project(project_id_or_name, data, query_params)
        
        domain_response = AddDomainResponse(
            name=response.get("name", ""),
            apex_name=response.get("apexName", ""),
            project_id=response.get("projectId", ""),
            redirect=response.get("redirect"),
            redirect_status_code=response.get("redirectStatusCode"),
            git_branch=response.get("gitBranch"),
            custom_environment_id=response.get("customEnvironmentId"),
            updated_at=response.get("updatedAt", 0),
            created_at=response.get("createdAt", 0),
            verified=response.get("verified", False),
            verification=response.get("verification", [])
        )
        
        return ApiResponse(data=domain_response)

    def create_project(self, params: CreateProjectParams) -> ApiResponse:
        params_dict = params.dict(exclude_none=True)
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        if "team_id" in params_dict:
            del params_dict["team_id"]
        if "slug" in params_dict:
            del params_dict["slug"]
        
        data = {}
        for key, value in params_dict.items():
            parts = key.split('_')
            camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
            data[camel_key] = value
        
        response = self.client.create_project(data, query_params)
        
        return ApiResponse(data=response)

    def create_env_vars(self, params: CreateEnvVarsParams) -> ApiResponse:
        project_id_or_name = params.project_id_or_name
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        if params.upsert:
            query_params["upsert"] = "true"
        
        if isinstance(params.env_vars, list):
            data = []
            for env_var in params.env_vars:
                env_data = env_var.dict(exclude_none=True, by_alias=False)
                formatted_data = {}
                for key, value in env_data.items():
                    parts = key.split('_')
                    camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
                    formatted_data[camel_key] = value
                data.append(formatted_data)
        else:
            # Single env var
            env_data = params.env_vars.dict(exclude_none=True, by_alias=False)
            # Convert snake_case to camelCase
            data = {}
            for key, value in env_data.items():
                parts = key.split('_')
                camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
                data[camel_key] = value
        
        response = self.client.create_env_vars(project_id_or_name, data, query_params)
        
        # Parse response
        result = CreateEnvVarsResponse()
        if "created" in response:
            result.created = EnvVarCreatedResponse(**response["created"])
        if "failed" in response:
            result.failed = [EnvVarErrorResponse(error=item) for item in response["failed"]]
        
        return ApiResponse(data=result)

    def delete_project(self, params: DeleteProjectParams) -> ApiResponse:
        """Delete a project"""
        project_id_or_name = params.project_id_or_name
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        self.client.delete_project(project_id_or_name, query_params)
        
        return ApiResponse(data={"status": "success", "message": "Project deleted successfully"})

    def edit_env_var(self, params: EditEnvVarParams) -> ApiResponse:
        """Edit an environment variable for a project"""
        project_id_or_name = params.project_id_or_name
        env_var_id = params.env_var_id
        
        data = {}
        if params.key is not None:
            data["key"] = params.key
        if params.value is not None:
            data["value"] = params.value
        if params.type is not None:
            data["type"] = params.type
        if params.target is not None:
            data["target"] = params.target
        if params.git_branch is not None:
            data["gitBranch"] = params.git_branch
        if params.custom_environment_ids is not None:
            data["customEnvironmentIds"] = params.custom_environment_ids
        if params.comment is not None:
            data["comment"] = params.comment
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.edit_env_var(project_id_or_name, env_var_id, data, query_params)
        
        env_var_response = self._convert_to_env_var_response(response)
        
        return ApiResponse(data=env_var_response)
    
    def get_project(self, params: GetProjectParams) -> ApiResponse:
        """Get a project by ID or name"""
        project_id_or_name = params.project_id_or_name
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.get_project(project_id_or_name, query_params)
        
        return ApiResponse(data=response)
    
    def get_project_domain(self, params: GetProjectDomainParams) -> ApiResponse:
        """Get a project domain by project ID/name and domain name"""
        project_id_or_name = params.project_id_or_name
        domain = params.domain
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.get_project_domain(project_id_or_name, domain, query_params)
        
        domain_response = ProjectDomainResponse(
            name=response.get("name", ""),
            apex_name=response.get("apexName", ""),
            project_id=response.get("projectId", ""),
            redirect=response.get("redirect"),
            redirect_status_code=response.get("redirectStatusCode"),
            git_branch=response.get("gitBranch"),
            custom_environment_id=response.get("customEnvironmentId"),
            updated_at=response.get("updatedAt", 0),
            created_at=response.get("createdAt", 0),
            verified=response.get("verified", False),
            verification=response.get("verification", [])
        )
        
        return ApiResponse(data=domain_response)
    
    def remove_env_var(self, params: RemoveEnvVarParams) -> ApiResponse:
        """Remove an environment variable from a project"""
        project_id_or_name = params.project_id_or_name
        env_var_id = params.env_var_id
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        if params.custom_environment_id:
            query_params["customEnvironmentId"] = params.custom_environment_id
        
        response = self.client.remove_env_var(project_id_or_name, env_var_id, query_params)
        
        if not response:
            return ApiResponse(data={"status": "success", "message": "Environment variable removed successfully"})
        
        if isinstance(response, list):
            env_vars = []
            for item in response:
                env_var = self._convert_to_env_var_response(item)
                env_vars.append(env_var)
            return ApiResponse(data=env_vars)
        
        if isinstance(response, dict):
            if "envs" in response:
                env_vars = []
                for item in response.get("envs", []):
                    env_var = self._convert_to_env_var_response(item)
                    env_vars.append(env_var)
                return ApiResponse(data=env_vars)
            return ApiResponse(data=response)
        
        return ApiResponse(data={"status": "success", "message": "Environment variable removed", "response": str(response)})
    
    def list_projects(self, params: Optional[ListProjectsParams] = None) -> ApiResponse:
        """Retrieve a list of projects"""
        params_dict = {}
        if params:
            for key, value in params.dict(exclude_none=True).items():
                if key in ["team_id", "slug"]:
                    params_dict[key] = value
                elif key == "from_timestamp":
                    params_dict["from"] = value
                elif key == "git_fork_protection":
                    params_dict["gitForkProtection"] = value
                elif key == "repo_id":
                    params_dict["repoId"] = value
                elif key == "repo_url":
                    params_dict["repoUrl"] = value
                elif key == "exclude_repos":
                    params_dict["excludeRepos"] = value
                elif key == "edge_config_id":
                    params_dict["edgeConfigId"] = value
                elif key == "edge_config_token_id":
                    params_dict["edgeConfigTokenId"] = value
                else:
                    params_dict[key] = value
        
        response = self.client.list_projects(params_dict)
        
        return ApiResponse(data=response)
    
    def _convert_to_env_var_response(self, item: Dict[str, Any]) -> EnvVarResponse:
        """Convert API response to EnvVarResponse model"""
        return EnvVarResponse(
            target=item.get("target", []),
            type=item.get("type", ""),
            id=item.get("id", ""),
            key=item.get("key", ""),
            value=item.get("value"),
            created_at=item.get("createdAt", 0),
            updated_at=item.get("updatedAt", 0),
            git_branch=item.get("gitBranch"),
            comment=item.get("comment"),
            custom_environment_ids=item.get("customEnvironmentIds")
        )

    def get_project_domains(self, params: GetProjectDomainsParams) -> ApiResponse:
        """Retrieve the domains associated with a given project"""
        project_id_or_name = params.project_id_or_name
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        if params.production is not None:
            query_params["production"] = params.production
        if params.target:
            query_params["target"] = params.target
        if params.custom_environment_id:
            query_params["customEnvironmentId"] = params.custom_environment_id
        if params.git_branch:
            query_params["gitBranch"] = params.git_branch
        if params.redirects is not None:
            query_params["redirects"] = params.redirects
        if params.redirect:
            query_params["redirect"] = params.redirect
        if params.verified is not None:
            query_params["verified"] = params.verified
        if params.limit:
            query_params["limit"] = params.limit
        if params.since:
            query_params["since"] = params.since
        if params.until:
            query_params["until"] = params.until
        if params.order:
            query_params["order"] = params.order
        
        response = self.client.get_project_domains(project_id_or_name, query_params)
        
        domains = []
        for item in response.get("domains", []):
            domain = ProjectDomainResponse(
                name=item.get("name", ""),
                apex_name=item.get("apexName", ""),
                project_id=item.get("projectId", ""),
                redirect=item.get("redirect"),
                redirect_status_code=item.get("redirectStatusCode"),
                git_branch=item.get("gitBranch"),
                custom_environment_id=item.get("customEnvironmentId"),
                updated_at=item.get("updatedAt", 0),
                created_at=item.get("createdAt", 0),
                verified=item.get("verified", False),
                verification=item.get("verification", [])
            )
            domains.append(domain)
        
        domains_response = ProjectDomainsResponse(
            domains=domains,
            pagination=response.get("pagination")
        )
        
        return ApiResponse(data={
            "domains": [domain.dict() for domain in domains],
            "pagination": response.get("pagination")
        })

    def verify_project_domain(self, params: VerifyProjectDomainParams) -> ApiResponse:
        """Verify a project domain"""
        project_id_or_name = params.project_id_or_name
        domain = params.domain
        
        # Prepare query parameters
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        response = self.client.verify_project_domain(project_id_or_name, domain, query_params)
        
        domain_response = ProjectDomainResponse(
            name=response.get("name", ""),
            apex_name=response.get("apexName", ""),
            project_id=response.get("projectId", ""),
            redirect=response.get("redirect"),
            redirect_status_code=response.get("redirectStatusCode"),
            git_branch=response.get("gitBranch"),
            custom_environment_id=response.get("customEnvironmentId"),
            updated_at=response.get("updatedAt", 0),
            created_at=response.get("createdAt", 0),
            verified=response.get("verified", False),
            verification=response.get("verification", [])
        )
        
        return ApiResponse(data=domain_response)

    def update_project(self, params: UpdateProjectParams) -> ApiResponse:
        project_id_or_name = params.project_id_or_name
        
        params_dict = params.dict(exclude_none=True)
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        
        if "team_id" in params_dict:
            del params_dict["team_id"]
        if "slug" in params_dict:
            del params_dict["slug"]
        if "project_id_or_name" in params_dict:
            del params_dict["project_id_or_name"]
        
        data = {}
        for key, value in params_dict.items():
            parts = key.split('_')
            camel_key = parts[0] + ''.join(x.title() for x in parts[1:])
            data[camel_key] = value
        
        response = self.client.update_project(project_id_or_name, data, query_params)
        
        return ApiResponse(data=response)

    def get_project_env_vars(self, params: GetProjectEnvVarsParams) -> ApiResponse:
        project_id_or_name = params.project_id_or_name
        
        query_params = {}
        if params.team_id:
            query_params["teamId"] = params.team_id
        if params.slug:
            query_params["slug"] = params.slug
        if params.decrypt is not None:
            query_params["decrypt"] = params.decrypt
        if params.custom_environment_id:
            query_params["customEnvironmentId"] = params.custom_environment_id
        if params.git_branch:
            query_params["gitBranch"] = params.git_branch
        
        response = self.client.get_project_env_vars(project_id_or_name, query_params)
        
        env_vars = []
        for item in response.get("envs", []):
            env_var = self._convert_to_env_var_response(item)
            env_vars.append(env_var)
        
        return ApiResponse(data=env_vars)