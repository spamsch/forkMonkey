"""
ForkMonkey GitHub Service

Handles all GitHub API interactions for the managed adoption flows.
"""

import os
import time
from typing import Optional, Dict, Any
from github import Github, GithubException


class GitHubService:
    """Service for GitHub API operations."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub service.
        
        Args:
            token: GitHub personal access token. If not provided, uses GITHUB_TOKEN env var.
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
        
        self.github = Github(self.token)
        self.source_repo = os.getenv('FORKMONKEY_SOURCE_REPO', 'roeiba/forkMonkey')
    
    def fork_repository(self, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fork the ForkMonkey repository to the authenticated user's account.
        
        Args:
            repo_name: Optional custom name for the forked repository.
            
        Returns:
            Dictionary with fork information.
        """
        try:
            source = self.github.get_repo(self.source_repo)
            
            # Fork to authenticated user's account
            fork = source.create_fork()
            
            # Wait for fork to be ready
            time.sleep(5)
            
            # Rename if custom name provided
            if repo_name and repo_name != fork.name:
                fork.edit(name=repo_name)
            
            return {
                'success': True,
                'repo_name': fork.name,
                'full_name': fork.full_name,
                'url': fork.html_url,
                'clone_url': fork.clone_url
            }
            
        except GithubException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def enable_github_actions(self, repo_full_name: str) -> Dict[str, Any]:
        """
        Enable GitHub Actions on a repository.
        
        Args:
            repo_full_name: Full repository name (owner/repo).
            
        Returns:
            Dictionary with operation result.
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            
            # Enable actions via the API
            # Note: This requires admin permissions
            repo._requester.requestJsonAndCheck(
                "PUT",
                f"/repos/{repo_full_name}/actions/permissions",
                input={"enabled": True, "allowed_actions": "all"}
            )
            
            return {'success': True}
            
        except GithubException as e:
            return {'success': False, 'error': str(e)}
    
    def enable_github_pages(self, repo_full_name: str) -> Dict[str, Any]:
        """
        Enable GitHub Pages with Actions deployment.
        
        Args:
            repo_full_name: Full repository name (owner/repo).
            
        Returns:
            Dictionary with operation result and pages URL.
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            
            # Create pages with workflow deployment
            try:
                repo._requester.requestJsonAndCheck(
                    "POST",
                    f"/repos/{repo_full_name}/pages",
                    input={"build_type": "workflow"}
                )
            except GithubException as e:
                if "already exists" not in str(e).lower():
                    raise
            
            owner = repo_full_name.split('/')[0]
            repo_name = repo_full_name.split('/')[1]
            pages_url = f"https://{owner}.github.io/{repo_name}/"
            
            return {
                'success': True,
                'pages_url': pages_url
            }
            
        except GithubException as e:
            return {'success': False, 'error': str(e)}
    
    def trigger_workflow(self, repo_full_name: str, workflow_file: str = 'on-create.yml') -> Dict[str, Any]:
        """
        Trigger a workflow dispatch event.
        
        Args:
            repo_full_name: Full repository name (owner/repo).
            workflow_file: Workflow file name.
            
        Returns:
            Dictionary with operation result.
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            workflow = repo.get_workflow(workflow_file)
            
            # Dispatch the workflow
            workflow.create_dispatch(ref='main')
            
            return {'success': True}
            
        except GithubException as e:
            return {'success': False, 'error': str(e)}
    
    def create_transfer_request(self, repo_full_name: str, new_owner: str) -> Dict[str, Any]:
        """
        Initiate a repository transfer to another user.
        
        Args:
            repo_full_name: Full repository name (owner/repo).
            new_owner: GitHub username to transfer to.
            
        Returns:
            Dictionary with operation result.
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            
            # Initiate transfer
            repo._requester.requestJsonAndCheck(
                "POST",
                f"/repos/{repo_full_name}/transfer",
                input={"new_owner": new_owner}
            )
            
            return {
                'success': True,
                'message': f'Transfer request sent to {new_owner}'
            }
            
        except GithubException as e:
            return {'success': False, 'error': str(e)}
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """
        Validate that a GitHub username exists.
        
        Args:
            username: GitHub username to validate.
            
        Returns:
            Dictionary with validation result.
        """
        try:
            user = self.github.get_user(username)
            return {
                'valid': True,
                'login': user.login,
                'name': user.name,
                'avatar_url': user.avatar_url
            }
        except GithubException:
            return {
                'valid': False,
                'error': f'User {username} not found'
            }
    
    def full_setup_for_trustless(self, target_username: str, customization: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Complete trustless adoption flow:
        1. Fork repo to our account
        2. Enable Actions
        3. Enable Pages
        4. Trigger initialization workflow
        5. Create transfer request
        
        Args:
            target_username: GitHub username to transfer to.
            customization: Optional trait customization.
            
        Returns:
            Dictionary with operation results.
        """
        # Validate username first
        validation = self.validate_username(target_username)
        if not validation.get('valid'):
            return {'success': False, 'error': validation.get('error')}
        
        # Generate unique repo name
        timestamp = int(time.time())
        repo_name = f"forkMonkey-{target_username}-{timestamp}"
        
        # Fork repository
        fork_result = self.fork_repository(repo_name)
        if not fork_result.get('success'):
            return fork_result
        
        repo_full_name = fork_result['full_name']
        
        # Wait for fork to be ready
        time.sleep(5)
        
        # Enable Actions
        actions_result = self.enable_github_actions(repo_full_name)
        if not actions_result.get('success'):
            return {'success': False, 'error': f"Failed to enable Actions: {actions_result.get('error')}"}
        
        # Enable Pages
        pages_result = self.enable_github_pages(repo_full_name)
        
        # Wait before triggering workflow
        time.sleep(3)
        
        # Trigger initialization workflow
        workflow_result = self.trigger_workflow(repo_full_name)
        
        # Wait for workflow to start
        time.sleep(5)
        
        # Create transfer request
        transfer_result = self.create_transfer_request(repo_full_name, target_username)
        if not transfer_result.get('success'):
            return {'success': False, 'error': f"Failed to initiate transfer: {transfer_result.get('error')}"}
        
        return {
            'success': True,
            'repo_name': repo_name,
            'repo_url': fork_result.get('url'),
            'github_username': target_username,
            'pages_url': pages_result.get('pages_url'),
            'message': f'Repository created and transfer request sent to {target_username}'
        }
