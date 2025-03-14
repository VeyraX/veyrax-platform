from typing import Optional, List, Dict, Any, Union
from .client import FigmaClient
from .schema import (
    ApiResponse, File, FileList, NodeList, Component, ComponentList,
    Style, StyleList, User, Project, Comment, CommentList,
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class FigmaService:
    def __init__(self, client: FigmaClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "figma"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _convert_to_file(self, file_data: Dict[str, Any]) -> File:
        return File(
            key=file_data.get('key', ''),
            name=file_data.get('name', ''),
            thumbnail_url=file_data.get('thumbnail_url'),
            last_modified=file_data.get('last_modified'),
            version=file_data.get('version'),
            document=file_data.get('document')
        )

    def _convert_to_component(self, component_data: Dict[str, Any]) -> Component:
        user = None
        if component_data.get('user'):
            user = User(
                id=component_data['user'].get('id', ''),
                handle=component_data['user'].get('handle', ''),
                img_url=component_data['user'].get('img_url')
            )
            
        return Component(
            key=component_data.get('key', ''),
            name=component_data.get('name', ''),
            description=component_data.get('description'),
            node_id=component_data.get('node_id', ''),
            thumbnail_url=component_data.get('thumbnail_url'),
            created_at=component_data.get('created_at'),
            updated_at=component_data.get('updated_at'),
            user=user,
            containing_frame=component_data.get('containing_frame')
        )

    def _convert_to_style(self, style_data: Dict[str, Any]) -> Style:
        user = None
        if style_data.get('user'):
            user = User(
                id=style_data['user'].get('id', ''),
                handle=style_data['user'].get('handle', ''),
                img_url=style_data['user'].get('img_url')
            )
            
        return Style(
            key=style_data.get('key', ''),
            name=style_data.get('name', ''),
            description=style_data.get('description'),
            style_type=style_data.get('style_type', ''),
            node_id=style_data.get('node_id'),
            thumbnail_url=style_data.get('thumbnail_url'),
            created_at=style_data.get('created_at'),
            updated_at=style_data.get('updated_at'),
            user=user
        )

    def get_file(self, file_key: str) -> ApiResponse:
        try:
            response = self.client.get_file(file_key)
            file = self._convert_to_file(response)
            return self.prepare_response(file, "FigmaFileDetail")
        except Exception as e:
            raise ValueError(f"Error getting file: {str(e)}")

    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> ApiResponse:
        try:
            response = self.client.get_file_nodes(file_key, node_ids)
            return self.prepare_response(NodeList(nodes=response.get('nodes', {})), "FigmaNodeList")
        except Exception as e:
            raise ValueError(f"Error getting file nodes: {str(e)}")

    def get_image(self, file_key: str, node_ids: List[str], format: str = "png", scale: float = 1) -> ApiResponse:
        try:
            response = self.client.get_image(file_key, node_ids, format, scale)
            return self.prepare_response(response.get('images', {}), "FigmaImageList")
        except Exception as e:
            raise ValueError(f"Error getting images: {str(e)}")

    def get_file_components(self, file_key: str) -> ApiResponse:
        try:
            response = self.client.get_file_components(file_key)
            components = [self._convert_to_component(comp) for comp in response.get('meta', {}).get('components', [])]
            
            component_list = ComponentList(
                items=components,
                cursor=response.get('cursor')
            )
            
            return self.prepare_response(component_list, "FigmaComponentList")
        except Exception as e:
            raise ValueError(f"Error getting file components: {str(e)}")

    def get_component_sets(self, file_key: str) -> ApiResponse:
        try:
            response = self.client.get_component_sets(file_key)
            return self.prepare_response(response, "FigmaComponentSetList")
        except Exception as e:
            raise ValueError(f"Error getting component sets: {str(e)}")

    def get_styles(self, file_key: str) -> ApiResponse:
        try:
            response = self.client.get_styles(file_key)
            styles = [self._convert_to_style(style) for style in response.get('meta', {}).get('styles', [])]
            
            style_list = StyleList(
                items=styles,
                cursor=response.get('cursor')
            )
            
            return self.prepare_response(style_list, "FigmaStyleList")
        except Exception as e:
            raise ValueError(f"Error getting styles: {str(e)}")

    def get_me(self) -> ApiResponse:
        try:
            response = self.client.get_me()
            user = User(
                id=response.get('id', ''),
                handle=response.get('handle', ''),
                img_url=response.get('img_url'),
                email=response.get('email')
            )
            return self.prepare_response(user, "FigmaUserDetail")
        except Exception as e:
            raise ValueError(f"Error getting user information: {str(e)}")

    def get_team_projects(self, team_id: str) -> ApiResponse:
        try:
            response = self.client.get_team_projects(team_id)
            projects = []
            for proj_data in response.get('projects', []):
                projects.append(Project(
                    id=proj_data.get('id', ''),
                    name=proj_data.get('name', ''),
                    thumbnail_url=proj_data.get('thumbnail_url'),
                    last_modified=proj_data.get('last_modified')
                ))
            return self.prepare_response(projects, "FigmaProjectList")
        except Exception as e:
            raise ValueError(f"Error getting team projects: {str(e)}")

    def get_project_files(self, project_id: str, branch_name: Optional[str] = None) -> ApiResponse:
        try:
            response = self.client.get_project_files(project_id, branch_name)
            files = []
            for file_data in response.get('files', []):
                files.append(self._convert_to_file(file_data))
            
            file_list = FileList(
                items=files,
                cursor=response.get('cursor')
            )
            
            return self.prepare_response(file_list, "FigmaFileList")
        except Exception as e:
            raise ValueError(f"Error getting project files: {str(e)}")

    def get_all_nodes(self, file_key: str) -> ApiResponse:
        try:
            file_response = self.client.get_file(file_key)
            
            node_ids = []
            
            def extract_node_ids(node):
                if 'id' in node:
                    node_ids.append(node['id'])
                
                if 'children' in node and node['children']:
                    for child in node['children']:
                        extract_node_ids(child)
            
            if 'document' in file_response:
                extract_node_ids(file_response['document'])
            
            batch_size = 100
            all_nodes = {}
            
            for i in range(0, len(node_ids), batch_size):
                batch_ids = node_ids[i:i+batch_size]
                batch_response = self.client.get_file_nodes(file_key, batch_ids)
                if 'nodes' in batch_response:
                    all_nodes.update(batch_response['nodes'])
            
            return self.prepare_response(NodeList(nodes=all_nodes), "FigmaNodeList")
        except Exception as e:
            raise ValueError(f"Error getting all nodes: {str(e)}")
