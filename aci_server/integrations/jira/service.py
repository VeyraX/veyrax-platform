from typing import Optional, Dict, Any, List, Union
from .client import JiraClient
from .schema import (
    IssueList, Issue, 
    IssueCreate, IssueUpdate, IssueFilters, Project, StatusCategory, Status, Priority, IssueType, Field, FieldSchema, JiraUser
)
from fastapi import HTTPException
import os
from ..common.component_handler import load_components, prepare_components_auto, create_component, find_component, wrap_component_with_tool
import json

class JiraService:
    def __init__(self, client: JiraClient):
        self.client = client
        self._initialize_service()
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Union[Issue, IssueList, Project, List[Project]], component_name: str = None):
        tool_name = "jira"


        if component_name == 'JiraStatusesTable':
            component_def = find_component(self.components_data, 'JiraStatusesTable')
            component = create_component(component_def, data)
            component = wrap_component_with_tool(component, tool_name)
            return {"data": data, "component": component}
        else:
            components = prepare_components_auto(data, component_name, self.components_data, tool_name)
            return {"data": data, "component": components}

    def _initialize_service(self):
        resources = self.client.get_accessible_resources()
        if not resources:
            raise Exception("No Jira resources available")
        
        resource = resources[0]
        cloud_id = resource['id']
        self.site_id = resource.get('url', '').split('/')[-1].replace('.atlassian.net', '')
        self.base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        self.cloud_id = cloud_id
        self.browser_base_url = f"https://{self.site_id}.atlassian.net"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.client.make_request(
            self.base_url,
            method,
            endpoint,
            **kwargs
        )

    def _generate_html_link(self, issue_key: str) -> str:
        return f"{self.browser_base_url}/browse/{issue_key}"

    def get_issues(self, filters: Optional[IssueFilters] = None):
        jql_parts = []
        
        if filters:
            if filters.project_id:
                jql_parts.append(f'project = {filters.project_id}')
            if filters.status_id:
                jql_parts.append(f'status = {filters.status_id}')
            if filters.assignee:
                jql_parts.append(f'assignee = "{filters.assignee}"')
            if filters.created_after:
                jql_parts.append(f'created >= "{filters.created_after.strftime("%Y-%m-%d")}"')
            if filters.created_before:
                jql_parts.append(f'created <= "{filters.created_before.strftime("%Y-%m-%d")}"')
            if filters.priority_id:
                jql_parts.append(f'priority = {filters.priority_id}')
        
        jql = ' AND '.join(jql_parts) if jql_parts else "order by created DESC"
        
        response = self._make_request(
            'GET',
            'search',
            params={
                'jql': jql,
                'startAt': 0,
                'maxResults': filters.max_results if filters and filters.max_results else 50
            }
        )
        
        issues = [
            Issue(
                **self._format_issue_base(issue),
                comments=[],
                labels=issue['fields'].get('labels', []),
                components=[c['name'] for c in issue['fields'].get('components', [])]
            )
            for issue in response['issues']
        ]
        
        issue_list = IssueList(
            issues=issues,
            total=response['total'],
            start_at=response['startAt']
        )
        
        return self.prepare_response(issue_list, "JiraIssueCard")

    def get_issue(self, issue_id: str):
        issue = self._make_request('GET', f'issue/{issue_id}')
        comments = self._make_request('GET', f'issue/{issue_id}/comment')
        
        issue_obj = Issue(
            **self._format_issue_base(issue),
            comments=comments.get('comments', []),
            labels=issue['fields'].get('labels', []),
            components=[c['name'] for c in issue['fields'].get('components', [])]
        )
        
        return self.prepare_response(issue_obj, "JiraIssueCard")

    def create_issue(self, issue_create: IssueCreate):
        fields = {
            'project': {'id': str(issue_create.project_id)},
            'summary': issue_create.summary,
            'issuetype': {'id': str(issue_create.issue_type_id)}
        }
        
        optional_fields = {
            'description': issue_create.description,
            'assignee': {'id': issue_create.assignee_id} if issue_create.assignee_id else None,
            'priority': {'id': issue_create.priority_id} if issue_create.priority_id else None,
            'parent': {'key': issue_create.parent_issue_key} if issue_create.parent_issue_key else None,
            'status': {'id': issue_create.status_id} if issue_create.status_id else None,
            'labels': issue_create.labels,
            'components': [{'name': c} for c in issue_create.components] if issue_create.components else None
        }
        
        fields.update({k: v for k, v in optional_fields.items() if v is not None})
        
        response = self._make_request('POST', 'issue', json={'fields': fields})
        
        if issue_create.status_id:
            issue_key = response['key']
            self._make_request(
                'POST',
                f'issue/{issue_key}/transitions',
                json={'transition': {'id': issue_create.status_id}}
            )
        
        # Get the issue data and return it properly
        issue_data = self.get_issue(response['id'])
        
        return issue_data  # The get_issue method already calls prepare_response

    def _get_allowed_transitions(self, issue_id: str) -> List[Dict[str, Any]]:
        response = self._make_request('GET', f'issue/{issue_id}/transitions')
        return response.get('transitions', [])

    def _validate_status_transition(self, issue_id: str, new_status_id: str) -> bool:
        allowed_transitions = self._get_allowed_transitions(issue_id)
        return any(t['id'] == new_status_id for t in allowed_transitions)

    def update_issue(self, issue_id: str, update: IssueUpdate):
        fields = {}
        
        if update.summary is not None:
            fields['summary'] = update.summary
        if update.description is not None:
            fields['description'] = update.description
        if update.assignee_id is not None:
            fields['assignee'] = {'id': update.assignee_id}
        if update.priority_id is not None:
            fields['priority'] = {'id': update.priority_id}
        if update.labels is not None:
            fields['labels'] = update.labels
        if update.components is not None:
            fields['components'] = [{'name': c} for c in update.components]
            
        if fields:
            self._make_request(
                'PUT',
                f'issue/{issue_id}',
                json={'fields': fields}
            )
        
        if update.status_id is not None:
            if not self._validate_status_transition(issue_id, update.status_id):
                current_status = self.get_issue(issue_id).status.name
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot transition from status '{current_status}' to status '{update.status_id}'. "
                          f"Check the workflow for the issue."
                )
                
            self._make_request(
                'POST',
                f'issue/{issue_id}/transitions',
                json={'transition': {'id': update.status_id}}
            )
        
        return self.get_issue(issue_id)

    def delete_issue(self, issue_id: str) -> Dict[str, Any]:
        self._make_request(
            'DELETE',
            f'issue/{issue_id}'
        )
        
        return {"status": "success"}

    def _format_issue_base(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        if not issue or 'fields' not in issue:
            raise HTTPException(status_code=500, detail="Invalid issue format")
        
        fields = issue.get('fields', {})
        return {
            'id': issue.get('id', ''),
            'key': issue.get('key', ''),
            'summary': fields.get('summary', ''),
            'description': fields.get('description'),
            'status': fields.get('status'),
            'created': fields.get('created'),
            'updated': fields.get('updated'),
            'assignee': fields.get('assignee'),
            'reporter': fields.get('reporter', {}).get('displayName') if fields.get('reporter') else None,
            'priority': fields.get('priority'),
            'url': self._generate_html_link(issue.get('key', ''))
        }

    def get_all_projects(self):
        projects = self._make_request('GET', 'project')
        project_list = [Project(
            id=p['id'],
            key=p['key'],
            name=p['name'],
            description=p.get('description'),
            lead=p.get('lead', {}).get('displayName'),
            url=f"{self.browser_base_url}/projects/{p['key']}",
            components=p.get('components', []),
            versions=p.get('versions', [])
        ) for p in projects]

        print("get all projects", projects)
        
        return self.prepare_response(project_list, "JiraProjectCard")

    def get_project_details(self, project_id: str):
        project = self._make_request('GET', f'project/{project_id}')
        project_obj = Project(
            id=project['id'],
            key=project['key'],
            name=project['name'],
            description=project.get('description'),
            lead=project.get('lead', {}).get('displayName'),
            url=f"{self.browser_base_url}/projects/{project['key']}",
            components=project.get('components', []),
            versions=project.get('versions', [])
        )
        
        return self.prepare_response(project_obj, "JiraProjectCard")

    def get_all_statuses(self) -> Dict[str, Any]:
        statuses = self._make_request('GET', 'status')
        status_list = [Status(
            id=s['id'],
            name=s['name'],
            description=s.get('description'),
            category=StatusCategory(**s['statusCategory'])
        ) for s in statuses]

        
        return self.prepare_response(status_list, "JiraStatusesTable")

    def get_all_priorities(self) -> Dict[str, Any]:
        priorities = self._make_request('GET', 'priority')
        priority_list = [Priority(**p) for p in priorities]
        
        return self.prepare_response(priority_list, "JiraStatusesTable")

    def get_all_issue_types(self) -> Dict[str, Any]:
        issue_types = self._make_request('GET', 'issuetype')
        issue_type_list = [IssueType(**it) for it in issue_types]
        
        return self.prepare_response(issue_type_list, "JiraDataTable")

    def get_all_fields(self) -> Dict[str, Any]:
        fields = self._make_request('GET', 'field')
        field_list = [
            Field(
                **{
                    **f,
                    'schema': FieldSchema(**f['schema']) if 'schema' in f else None
                }
            )
            for f in fields
        ]
        
        return self.prepare_response(field_list, "JiraDataTable")

    def get_users(self, query: Optional[str] = None) -> Dict[str, Any]:
        resources = self.client.get_accessible_resources()
        
        if not resources:
            raise Exception("No Jira resources available")
        
        cloud_id = resources[0]['id']
        base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        
        users = self.client.get_users(query, base_url)
        
        user_list = [
            JiraUser(
                account_id=user['accountId'],
                email=user.get('emailAddress'),
                display_name=user['displayName'],
                active=user['active']
            )
            for user in users
        ]
        
        return self.prepare_response(user_list, "JiraDataTable")