import requests
from typing import Optional

class LinearClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def execute_query(self, query: str, variables: dict = None) -> dict:
        response = requests.post(
            self.base_url,
            json={"query": query, "variables": variables or {}},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def list_issues(self, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query Issues($cursor: String, $first: Int!) {
            issues(
                first: $first, 
                after: $cursor,
                orderBy: createdAt
            ) {
                nodes {
                    id 
                    title 
                    description 
                    identifier
                    state { id name }
                    priority
                    assignee { id name email }
                    creator { id name email }
                    createdAt 
                    updatedAt
                    labels { nodes { name } }
                    project { id }
                    team { id key }
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"cursor": cursor, "first": max_results})

    def search_issues(self, search_term: str, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query SearchIssues($search: String!, $cursor: String, $first: Int!) {
            issueSearch(query: $search, first: $first, after: $cursor) {
                nodes {
                    id 
                    title 
                    description
                    identifier
                    state { id name }
                    priority
                    assignee { id name email }
                    creator { id name email }
                    createdAt 
                    updatedAt
                    labels { nodes { name } }
                    project { id }
                    team { id key }
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"search": search_term, "cursor": cursor, "first": max_results})

    def filter_issues(self, graphql_filters: dict, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query FilterIssues($filter: IssueFilter, $cursor: String, $first: Int!) {
            issues(filter: $filter, first: $first, after: $cursor) {
                nodes {
                    id 
                    title 
                    description
                    identifier
                    state { id name }
                    priority
                    assignee { id name email }
                    creator { id name email }
                    createdAt 
                    updatedAt
                    labels { nodes { name } }
                    project { id }
                    team { id key }
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"filter": graphql_filters, "cursor": cursor, "first": max_results})

    def create_issue(self, input_data: dict) -> dict:
        query = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                issue {
                    id 
                    title 
                    description
                    identifier
                    state { id name }
                    priority
                    assignee { id name email }
                    creator { id name email }
                    createdAt 
                    updatedAt
                    labels { nodes { name } }
                    project { id }
                    team { id key }
                }
            }
        }
        """
        return self.execute_query(query, {"input": input_data})

    def update_issue(self, issue_id: str, input_data: dict) -> dict:
        query = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                issue {
                    id 
                    title 
                    description
                    identifier
                    state { id name }
                    priority
                    assignee { id name email }
                    creator { id name email }
                    createdAt 
                    updatedAt
                    labels { nodes { name } }
                    project { id }
                    team { id key }
                }
            }
        }
        """
        
        return self.execute_query(query, {"id": issue_id, "input": input_data})

    def create_comment(self, issue_id: str, body: str) -> dict:
        query = """
        mutation CreateComment($input: CommentCreateInput!) {
            commentCreate(input: $input) {
                success
                comment {
                    id
                    body
                    user { id name email }
                    createdAt
                }
            }
        }
        """
        return self.execute_query(query, {
            "input": {
                "issueId": issue_id,
                "body": body
            }
        })

    def list_projects(self, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query Projects($cursor: String, $first: Int!) {
            projects(first: $first, after: $cursor) {
                nodes {
                    id name description
                    state
                    createdAt updatedAt
                    lead { id name email }
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"cursor": cursor, "first": max_results})

    def get_project(self, project_id: str) -> dict:
        query = """
        query Project($id: String!) {
            project(id: $id) {
                id name description
                state
                createdAt updatedAt
                lead { id name email }
                issues {
                    nodes {
                        id title state { name }
                    }
                }
            }
        }
        """
        return self.execute_query(query, {"id": project_id})

    def list_users(self, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query Users($cursor: String, $first: Int!) {
            users(first: $first, after: $cursor) {
                nodes {
                    id
                    name
                    email
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"cursor": cursor, "first": max_results})

    def list_teams(self, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query Teams($cursor: String, $first: Int!) {
            teams(first: $first, after: $cursor) {
                nodes {
                    id
                    name
                    key
                    description
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"cursor": cursor, "first": max_results})

    def get_team(self, team_id: str) -> dict:
        query = """
        query Team($id: String!) {
            team(id: $id) {
                id
                name
                key
                description
            }
        }
        """
        return self.execute_query(query, {"id": team_id})

    def list_workflow_states(self, cursor: Optional[str] = None, max_results: int = 50) -> dict:
        query = """
        query WorkflowStates($cursor: String, $first: Int!) {
            workflowStates(first: $first, after: $cursor) {
                nodes {
                    id
                    name
                    color
                    type
                    position
                    team { id key name }
                }
                pageInfo { hasNextPage endCursor }
            }
        }
        """
        return self.execute_query(query, {"cursor": cursor, "first": max_results})

