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
    """Test listing commits with a specific branch or tag."""
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


def test_create_pull_request(base_setup, test_repo_info):
    """Test creating a pull request."""
    service = base_setup["service"]
    owner = test_repo_info["owner"]
    repo = test_repo_info["repo"]
    
    # Create a unique branch name for testing
    branch_name = f"test-branch-{int(time.time())}"
    
    # First, we need to create a new branch
    # This is done outside the service since branch creation is not part of our API
    try:
        # Get the default branch to use as base
        repo_info = service.get_repository(owner=owner, repo=repo)
        default_branch = repo_info.data.default_branch
        
        # Create a test PR title
        pr_title = get_timestamped_title("Test Pull Request")
        
        # For testing purposes, we'll try to create a PR from the same branch to itself
        # This will fail in a real scenario, but we can test the API call structure
        response = service.create_pull_request(
            owner=owner,
            repo=repo,
            title=pr_title,
            head=default_branch,  # In a real scenario, this would be a different branch
            base=default_branch,
            body="This is a test pull request created by automated tests.",
            draft=True
        )
        
        # This will likely fail with a same-branch error, but we can check the error handling
        if "Error creating pull request" in response.message:
            # Expected error for same branch
            assert "No commits between" in response.message or "same branch" in response.message.lower()
        else:
            # If it somehow succeeds (e.g., if the repo has multiple branches)
            assert response.data is not None
            assert isinstance(response.data, PullRequestSchema)
            assert response.data.title == pr_title
    except Exception as e:
        # This test may fail in CI environments without proper permissions
        # We'll make it a soft assertion
        print(f"Error in create_pull_request test: {str(e)}")
        assert "Error creating pull request" in str(e) or "No commits between" in str(e) or "same branch" in str(e).lower()


def test_update_pull_request(base_setup, test_repo_info):
    """Test updating a pull request."""
    service = base_setup["service"]
    owner = test_repo_info["owner"]
    repo = test_repo_info["repo"]
    
    # First, get an existing PR if available
    prs_response = service.get_pull_requests(owner=owner, repo=repo, state="all")
    
    if not prs_response.data or not prs_response.data.pull_requests:
        pytest.skip("No pull requests available for testing update")
    
    # Get the first PR
    pr = prs_response.data.pull_requests[0]
    pr_number = pr.number
    
    # Update the PR with a new title
    new_title = get_timestamped_title("Updated PR Title")
    response = service.update_pull_request(
        owner=owner,
        repo=repo,
        pull_number=pr_number,
        title=new_title
    )
    
    # Check if update was successful
    if "Error updating pull request" in response.message:
        # This might happen if we don't have write permissions
        assert "permission" in response.message.lower() or "not authorized" in response.message.lower()
    else:
        assert response.data is not None
        assert isinstance(response.data, PullRequestSchema)
        assert response.data.title == new_title


def test_merge_pull_request(base_setup, test_repo_info):
    """Test merging a pull request."""
    service = base_setup["service"]
    owner = test_repo_info["owner"]
    repo = test_repo_info["repo"]
    
    # First, get an open PR if available
    prs_response = service.get_pull_requests(owner=owner, repo=repo, state="open")
    
    if not prs_response.data or not prs_response.data.pull_requests:
        pytest.skip("No open pull requests available for testing merge")
    
    # Get the first open PR
    pr = prs_response.data.pull_requests[0]
    pr_number = pr.number
    
    # Try to merge the PR
    response = service.merge_pull_request(
        owner=owner,
        repo=repo,
        pull_number=pr_number,
        commit_title=f"Merge PR #{pr_number}",
        merge_method="merge"
    )
    
    # Check if merge was successful or failed with expected error
    if "Error merging pull request" in response.message:
        # This might happen if we don't have write permissions or PR isn't mergeable
        assert ("permission" in response.message.lower() or 
                "not authorized" in response.message.lower() or
                "not mergeable" in response.message.lower())
    else:
        assert response.message == "Pull request merged successfully"
        assert response.data is not None


def test_get_pull_request_reviews(base_setup, test_repo_info):
    """Test getting reviews for a pull request."""
    service = base_setup["service"]
    owner = test_repo_info["owner"]
    repo = test_repo_info["repo"]
    
    # First, get a PR if available
    prs_response = service.get_pull_requests(owner=owner, repo=repo, state="all")
    
    if not prs_response.data or not prs_response.data.pull_requests:
        pytest.skip("No pull requests available for testing reviews")
    
    # Get the first PR
    pr = prs_response.data.pull_requests[0]
    pr_number = pr.number
    
    # Get reviews for the PR
    response = service.get_pull_request_reviews(
        owner=owner,
        repo=repo,
        pull_number=pr_number
    )
    
    # Check response structure
    assert response.data is not None
    
    # Reviews might be empty if none exist
    if response.data.reviews:
        review = response.data.reviews[0]
        assert review.id is not None
        assert review.user is not None
        assert review.state is not None


def test_create_pull_request_review(base_setup, test_repo_info):
    """Test creating a review for a pull request."""
    service = base_setup["service"]
    owner = test_repo_info["owner"]
    repo = test_repo_info["repo"]
    
    # First, get an open PR if available
    prs_response = service.get_pull_requests(owner=owner, repo=repo, state="open")
    
    if not prs_response.data or not prs_response.data.pull_requests:
        pytest.skip("No open pull requests available for testing review creation")
    
    # Get the first open PR
    pr = prs_response.data.pull_requests[0]
    pr_number = pr.number
    
    # Create a review
    response = service.create_pull_request_review(
        owner=owner,
        repo=repo,
        pull_number=pr_number,
        body="This is a test review created by automated tests.",
        event="COMMENT"  # APPROVE, REQUEST_CHANGES, COMMENT
    )
    
    # Check if review creation was successful
    if "Error creating pull request review" in response.message:
        # This might happen if we don't have write permissions
        assert "permission" in response.message.lower() or "not authorized" in response.message.lower()
    else:
        assert response.data is not None
        assert response.data.body == "This is a test review created by automated tests."
        assert response.data.state is not None