from typing import Optional, Dict, Any, Union, List

import os
from .client import SentryClient
from .schema import (
    OrganizationList, Organization, TeamList, Team, 
    ProjectList, Project, IssueList, Issue, EventList, Event,
    ReleaseList, Release, AlertRuleList, AlertRule,
    UserFeedbackList, UserFeedback, ServiceHookList, ServiceHook,
    ApiResponse, Dsn, DsnResponse
)

from ..common.component_handler import load_components, prepare_components_auto

class SentryService:
    def __init__(self, client: SentryClient):
        self.client = client
        self.components_data = self._load_components()

    def _load_components(self) -> Dict[str, Any]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return load_components(current_dir)

    def prepare_response(self, data: Any, component_name: str = None) -> ApiResponse:
        tool_name = "sentry"
        components = prepare_components_auto(data, component_name, self.components_data, tool_name)
        return ApiResponse(data=data, component=components)

    # Organization and Team Management
    def list_organizations(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_organizations()
        organizations = [
            Organization(
                id=org["id"],
                slug=org["slug"],
                name=org["name"],
                dateCreated=org["dateCreated"],
                status=org.get("status"),
                avatar=org.get("avatar")
            )
            for org in response
        ]
        org_list = OrganizationList(organizations=organizations)
        return self.prepare_response(org_list, "SentryOrganizationList")

    def list_teams(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_teams()
        teams = [
            Team(
                id=team["id"],
                slug=team["slug"],
                name=team["name"],
                dateCreated=team["dateCreated"],
                isMember=team.get("isMember", False),
                teamRole=team.get("teamRole"),
                access=team.get("access", []),
                memberCount=team.get("memberCount", 0),
                avatar=team.get("avatar")
            )
            for team in response
        ]
        team_list = TeamList(teams=teams)
        return self.prepare_response(team_list, "SentryTeamList")

    def create_team(self, name: Optional[str] = None, slug: Optional[str] = None) -> ApiResponse:
        data = {}
        if name:
            data["name"] = name
        if slug:
            data["slug"] = slug
        
        response = self.client.create_team(data)
        team = Team(
            id=response["id"],
            slug=response["slug"],
            name=response["name"],
            dateCreated=response["dateCreated"],
            isMember=response.get("isMember", False),
            teamRole=response.get("teamRole"),
            access=response.get("access", []),
            memberCount=response.get("memberCount", 0),
            avatar=response.get("avatar")
        )
        return self.prepare_response(team, "SentryTeamCard")

    def list_user_teams(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_user_teams()
        teams = [
            Team(
                id=team["id"],
                slug=team["slug"],
                name=team["name"],
                dateCreated=team["dateCreated"],
                isMember=team.get("isMember", False),
                teamRole=team.get("teamRole"),
                access=team.get("access", []),
                memberCount=team.get("memberCount", 0),
                avatar=team.get("avatar")
            )
            for team in response
        ]
        team_list = TeamList(teams=teams)
        return self.prepare_response(team_list, "SentryTeamList")

    # Project Management
    def list_projects(self, cursor: Optional[str] = None) -> ApiResponse:
        response = self.client.list_projects()
        projects = [
            Project(
                id=project["id"],
                slug=project["slug"],
                name=project["name"],
                platform=project.get("platform"),
                dateCreated=project["dateCreated"],
                isBookmarked=project.get("isBookmarked", False),
                isMember=project.get("isMember", False),
                features=project.get("features", []),
                firstEvent=project.get("firstEvent"),
                access=project.get("access", []),
                hasAccess=project.get("hasAccess", True),
                status=project.get("status", "active"),
                avatar=project.get("avatar"),
                color=project.get("color")
            )
            for project in response
        ]
        project_list = ProjectList(projects=projects)
        return self.prepare_response(project_list, "SentryProjectList")

    def create_project(self, team_slug: str, name: str, slug: Optional[str] = None, platform: Optional[str] = None) -> ApiResponse:
        data = {"name": name}
        if slug:
            data["slug"] = slug
        if platform:
            data["platform"] = platform
        
        response = self.client.create_project(team_slug, data)
        project = Project(
            id=response["id"],
            slug=response["slug"],
            name=response["name"],
            platform=response.get("platform"),
            dateCreated=response["dateCreated"],
            isBookmarked=response.get("isBookmarked", False),
            isMember=response.get("isMember", False),
            features=response.get("features", []),
            firstEvent=response.get("firstEvent"),
            access=response.get("access", []),
            hasAccess=response.get("hasAccess", True),
            status=response.get("status", "active"),
            avatar=response.get("avatar"),
            color=response.get("color")
        )
        return self.prepare_response(project, "SentryProjectCard")

    # Issues and Events Management
    def list_issues(self, project_slug: str, query: Optional[str] = None, status: Optional[str] = None, cursor: Optional[str] = None) -> ApiResponse:
        query_params = {}
        if query:
            query_params["query"] = query
        if status:
            query_params["status"] = status
        if cursor:
            query_params["cursor"] = cursor
        
        response = self.client.list_issues(project_slug, query_params)
        issues = []
        for issue_data in response:
            project_data = issue_data["project"]
            project = Project(
                id=project_data["id"],
                slug=project_data["slug"],
                name=project_data["name"],
                platform=project_data.get("platform"),
                dateCreated=project_data.get("dateCreated", ""),
                hasAccess=project_data.get("hasAccess", True),
                status=project_data.get("status", "active")
            )
            
            issue = Issue(
                id=issue_data["id"],
                shortId=issue_data["shortId"],
                title=issue_data["title"],
                culprit=issue_data["culprit"],
                level=issue_data["level"],
                status=issue_data["status"],
                statusDetails=issue_data.get("statusDetails"),
                isSubscribed=issue_data.get("isSubscribed", False),
                isBookmarked=issue_data.get("isBookmarked", False),
                project=project,
                type=issue_data.get("type", "error"),
                metadata=issue_data.get("metadata", {}),
                numComments=issue_data.get("numComments", 0),
                assignedTo=issue_data.get("assignedTo"),
                count=issue_data.get("count", "0"),
                userCount=issue_data.get("userCount", 0),
                firstSeen=issue_data["firstSeen"],
                lastSeen=issue_data["lastSeen"]
            )
            issues.append(issue)
        
        cursor = response.get("nextCursor") if isinstance(response, dict) else None
        issue_list = IssueList(issues=issues, cursor=cursor)
        return self.prepare_response(issue_list, "SentryIssueList")

    def get_issue_details(self, issue_id: str) -> ApiResponse:
        response = self.client.get_issue_details(issue_id)
        
        project_data = response["project"]
        project = Project(
            id=project_data["id"],
            slug=project_data["slug"],
            name=project_data["name"],
            platform=project_data.get("platform"),
            dateCreated=project_data.get("dateCreated", ""),
            hasAccess=project_data.get("hasAccess", True),
            status=project_data.get("status", "active")
        )
        
        issue = Issue(
            id=response["id"],
            shortId=response["shortId"],
            title=response["title"],
            culprit=response["culprit"],
            level=response["level"],
            status=response["status"],
            statusDetails=response.get("statusDetails"),
            isSubscribed=response.get("isSubscribed", False),
            isBookmarked=response.get("isBookmarked", False),
            project=project,
            type=response.get("type", "error"),
            metadata=response.get("metadata", {}),
            numComments=response.get("numComments", 0),
            assignedTo=response.get("assignedTo"),
            count=response.get("count", "0"),
            userCount=response.get("userCount", 0),
            firstSeen=response["firstSeen"],
            lastSeen=response["lastSeen"]
        )
        return self.prepare_response(issue, "SentryIssueDetails")

    def list_issue_events(self, issue_id: str, cursor: Optional[str] = None) -> ApiResponse:
        query_params = {}
        if cursor:
            query_params["cursor"] = cursor
        
        response = self.client.list_issue_events(issue_id, query_params)
        events = []
        for event_data in response:
            event = Event(
                id=event_data["id"],
                eventID=event_data["eventID"],
                groupID=event_data["groupID"],
                title=event_data.get("title", ""),
                message=event_data.get("message"),
                dateCreated=event_data["dateCreated"],
                user=event_data.get("user"),
                tags=event_data.get("tags", []),
                entries=event_data.get("entries", []),
                metadata=event_data.get("metadata", {})
            )
            events.append(event)
        
        cursor = response.get("nextCursor") if isinstance(response, dict) else None
        event_list = EventList(events=events, cursor=cursor)
        return self.prepare_response(event_list, "SentryEventList")

    # Releases Management
    def list_releases(self, query: Optional[str] = None, cursor: Optional[str] = None) -> ApiResponse:
        query_params = {}
        if query:
            query_params["query"] = query
        if cursor:
            query_params["cursor"] = cursor
        
        response = self.client.list_releases(query_params)
        releases = []
        for release_data in response:
            release = Release(
                id=str(release_data["id"]),
                version=release_data["version"],
                dateCreated=release_data["dateCreated"],
                dateReleased=release_data.get("dateReleased"),
                projects=release_data.get("projects", []),
                url=release_data["url"],
                newGroups=release_data.get("newGroups", 0),
                commits=release_data.get("commits")
            )
            releases.append(release)
        
        cursor = response.get("nextCursor") if isinstance(response, dict) else None
        release_list = ReleaseList(releases=releases, cursor=cursor)
        return self.prepare_response(release_list, "SentryReleaseList")

    def create_release(self, version: str, projects: List[str], ref: Optional[str] = None, 
                      url: Optional[str] = None, dateReleased: Optional[str] = None) -> ApiResponse:
        data = {
            "version": version,
            "projects": projects
        }
        if ref:
            data["ref"] = ref
        if url:
            data["url"] = url
        if dateReleased:
            data["dateReleased"] = dateReleased
        
        response = self.client.create_release(data)
        release = Release(
            id=str(response["id"]),
            version=response["version"],
            dateCreated=response["dateCreated"],
            dateReleased=response.get("dateReleased"),
            projects=response.get("projects", []),
            url=response["url"],
            newGroups=response.get("newGroups", 0),
            commits=response.get("commits")
        )
        return self.prepare_response(release, "SentryReleaseDetails")

    # Alert Rules Management
    def list_alert_rules(self, project_slug: str) -> ApiResponse:
        response = self.client.list_alert_rules(project_slug)
        rules = []
        for rule_data in response:
            rule = AlertRule(
                id=rule_data["id"],
                name=rule_data["name"],
                conditions=rule_data["conditions"],
                actions=rule_data["actions"],
                actionMatch=rule_data["actionMatch"],
                dateCreated=rule_data["dateCreated"],
                environment=rule_data.get("environment"),
                frequency=rule_data["frequency"],
                dateModified=rule_data.get("dateModified", "")
            )
            rules.append(rule)
        
        rule_list = AlertRuleList(rules=rules)
        return self.prepare_response(rule_list, "SentryAlertRuleList")

    def create_alert_rule(self, project_slug: str, name: str, conditions: List[Dict[str, Any]], 
                        actions: List[Dict[str, Any]], actionMatch: str = "all", 
                        frequency: int = 30, environment: Optional[str] = None) -> ApiResponse:
        data = {
            "name": name,
            "conditions": conditions,
            "actions": actions,
            "actionMatch": actionMatch,
            "frequency": frequency
        }
        if environment:
            data["environment"] = environment
        
        response = self.client.create_alert_rule(project_slug, data)
        rule = AlertRule(
            id=response["id"],
            name=response["name"],
            conditions=response["conditions"],
            actions=response["actions"],
            actionMatch=response["actionMatch"],
            dateCreated=response["dateCreated"],
            environment=response.get("environment"),
            frequency=response["frequency"],
            dateModified=response.get("dateModified", "")
        )
        return self.prepare_response(rule, "SentryAlertRuleDetails")

    # User Feedback Management
    def list_user_feedback(self, project_slug: str, cursor: Optional[str] = None) -> ApiResponse:
        query_params = {}
        if cursor:
            query_params["cursor"] = cursor
        
        response = self.client.list_user_feedback(project_slug, query_params)
        feedback_items = []
        for item_data in response:
            feedback = UserFeedback(
                id=item_data["id"],
                name=item_data["name"],
                email=item_data["email"],
                comments=item_data["comments"],
                dateCreated=item_data["dateCreated"],
                issueId=item_data.get("issue", {}).get("id", ""),
                eventId=item_data["eventID"],
                event=item_data.get("event")
            )
            feedback_items.append(feedback)
        
        cursor = response.get("nextCursor") if isinstance(response, dict) else None
        feedback_list = UserFeedbackList(feedback=feedback_items, cursor=cursor)
        return self.prepare_response(feedback_list, "SentryUserFeedbackList")

    # Service Hooks Management
    def list_service_hooks(self, project_slug: str) -> ApiResponse:
        response = self.client.list_service_hooks(project_slug)
        hooks = []
        for hook_data in response:
            hook = ServiceHook(
                id=hook_data["id"],
                url=hook_data["url"],
                events=hook_data["events"],
                dateCreated=hook_data["dateCreated"],
                status=hook_data.get("status", "active")
            )
            hooks.append(hook)
        
        hook_list = ServiceHookList(hooks=hooks)
        return self.prepare_response(hook_list, "SentryServiceHookList")

    def create_service_hook(self, project_slug: str, url: str, events: List[str]) -> ApiResponse:
        data = {
            "url": url,
            "events": events
        }
        
        response = self.client.create_service_hook(project_slug, data)
        hook = ServiceHook(
            id=response["id"],
            url=response["url"],
            events=response["events"],
            dateCreated=response["dateCreated"],
            status=response.get("status", "active")
        )
        return self.prepare_response(hook, "SentryServiceHookDetails")

    def get_project_dsn(self, project_slug: str) -> ApiResponse:
        dsn_data = self.client.get_project_dsn(project_slug)
        if not dsn_data:
            raise ValueError("No DSN found for project")
        
        # Get first key's DSN information
        key_data = dsn_data[0]
        dsn = Dsn(
            public=key_data["dsn"]["public"],
            secret=key_data["dsn"].get("secret"),
            csp=key_data["dsn"].get("csp"),
            minidump=key_data["dsn"].get("minidump"),
            security=key_data["dsn"].get("security"),
            cdn=key_data["dsn"].get("cdn"),
            curl=key_data["dsn"].get("curl"),
            meta=key_data["dsn"].get("meta")
        )
        
        return self.prepare_response(
            DsnResponse(
                project_slug=project_slug,
                dsn=dsn,
                id=key_data["id"]
            ),
            "SentryDsnDisplay"
        )

    

