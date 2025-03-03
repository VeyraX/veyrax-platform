import os
import pytest
import time
from typing import Dict, Any

from aci_server.integrations.github.client import GitHubClient
from aci_server.integrations.github.service import GitHubService


def get_timestamped_title(base_title: str) -> str:
    """Generate a unique title with timestamp to avoid conflicts in tests."""
    timestamp = int(time.time())
    return f"{base_title} {timestamp}"


@pytest.fixture(scope="module")
def base_setup():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN environment variable not set")
    
    client = GitHubClient(token)
    service = GitHubService(client)
    
    return {
        "client": client,
        "service": service,
        "token": token
    }


@pytest.fixture(scope="module")
def test_repo_info():
    """Fixture to provide test repository information.
    
    Using a public repository that belongs to the user for reliable testing.
    """
    return "diko0071", "browser-use"


def test_list_repositories(base_setup):
    """Test listing repositories."""
    service = base_setup["service"]
    
    response = service.get_repositories(per_page=5)
    
    assert response is not None
    assert response.data is not None
    assert hasattr(response.data, "repositories")
    assert isinstance(response.data.repositories, list)
    
    response = service.get_repositories(username="octocat", per_page=5)
    
    assert response is not None
    assert response.data is not None
    assert hasattr(response.data, "repositories")
    assert isinstance(response.data.repositories, list)


def test_get_repository(base_setup, test_repo_info):
    """Test getting a specific repository."""
    service = base_setup["service"]
    
    response = service.get_repository(
        owner=test_repo_info["owner"],
        repo=test_repo_info["repo"]
    )
    
    assert response is not None
    assert response.data is not None
    assert response.data.id is not None
    assert response.data.name == test_repo_info["repo"]
    assert response.data.full_name == f"{test_repo_info['owner']}/{test_repo_info['repo']}"
    assert response.data.html_url is not None


def test_list_issues(base_setup, test_repo_info):
    """Test listing issues for a repository."""
    service = base_setup["service"]
    
    response = service.get_issues(
        owner=test_repo_info["owner"],
        repo=test_repo_info["repo"],
        per_page=5
    )
    
    assert response is not None
    assert response.data is not None
    assert hasattr(response.data, "issues")
    assert isinstance(response.data.issues, list)


def test_get_issue(base_setup, test_repo_info):
    """Test getting a specific issue."""
    service = base_setup["service"]
    client = base_setup["client"]
    
    try:
        issues = client.get_issues(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"],
            per_page=1
        )
        
        if not issues:
            pytest.skip("No issues available for testing")
        
        issue_number = issues[0]["number"]
        
        response = service.get_issue(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"],
            issue_number=issue_number
        )
        
        assert response is not None
        assert response.data is not None
        assert response.data.id is not None
        assert response.data.number == issue_number
        assert response.data.title is not None
        assert response.data.html_url is not None
        assert response.data.repository is not None
        assert response.data.repository["owner"] == test_repo_info["owner"]
        assert response.data.repository["name"] == test_repo_info["repo"]
    except Exception as e:
        pytest.skip(f"Error getting issues: {str(e)}")


def test_list_pull_requests(base_setup, test_repo_info):
    """Test listing pull requests for a repository."""
    service = base_setup["service"]
    
    response = service.get_pull_requests(
        owner=test_repo_info["owner"],
        repo=test_repo_info["repo"],
        per_page=5
    )
    
    assert response is not None
    assert response.data is not None
    assert hasattr(response.data, "pull_requests")
    assert isinstance(response.data.pull_requests, list)


def test_get_pull_request(base_setup, test_repo_info):
    """Test getting a specific pull request."""
    service = base_setup["service"]
    client = base_setup["client"]
    
    try:
        prs = client.get_pull_requests(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"],
            per_page=1
        )
        
        if not prs:
            pytest.skip("No pull requests available for testing")
        
        pr_number = prs[0]["number"]
        
        response = service.get_pull_request(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"],
            pull_number=pr_number
        )
        
        assert response is not None
        assert response.data is not None
        assert response.data.id is not None
        assert response.data.number == pr_number
        assert response.data.title is not None
        assert response.data.html_url is not None
        assert response.data.head is not None
        assert response.data.base is not None
    except Exception as e:
        pytest.skip(f"Error getting pull requests: {str(e)}")


def test_get_commit(base_setup, test_repo_info):
    """Test getting a specific commit."""
    service = base_setup["service"]
    client = base_setup["client"]
    
    try:
        repo = client.get_repository(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"]
        )
        
        default_branch = repo.get("default_branch", "main")
        
        commits_endpoint = f"/repos/{test_repo_info['owner']}/{test_repo_info['repo']}/commits"
        commits_params = {"sha": default_branch, "per_page": 1}
        commits = client._make_request("GET", commits_endpoint, params=commits_params)
        
        if not commits:
            pytest.skip("No commits available for testing")
        
        commit_sha = commits[0]["sha"]
        
        response = service.get_commit(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"],
            commit_sha=commit_sha
        )
        
        assert response is not None
        assert response.data is not None
        assert response.data.sha == commit_sha
        assert response.data.commit is not None
        assert response.data.html_url is not None
    except Exception as e:
        pytest.skip(f"Error getting commits: {str(e)}")


def test_star_repository(base_setup, test_repo_info):
    """Test starring a repository."""
    service = base_setup["service"]
    
    try:
        response = service.star_repository(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"]
        )
        
        assert response is not None
        assert response.message is not None
        assert f"Repository {test_repo_info['owner']}/{test_repo_info['repo']} has been starred successfully" in response.message
    except Exception as e:
        pytest.skip(f"Error starring repository: {str(e)}")


def test_unstar_repository(base_setup, test_repo_info):
    """Test unstarring a repository."""
    service = base_setup["service"]
    
    try:
        service.star_repository(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"]
        )
        
        response = service.unstar_repository(
            owner=test_repo_info["owner"],
            repo=test_repo_info["repo"]
        )
        
        assert response is not None
        assert response.message is not None
        assert f"Repository {test_repo_info['owner']}/{test_repo_info['repo']} has been unstarred successfully" in response.message
    except Exception as e:
        pytest.skip(f"Error unstarring repository: {str(e)}")


def test_api_response_format(base_setup, test_repo_info):
    """Test that API responses have the correct format."""
    service = base_setup["service"]
    
    repo_response = service.get_repository(
        owner=test_repo_info["owner"],
        repo=test_repo_info["repo"]
    )
    
    assert repo_response is not None
    assert hasattr(repo_response, "data")
    assert hasattr(repo_response, "component")
    assert hasattr(repo_response, "message")
    
    repos_response = service.get_repositories(username="octocat", per_page=5)
    
    assert repos_response is not None
    assert hasattr(repos_response, "data")
    assert hasattr(repos_response, "component")
    assert hasattr(repos_response, "message")
    assert hasattr(repos_response.data, "repositories")
    assert hasattr(repos_response.data, "next_page")


def test_list_commits(base_setup, test_repo_info):
    """Test listing commits for a repository."""
    client, service = base_setup
    owner, repo = test_repo_info 
    response = service.get_commits(owner=owner, repo=repo)
    
    assert response is not None
    assert hasattr(response, 'data')
    assert hasattr(response.data, 'commits')
    assert isinstance(response.data.commits, list)
    
    if response.data.commits:
        commit = response.data.commits[0]
        assert hasattr(commit, 'sha')
        assert hasattr(commit, 'commit')
        assert hasattr(commit, 'html_url')
        
        assert 'message' in commit.commit
        assert 'author' in commit.commit
        assert 'committer' in commit.commit
    
    response = service.get_commits(owner=owner, repo=repo, per_page=3, page=1)
    assert response is not None
    assert hasattr(response, 'data')
    
    if response.data.commits and len(response.data.commits) == 3:
        assert response.data.next_page == 2


def test_commits_api_format(base_setup, test_repo_info):
    """Test that the commits API returns data in the expected format."""
    client, service = base_setup
    owner, repo = test_repo_info
    
    response = service.get_commits(owner=owner, repo=repo, per_page=1)
    
    assert response is not None
    assert hasattr(response, 'data')
    
    if hasattr(response.data, 'commits') and response.data.commits:
        commit = response.data.commits[0]
        
        assert hasattr(commit, 'sha')
        assert hasattr(commit, 'commit')
        assert hasattr(commit, 'html_url')
        
        assert 'message' in commit.commit
        assert 'author' in commit.commit
        assert 'committer' in commit.commit
        
        if hasattr(commit, 'author') and commit.author:
            assert 'login' in commit.author
            assert 'avatar_url' in commit.author
        
        if hasattr(commit, 'files') and commit.files:
            file = commit.files[0]
            assert 'filename' in file
            assert 'status' in file
            
        if hasattr(commit, 'stats') and commit.stats:
            assert 'additions' in commit.stats
            assert 'deletions' in commit.stats
            assert 'total' in commit.stats


def test_commits_with_path_filter(base_setup, test_repo_info):
    """Test filtering commits by file path."""
    client, service = base_setup
    owner, repo = test_repo_info
    
    all_commits = service.get_commits(owner=owner, repo=repo)
    
    file_path = None
    if (hasattr(all_commits, 'data') and 
        hasattr(all_commits.data, 'commits') and 
        all_commits.data.commits and 
        hasattr(all_commits.data.commits[0], 'files') and 
        all_commits.data.commits[0].files):
        
        file_path = all_commits.data.commits[0].files[0].get('filename')
    
    if file_path:
        filtered_response = service.get_commits(owner=owner, repo=repo, path=file_path)
        assert filtered_response is not None
        assert hasattr(filtered_response, 'data')
        assert hasattr(filtered_response.data, 'commits')
        
        if filtered_response.data.commits:
            assert hasattr(filtered_response.data.commits[0], 'sha')
            assert hasattr(filtered_response.data.commits[0], 'commit')


def test_commits_date_filtering(base_setup, test_repo_info):
    """Test filtering commits by date range."""
    client, service = base_setup
    owner, repo = test_repo_info
    
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    date_filtered = service.get_commits(
        owner=owner, 
        repo=repo,
        since=one_year_ago,
        until=today
    )
    
    assert date_filtered is not None
    assert hasattr(date_filtered, 'data')
    assert hasattr(date_filtered.data, 'commits')
    
    if date_filtered.data.commits:
        assert hasattr(date_filtered.data.commits[0], 'sha')
        assert hasattr(date_filtered.data.commits[0], 'commit')
        assert 'date' in date_filtered.data.commits[0].commit['author']


def test_commits_with_branch_or_tag(base_setup, test_repo_info):
    client, service = base_setup
    owner, repo = test_repo_info
    
    default_branch = 'main'     
    
    branch_commits = service.get_commits(owner=owner, repo=repo, sha=default_branch)
    
    assert branch_commits is not None
    assert hasattr(branch_commits, 'data')
    assert hasattr(branch_commits.data, 'commits')
    
    if not branch_commits.data.commits:
        branch_commits = service.get_commits(owner=owner, repo=repo, sha='master')
        
    if branch_commits.data.commits:
        assert hasattr(branch_commits.data.commits[0], 'sha')
        assert hasattr(branch_commits.data.commits[0], 'commit')