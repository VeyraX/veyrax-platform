from typing import Optional, List
from .client import LinearClient
from .schema import (
    IssueList, Issue, ProjectList, Project,
    IssueCreate, IssueUpdate, CommentCreate, IssueFilter, CommentResponse, UserList, TeamList, Team
)

class LinearService:
    def __init__(self, client: LinearClient):
        self.client = client

    def list_issues(self, cursor: Optional[str] = None) -> IssueList:
        response = self.client.list_issues(cursor)
        if not response or 'data' not in response or 'issues' not in response['data']:
            raise ValueError("Invalid response format from Linear API")
            
        data = response['data']['issues']
        if not data or 'nodes' not in data or 'pageInfo' not in data:
            raise ValueError("Missing required fields in Linear API response")
            
        return IssueList(
            issues=[self._parse_issue(issue) for issue in data['nodes']],
            cursor=data['pageInfo'].get('endCursor')
        )

    def search_issues(self, query: str, cursor: Optional[str] = None) -> IssueList:
        response = self.client.search_issues(query, cursor)
        data = response['data']['issueSearch']
        return IssueList(
            issues=[self._parse_issue(issue) for issue in data['nodes']],
            cursor=data['pageInfo']['endCursor']
        )

    def filter_issues(self, filters: IssueFilter, cursor: Optional[str] = None) -> IssueList:
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

        try:
            response = self.client.filter_issues(graphql_filters, cursor)
            if 'errors' in response:
                raise ValueError(f"GraphQL Error: {response['errors']}")
            
            data = response['data']['issues']
            return IssueList(
                issues=[self._parse_issue(issue) for issue in data['nodes']],
                cursor=data['pageInfo']['endCursor']
            )
        except Exception as e:
            raise ValueError(f"Error filtering issues: {str(e)}")

    def create_issue(self, issue_create: IssueCreate) -> Issue:
        issue_data = issue_create.dict(exclude_none=True)
        issue_data['teamId'] = issue_data.pop('team_id')
        if 'assignee_id' in issue_data:
            issue_data['assigneeId'] = issue_data.pop('assignee_id')
        if 'project_id' in issue_data:
            issue_data['projectId'] = issue_data.pop('project_id')
        if 'state_id' in issue_data:
            issue_data['stateId'] = issue_data.pop('state_id')

        response = self.client.create_issue(issue_data)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        return self._parse_issue(response['data']['issueCreate']['issue'])

    def update_issue(self, issue_id: str, issue_update: IssueUpdate) -> Issue:
        response = self.client.update_issue(
            issue_id, 
            issue_update.dict(exclude_none=True)
        )
        return self._parse_issue(response['data']['issueUpdate']['issue'])

    def comment_issue(self, issue_id: str, comment: CommentCreate) -> CommentResponse:
        response = self.client.create_comment(issue_id, comment.body)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        
        data = response['data']['commentCreate']
        if not data['success']:
            raise ValueError("Failed to create comment")
        
        comment_data = data['comment']
        return CommentResponse(
            id=comment_data['id'],
            body=comment_data['body'],
            created_at=comment_data['createdAt'],
            user=self._parse_user(comment_data.get('user'))
        )

    def get_activity_feed(self) -> List[dict]:
        try:
            response = self.client.get_activity_feed()
            if 'errors' in response:
                raise ValueError(f"GraphQL Error: {response['errors']}")
            
            return response['data']['organizationActivity']['nodes']
        except Exception as e:
            raise ValueError(f"Error getting activity feed: {str(e)}")

    def list_projects(self, cursor: Optional[str] = None) -> ProjectList:
        response = self.client.list_projects(cursor)
        data = response['data']['projects']
        return ProjectList(
            projects=[self._parse_project(project) for project in data['nodes']],
            cursor=data['pageInfo']['endCursor']
        )

    def get_project(self, project_id: str) -> Project:
        response = self.client.get_project(project_id)
        return self._parse_project(response['data']['project'])

    def list_users(self, cursor: Optional[str] = None) -> UserList:
        response = self.client.list_users(cursor)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        data = response['data']['users']
        return UserList(
            users=[self._parse_user(user) for user in data['nodes']],
            cursor=data['pageInfo']['endCursor']
        )

    def list_teams(self, cursor: Optional[str] = None) -> TeamList:
        response = self.client.list_teams(cursor)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
            
        data = response['data']['teams']
        return TeamList(
            teams=[self._parse_team(team) for team in data['nodes']],
            cursor=data['pageInfo']['endCursor']
        )

    def get_team(self, team_id: str) -> Team:
        response = self.client.get_team(team_id)
        if 'errors' in response:
            raise ValueError(f"GraphQL Error: {response['errors']}")
        return self._parse_team(response['data']['team'])

    def _parse_issue(self, issue: dict) -> Issue:
        if not issue:
            raise ValueError("Cannot parse empty issue")
            
        state = issue.get('state', {})
        if not isinstance(state, dict):
            state = {}
            
        return Issue(
            id=issue.get('id', ''),
            title=issue.get('title', ''),
            description=issue.get('description'),
            state=state.get('name', 'unknown'),
            priority=issue.get('priority'),
            assignee=self._parse_user(issue.get('assignee')) if issue.get('assignee') else None,
            creator=self._parse_user(issue.get('creator', {})),
            created_at=issue.get('createdAt'),
            updated_at=issue.get('updatedAt'),
            labels=[label['name'] for label in issue.get('labels', {}).get('nodes', [])] if issue.get('labels') else None,
            project_id=issue.get('project', {}).get('id') if issue.get('project') else None,
            team_id=issue.get('team', {}).get('id')
        )

    def _parse_user(self, user: dict) -> dict:
        if not user:
            return {'id': '', 'name': 'Unknown', 'email': None}
        return {
            'id': user.get('id', ''),
            'name': user.get('name', 'Unknown'),
            'email': user.get('email')
        }

    def _parse_project(self, project: dict) -> Project:
        return Project(
            id=project['id'],
            name=project['name'],
            description=project.get('description'),
            state=project['state'],
            created_at=project['createdAt'],
            updated_at=project['updatedAt'],
            lead=self._parse_user(project['lead']) if project.get('lead') else None
        )

    def _parse_activity(self, activity: dict) -> dict:
        return {
            'id': activity['id'],
            'type': activity['type'],
            'created_at': activity['createdAt'],
            'user': self._parse_user(activity['user']),
            'target': activity.get('issue', {})
        }

    def _parse_team(self, team: dict) -> Team:
        return Team(
            id=team['id'],
            name=team['name'],
            key=team['key'],
            description=team.get('description')
        )