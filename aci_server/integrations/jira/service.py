from typing import Optional, Dict, Any, List
from .client import JiraClient
from .schema import (
    JiraServerInfo, JiraCredentials, IssueList, Issue, 
    IssueCreate, IssueUpdate, IssueFilters, Project, StatusCategory, Status, Priority, IssueType, Field, FieldSchema, JiraUser
)
from datetime import datetime
from fastapi import HTTPException
import os 

class JiraService:
    def __init__(self, client: JiraClient):
        self.client = client
        self._initialize_service()

    def _initialize_service(self):
        resources = self.client.get_accessible_resources()
        if not resources:
            raise Exception("No Jira resources available")
        
        resource = resources[0]
        cloud_id = resource['id']
        self.site_id = resource.get('url', '').split('/')[-1].replace('.atlassian.net', '')
        self.base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        self.cloud_id = cloud_id

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        return self.client.make_request(
            self.base_url,
            method,
            endpoint,
            **kwargs
        )

    def _generate_html_link(self, issue_key: str) -> str:
        return f"https://{self.site_id}.atlassian.net/browse/{issue_key}"

    def get_issues(self, filters: Optional[IssueFilters] = None) -> IssueList:
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
                comments=[],  # Comments are loaded separately if needed
                labels=issue['fields'].get('labels', []),
                components=[c['name'] for c in issue['fields'].get('components', [])]
            )
            for issue in response['issues']
        ]
        
        return IssueList(
            issues=issues,
            total=response['total'],
            start_at=response['startAt']
        )

    def get_issue(self, issue_id: str) -> Issue:
        issue = self._make_request('GET', f'issue/{issue_id}')
        comments = self._make_request('GET', f'issue/{issue_id}/comment')
        
        return Issue(
            **self._format_issue_base(issue),
            comments=comments.get('comments', []),
            labels=issue['fields'].get('labels', []),
            components=[c['name'] for c in issue['fields'].get('components', [])]
        )

    def create_issue(self, issue_create: IssueCreate) -> Issue:
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
        
        return self.get_issue(response['id'])

    def _get_allowed_transitions(self, issue_id: str) -> List[Dict[str, Any]]:
        response = self._make_request('GET', f'issue/{issue_id}/transitions')
        return response.get('transitions', [])

    def _validate_status_transition(self, issue_id: str, new_status_id: str) -> bool:
        allowed_transitions = self._get_allowed_transitions(issue_id)
        return any(t['id'] == new_status_id for t in allowed_transitions)

    def update_issue(self, issue_id: str, update: IssueUpdate) -> Issue:
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

    def delete_issue(self, issue_id: str) -> None:
        self._make_request(
            'DELETE',
            f'issue/{issue_id}'
        )

    def _format_issue_base(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        if not issue or 'fields' not in issue:
            raise HTTPException(status_code=500, detail="Invalid issue format")
        
        fields = issue.get('fields', {})
        return {
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

    def get_all_projects(self) -> List[Project]:
        projects = self._make_request('GET', 'project')
        return [Project(
            id=p['id'],
            key=p['key'],
            name=p['name'],
            description=p.get('description'),
            lead=p.get('lead', {}).get('displayName'),
            url=p['self'],
            components=p.get('components', []),
            versions=p.get('versions', [])
        ) for p in projects]

    def get_project_details(self, project_id: str) -> Project:
        project = self._make_request('GET', f'project/{project_id}')
        return Project(
            id=project['id'],
            key=project['key'],
            name=project['name'],
            description=project.get('description'),
            lead=project.get('lead', {}).get('displayName'),
            url=project['self'],
            components=project.get('components', []),
            versions=project.get('versions', [])
        )

    def get_all_statuses(self) -> List[Status]:
        statuses = self._make_request('GET', 'status')
        return [Status(
            id=s['id'],
            name=s['name'],
            description=s.get('description'),
            category=StatusCategory(**s['statusCategory'])
        ) for s in statuses]

    def get_all_priorities(self) -> List[Priority]:
        priorities = self._make_request('GET', 'priority')
        return [Priority(**p) for p in priorities]

    def get_all_issue_types(self) -> List[IssueType]:
        issue_types = self._make_request('GET', 'issuetype')
        return [IssueType(**it) for it in issue_types]

    def get_all_fields(self) -> List[Field]:
        fields = self._make_request('GET', 'field')
        return [
            Field(
                **{
                    **f,
                    'schema': FieldSchema(**f['schema']) if 'schema' in f else None
                }
            )
            for f in fields
        ]

    def get_users(self, query: Optional[str] = None) -> List[JiraUser]:
        resources = self.client.get_accessible_resources()
        
        if not resources:
            raise Exception("No Jira resources available")
        
        cloud_id = resources[0]['id']
        base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}"
        
        users = self.client.get_users(query, base_url)
        
        return [
            JiraUser(
                account_id=user['accountId'],
                email=user.get('emailAddress'),
                display_name=user['displayName'],
                active=user['active']
            )
            for user in users
        ]