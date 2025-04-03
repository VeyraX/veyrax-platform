from typing import Optional, List, Dict, Any, Union
from .client import LinearClient
from .schema import (
    IssueList, Issue, ProjectList, Project,
    IssueCreate, IssueUpdate, CommentCreate, IssueFilter, CommentResponse, UserList, User, TeamList, Team,
    WorkflowState, WorkflowStateList, ApiResponse, LabelListItem, LabelList
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class LinearService:
    def __init__(self, client: LinearClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "linear"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def list_issues(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_issues(cursor, max_results)
        
        if not response or 'data' not in response or 'issues' not in response['data']:
            raise ValueError("Invalid response format from Linear API")
        
        data = response['data']['issues']
        if not data or 'nodes' not in data or 'pageInfo' not in data:
            raise ValueError("Missing required fields in Linear API response")
        
        issues = [Issue(**issue) for issue in data['nodes']]
        issues_list = IssueList(
            items=issues,
            cursor=data['pageInfo'].get('endCursor')
        )
        
        return self.prepare_response(issues_list, "LinearIssueCard")

    def search_issues(self, query: str, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        # Check if query matches ID format (Linear IDs are UUIDs)
        search_id = query if len(query) == 36 and '-' in query else None
        
        response = self.client.search_issues(
            search_term=query,
            cursor=cursor,
            max_results=max_results
        )
        
        if not response or 'data' not in response or 'issues' not in response['data']:
            raise ValueError("Invalid response format from Linear API")
        
        data = response['data']['issues']
        
        issues = [Issue(**issue) for issue in data['nodes']]
        issues_list = IssueList(
            items=issues,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(issues_list, "LinearIssueCard")

    def filter_issues(self, filters: IssueFilter, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        # Convert filters to Linear's GraphQL format
        graphql_filters = {}
        
        filter_dict = filters.dict(exclude_none=True)
        
        if filter_dict.get('assignee_id'):
            graphql_filters['assignee'] = {'id': {'eq': filter_dict['assignee_id']}}
        if filter_dict.get('creator_id'):
            graphql_filters['creator'] = {'id': {'eq': filter_dict['creator_id']}}
        if filter_dict.get('project_id'):
            graphql_filters['project'] = {'id': {'eq': filter_dict['project_id']}}
        if filter_dict.get('state_id'):
            graphql_filters['state'] = {'id': {'eq': filter_dict['state_id']}}
        if filter_dict.get('priority') is not None:
            graphql_filters['priority'] = {'eq': filter_dict['priority']}
        if filter_dict.get('created_after'):
            graphql_filters['createdAt'] = {'gt': filter_dict['created_after'].isoformat()}
        if filter_dict.get('created_before'):
            graphql_filters['createdAt'] = {'lt': filter_dict['created_before'].isoformat()}

        response = self.client.filter_issues(graphql_filters, cursor, max_results)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        
        data = response['data']['issues']
        
        issues = [Issue(**issue) for issue in data['nodes']]
        issues_list = IssueList(
            items=issues,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(issues_list, "LinearIssueCard")

    def create_issue(self, issue_create: IssueCreate) -> ApiResponse:
        # Convert label names to IDs
        issue_data = issue_create.dict(exclude_none=True)
        
        # Transform field names for Linear API
        issue_data['teamId'] = issue_data.pop('team_id')
        if 'assignee_id' in issue_data:
            issue_data['assigneeId'] = issue_data.pop('assignee_id')
        if 'project_id' in issue_data:
            issue_data['projectId'] = issue_data.pop('project_id')
        if 'state_id' in issue_data:
            issue_data['stateId'] = issue_data.pop('state_id')
        if 'labels' in issue_data:
            # Convert label names to IDs (implementation needed)
            issue_data['labelIds'] = self._convert_label_names_to_ids(issue_data.pop('labels'))
            
        response = self.client.create_issue(issue_data)
        
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        issue = Issue(**response['data']['issueCreate']['issue'])
        return self.prepare_response(issue, "LinearIssueCard")

    def _convert_label_names_to_ids(self, label_names: List[str]) -> List[str]:
        """Convert label names to their Linear IDs (case-insensitive)"""
        all_labels = []
        cursor = None
        
        # Paginate through all labels
        while True:
            response = self.client.list_labels(cursor=cursor)
            data = response.get('data', {}).get('issueLabels', {})
            
            if not data:
                break
                
            batch = data.get('nodes', [])
            all_labels.extend([(label['id'], label['name']) for label in batch])
            
            if data.get('pageInfo', {}).get('hasNextPage'):
                cursor = data['pageInfo'].get('endCursor')
            else:
                break

        # Create case-insensitive mapping while preserving original case matches
        lower_to_original = {name.lower(): (id, name) for id, name in all_labels}
        
        # Match input names case-insensitively but preserve input order
        return [
            lower_to_original[name.lower()][0]  # Get ID from tuple
            for name in label_names
            if name.lower() in lower_to_original
        ]

    def update_issue(self, issue_id: str, issue_update: IssueUpdate) -> ApiResponse:
        update_data = issue_update.dict(exclude_none=True)
        
        field_mappings = {
            'assignee_id': 'assigneeId',
            'project_id': 'projectId',
            'state_id': 'stateId'
        }
        
        transformed_data = {}
        for key, value in update_data.items():
            if key == 'labels':
                transformed_data['labelIds'] = self._convert_label_names_to_ids(value)
            else:
                new_key = field_mappings.get(key, key)
                transformed_data[new_key] = value
        
        response = self.client.update_issue(issue_id, transformed_data)
        
        if 'errors' in response:
            error_msg = response.get('errors', [{}])[0].get('message', 'Unknown error')
            raise ValueError(f"GraphQL Error: {error_msg}")
        
        update_result = response.get('data', {}).get('issueUpdate')
        if not update_result or not update_result.get('success'):
            raise ValueError("Failed to update issue")
            
        issue = Issue(**update_result['issue'])
        return self.prepare_response(issue, "LinearIssueCard")

    def comment_issue(self, issue_id: str, comment: CommentCreate) -> ApiResponse:
        response = self.client.create_comment(issue_id, comment.body)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        
        data = response['data']['commentCreate']
        if not data['success']:
            raise ValueError("Failed to create comment")
        
        comment_response = CommentResponse.parse_obj(data['comment'])
        return self.prepare_response(comment_response, None)

    def list_projects(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_projects(cursor, max_results)
        data = response['data']['projects']
        
        projects = [Project(**project) for project in data['nodes']]
        projects_list = ProjectList(
            items=projects,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(projects_list, "LinearProjectList")

    def get_project(self, project_id: str) -> ApiResponse:
        response = self.client.get_project(project_id)
        project = Project(**response['data']['project'])
        return self.prepare_response(project, "LinearProjectCard")

    def list_users(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_users(cursor, max_results)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        data = response['data']['users']
        
        users = [User(**user) for user in data['nodes']]
        users_list = UserList(
            items=users,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(users_list, None)

    def list_teams(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_teams(cursor, max_results)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        data = response['data']['teams']
        
        teams = [Team(**team) for team in data['nodes']]
        teams_list = TeamList(
            items=teams,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(teams_list, "LinearTeamList")

    def get_team(self, team_id: str) -> ApiResponse:
        response = self.client.get_team(team_id)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        team = Team(**response['data']['team'])
        return self.prepare_response(team, None)

    def list_workflow_states(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_workflow_states(cursor, max_results)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        data = response['data']['workflowStates']
        
        states = [WorkflowState(**state) for state in data['nodes']]
        states_list = WorkflowStateList(
            items=states,
            cursor=data['pageInfo']['endCursor']
        )
        
        return self.prepare_response(states_list, "LinearWorkflowStateList")

    def list_labels(self, cursor: Optional[str] = None, max_results: int = 50) -> ApiResponse:
        response = self.client.list_labels(cursor, max_results)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        
        data = response['data']['issueLabels']
        
        labels = [
            LabelListItem(
                id=label['id'],
                name=label['name'],
                color=label.get('color')
            ) for label in data['nodes']
        ]

        label_list = LabelList(
            items=labels,
            cursor=data['pageInfo']['endCursor']
        )

        # Convert to dict for serialization
        return self.prepare_response(label_list.dict(), "LinearLabelList")
