from typing import Optional, List, Dict, Any, Union
from .client import AsanaClient
from .schema import (
    Task, TaskList, Workspace, Project, ApiResponse,
    User, TimePeriod, GoalMetric, Goal, GoalList, UserList, WorkspaceList,
    Section, SectionList, Team, Tag, TimePeriodList
)
import os
from ..common.component_handler import load_components, prepare_components_auto

class AsanaService:
    def __init__(self, client: AsanaClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)
        
    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "asana"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    def _convert_to_task(self, task_data: Dict[str, Any]) -> Task:
        assignee = None
        if isinstance(task_data.get('assignee'), dict) and task_data['assignee'].get('gid'):
            assignee = User(
                gid=task_data['assignee'].get('gid'),
                name=task_data['assignee'].get('name', ''), 
                email=task_data['assignee'].get('email')
            )
        
        workspace = None
        workspace_data = task_data.get('workspace', {})
        if isinstance(workspace_data, dict) and workspace_data.get('gid') and workspace_data.get('name'):
            workspace = Workspace(
                gid=workspace_data['gid'],
                name=workspace_data['name']
            )
        
        projects = []
        if isinstance(task_data.get('projects'), list):
            for p in task_data['projects']:
                if isinstance(p, dict) and p.get('gid') and p.get('name'):
                    projects.append(Project(
                        gid=p['gid'],
                        name=p['name']
                    ))
        
        return Task(
            gid=task_data.get('gid', ''), 
            name=task_data.get('name', ''),
            completed=task_data.get('completed', False),
            due_on=task_data.get('due_on'),
            notes=task_data.get('notes'),
            assignee=assignee,
            workspace=workspace,
            projects=projects or None,  # Convert empty list to None
            parent=task_data.get('parent', {}).get('gid') if isinstance(task_data.get('parent'), dict) else None,
            created_at=task_data.get('created_at'),
            modified_at=task_data.get('modified_at')
        )

    def get_tasks(self, workspace_id: str, project_id: Optional[str] = None, 
                 assignee: Optional[str] = None, completed_since: Optional[str] = None, 
                 limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_tasks(
            workspace_id=workspace_id,
            project_id=project_id,
            assignee=assignee,
            completed_since=completed_since,
            limit=limit,
            offset=offset
        )
        
        tasks = [self._convert_to_task(task) for task in response.get('data', [])]
        
        task_list = TaskList(
            items=tasks,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(task_list, "AsanaTaskList")

    def get_task(self, task_id: str) -> ApiResponse:
        response = self.client.get_task(task_id)
        task = self._convert_to_task(response.get('data', {}))
        return self.prepare_response(task, "AsanaTaskDetail")

    def create_task(self, task_data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_task(task_data)
        task = self._convert_to_task(response.get('data', {}))
        return self.prepare_response(task, "AsanaTaskDetail")

    def update_task(self, task_id: str, task_update: Dict[str, Any]) -> ApiResponse:
        response = self.client.update_task(task_id, task_update)
        task = self._convert_to_task(response.get('data', {}))
        return self.prepare_response(task, "AsanaTaskDetail")

    def delete_task(self, task_id: str) -> ApiResponse:
        response = self.client.delete_task(task_id)
        return self.prepare_response(response.get('data', {}), None)

    def get_subtasks(self, task_id: str) -> ApiResponse:
        response = self.client.get_subtasks(task_id)
        subtasks = [self._convert_to_task(task) for task in response.get('data', [])]
        
        task_list = TaskList(
            items=subtasks,
            offset=None  # Subtasks endpoint doesn't support pagination in the same way
        )
        
        return self.prepare_response(task_list, "AsanaTaskList")

    def create_subtask(self, parent_task_id: str, subtask_data: Dict[str, Any]) -> ApiResponse:
        response = self.client.create_subtask(parent_task_id, subtask_data)
        subtask = self._convert_to_task(response.get('data', {}))
        return self.prepare_response(subtask, "AsanaTaskDetail")

    def get_workspaces(self, limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_workspaces(
            limit=limit,
            offset=offset
        )
        
        workspaces = [self._convert_to_workspace(workspace) for workspace in response.get('data', [])]
        
        workspace_list = WorkspaceList(
            items=workspaces,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(workspace_list, "AsanaWorkspaceList")

    def get_workspace(self, workspace_id: str) -> ApiResponse:
        response = self.client.get_workspace(workspace_id)
        workspace = self._convert_to_workspace(response.get('data', {}))
        return self.prepare_response(workspace, "AsanaWorkspaceDetail")

    def get_projects(self, workspace_id: Optional[str] = None, team_id: Optional[str] = None, 
                    archived: Optional[bool] = None, limit: int = 20, 
                    offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_projects(
            workspace_id=workspace_id,
            team_id=team_id,
            archived=archived,
            limit=limit,
            offset=offset
        )
        projects = [self._convert_to_project(p) for p in response.get('data', [])]
        return self.prepare_response(projects, "AsanaProjectList")

    def _convert_to_goal(self, goal_data: Dict[str, Any]) -> Goal:
        owner = None
        if goal_data.get('owner'):
            owner = User(
                gid=goal_data['owner'].get('gid'),
                name=goal_data['owner'].get('name'),
                email=goal_data['owner'].get('email', None)
            )
        
        # Extract workspace if present
        workspace = None
        if goal_data.get('workspace'):
            workspace = Workspace(
                gid=goal_data['workspace'].get('gid'),
                name=goal_data['workspace'].get('name')
            )
        
        # Extract time period if present and has required fields
        time_period = None
        if goal_data.get('time_period') and goal_data['time_period'].get('gid') and goal_data['time_period'].get('name'):
            time_period = TimePeriod(
                gid=goal_data['time_period'].get('gid'),
                name=goal_data['time_period'].get('name'),
                start_on=goal_data['time_period'].get('start_on'),
                end_on=goal_data['time_period'].get('end_on')
            )
        
        # Extract metric if present and has required fields
        metric = None
        if goal_data.get('metric') and goal_data['metric'].get('gid') and goal_data['metric'].get('name'):
            metric = GoalMetric(
                gid=goal_data['metric'].get('gid'),
                name=goal_data['metric'].get('name'),
                progress_value=goal_data['metric'].get('progress_value'),
                target_number_value=goal_data['metric'].get('target_number_value'),
                current_number_value=goal_data['metric'].get('current_number_value'),
                unit=goal_data['metric'].get('unit'),
                precision=goal_data['metric'].get('precision')
            )
        
        # Create Goal object
        return Goal(
            gid=goal_data.get('gid'),
            name=goal_data.get('name'),
            due_on=goal_data.get('due_on'),
            notes=goal_data.get('notes'),
            status=goal_data.get('status'),
            owner=owner,
            workspace=workspace,
            time_period=time_period,
            metric=metric,
            is_workspace_level=goal_data.get('is_workspace_level', False),
            liked=goal_data.get('liked', False)
        )

    def _convert_to_goal_metric(self, metric_data: Dict[str, Any]) -> GoalMetric:
        """Convert Asana API goal metric data to GoalMetric model."""
        return GoalMetric(
            gid=metric_data.get('gid'),
            name=metric_data.get('name'),
            progress_value=metric_data.get('progress_value'),
            target_number_value=metric_data.get('target_number_value'),
            current_number_value=metric_data.get('current_number_value'),
            unit=metric_data.get('unit'),
            precision=metric_data.get('precision')
        )

    def get_goals(self, workspace_id: str, time_period_id: Optional[str] = None, 
                 owner_id: Optional[str] = None, is_workspace_level: Optional[bool] = None,
                 limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        """Get goals with optional filtering."""
        response = self.client.get_goals(
            workspace_id=workspace_id,
            time_period_id=time_period_id,
            owner_id=owner_id,
            is_workspace_level=is_workspace_level,
            limit=limit,
            offset=offset
        )
        
        goals = [self._convert_to_goal(goal) for goal in response.get('data', [])]
        
        goal_list = GoalList(
            items=goals,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(goal_list, "AsanaGoalList")

    def get_goal(self, goal_id: str) -> ApiResponse:
        """Get a specific goal by ID."""
        response = self.client.get_goal(goal_id)
        goal = self._convert_to_goal(response.get('data', {}))
        return self.prepare_response(goal, "AsanaGoalDetail")

    def create_goal(self, goal_data: Dict[str, Any]) -> ApiResponse:
        """Create a new goal."""
        response = self.client.create_goal(goal_data)
        goal = self._convert_to_goal(response.get('data', {}))
        return self.prepare_response(goal, "AsanaGoalDetail")

    def update_goal(self, goal_id: str, goal_update: Dict[str, Any]) -> ApiResponse:
        """Update an existing goal."""
        response = self.client.update_goal(goal_id, goal_update)
        goal = self._convert_to_goal(response.get('data', {}))
        return self.prepare_response(goal, "AsanaGoalDetail")

    def create_goal_metric(self, goal_id: str, metric_data: Dict[str, Any]) -> ApiResponse:
        """Create a metric for a goal."""
        response = self.client.create_goal_metric(goal_id, metric_data)
        metric = self._convert_to_goal_metric(response.get('data', {}))
        return self.prepare_response(metric, None)

    def update_goal_metric(self, goal_metric_id: str, metric_update: Dict[str, Any]) -> ApiResponse:
        """Update a goal metric."""
        response = self.client.update_goal_metric(goal_metric_id, metric_update)
        metric = self._convert_to_goal_metric(response.get('data', {}))
        return self.prepare_response(metric, None)

    def get_users(self, workspace_id: Optional[str] = None, team_id: Optional[str] = None,
                 limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_users(
            workspace_id=workspace_id,
            team_id=team_id,
            limit=limit,
            offset=offset
        )
        
        users = [self._convert_to_user(user) for user in response.get('data', [])]
        
        user_list = UserList(
            items=users,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(user_list, "AsanaUserList")

    def get_user(self, user_id: str) -> ApiResponse:
        response = self.client.get_user(user_id)
        user = self._convert_to_user(response.get('data', {}))
        return self.prepare_response(user, "AsanaUserDetail")

    def _convert_to_user(self, user_data: Dict[str, Any]) -> User:
        return User(
            gid=user_data.get('gid'),
            name=user_data.get('name'),
            email=user_data.get('email', None)
        )

    def _convert_to_workspace(self, workspace_data: Dict[str, Any]) -> Workspace:
        return Workspace(
            gid=workspace_data.get('gid'),
            name=workspace_data.get('name')
        )

    def _convert_to_section(self, section_data: Dict[str, Any]) -> Section:
        project = None
        if isinstance(section_data.get('project'), dict):
            project = Project(
                gid=section_data['project'].get('gid'),
                name=section_data['project'].get('name')
            )
        
        return Section(
            gid=section_data.get('gid'),
            name=section_data.get('name'),
            project=project,
            created_at=section_data.get('created_at')
        )

    def get_sections(self, project_id: str) -> ApiResponse:
        response = self.client.get_sections(project_id)
        sections = [self._convert_to_section(section) for section in response.get('data', [])]
        
        section_list = SectionList(
            items=sections,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(section_list, "AsanaSectionList")

    def get_section(self, section_id: str) -> ApiResponse:
        response = self.client.get_section(section_id)
        section = self._convert_to_section(response.get('data', {}))
        return self.prepare_response(section, "AsanaSectionDetail")

    def get_section_tasks(self, section_id: str, limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_section_tasks(section_id, limit, offset)
        tasks = [self._convert_to_task(task) for task in response.get('data', [])]
        
        task_list = TaskList(
            items=tasks,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(task_list, "AsanaTaskList")

    def _convert_to_project(self, project_data: Dict[str, Any]) -> Project:
        owner = None
        if isinstance(project_data.get('owner'), dict):
            owner = User(
                gid=project_data['owner'].get('gid'),
                name=project_data['owner'].get('name'),
                email=project_data['owner'].get('email')
            )

        team = None
        if isinstance(project_data.get('team'), dict):
            team = Team(
                gid=project_data['team'].get('gid'),
                name=project_data['team'].get('name'),
                description=project_data['team'].get('description')
            )

        workspace = None
        if isinstance(project_data.get('workspace'), dict):
            workspace = Workspace(
                gid=project_data['workspace'].get('gid'),
                name=project_data['workspace'].get('name')
            )

        return Project(
            gid=project_data.get('gid'),
            name=project_data.get('name'),
            notes=project_data.get('notes'),
            archived=project_data.get('archived', False),
            color=project_data.get('color'),
            created_at=project_data.get('created_at'),
            modified_at=project_data.get('modified_at'),
            due_date=project_data.get('due_date'),
            owner=owner,
            team=team,
            workspace=workspace
        )

    def get_project(self, project_id: str) -> ApiResponse:
        response = self.client.get_project(project_id)
        project = self._convert_to_project(response.get('data', {}))
        return self.prepare_response(project, "AsanaProjectDetail")

    def _convert_to_tag(self, tag_data: Dict[str, Any]) -> Tag:
        workspace = None
        if isinstance(tag_data.get('workspace'), dict):
            workspace = Workspace(
                gid=tag_data['workspace'].get('gid'),
                name=tag_data['workspace'].get('name')
            )
        
        return Tag(
            gid=tag_data.get('gid'),
            name=tag_data.get('name'),
            color=tag_data.get('color'),
            workspace=workspace
        )

    def get_tags(self, workspace_id: Optional[str] = None, limit: int = 20, 
                 offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_tags(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset
        )
        tags = [self._convert_to_tag(tag) for tag in response.get('data', [])]
        return self.prepare_response(tags, "AsanaTagList")

    def get_tag(self, tag_id: str) -> ApiResponse:
        response = self.client.get_tag(tag_id)
        tag = self._convert_to_tag(response.get('data', {}))
        return self.prepare_response(tag, "AsanaTagDetail")

    def _convert_to_team(self, team_data: Dict[str, Any]) -> Team:
        return Team(
            gid=team_data.get('gid'),
            name=team_data.get('name'),
            description=team_data.get('description')
        )

    def get_teams(self, workspace_id: str, limit: int = 20, 
                  offset: Optional[str] = None) -> ApiResponse:
        response = self.client.get_teams(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset
        )
        teams = [self._convert_to_team(team) for team in response.get('data', [])]
        return self.prepare_response(teams, "AsanaTeamList")

    def get_team(self, team_id: str) -> ApiResponse:
        response = self.client.get_team(team_id)
        team = self._convert_to_team(response.get('data', {}))
        return self.prepare_response(team, "AsanaTeamDetail")

    def get_time_periods(self, workspace_id: str, limit: int = 20, offset: Optional[str] = None) -> ApiResponse:
        try:
            response = self.client.get_time_periods(
                workspace_id=workspace_id,
                limit=limit,
                offset=offset
            )
        except Exception:
            response = self.client.get_goal_time_periods(
                workspace_id=workspace_id,
                limit=limit,
                offset=offset
            )
        
        time_periods = []
        for period_data in response.get('data', []):
            if period_data.get('gid'):
                time_periods.append(TimePeriod(
                    gid=period_data['gid'],
                    name=period_data.get('name', ''),
                    start_on=period_data.get('start_on'),
                    end_on=period_data.get('end_on')
                ))
        
        period_list = TimePeriodList(
            items=time_periods,
            offset=response.get('next_page', {}).get('offset') if response.get('next_page') else None
        )
        
        return self.prepare_response(period_list, "AsanaTimePeriodList")
