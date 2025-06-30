"""GitHub API client for Reading List Generator."""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import AsyncIterator, Dict, List, Optional, Union

import aiohttp
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import GitHubConfig

logger = logging.getLogger(__name__)


@dataclass
class Repository:
    """GitHub repository representation."""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    stargazers_count: int
    language: Optional[str]
    topics: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    size: int = 0
    default_branch: str = "main"
    archived: bool = False
    disabled: bool = False
    private: bool = False
    fork: bool = False
    license: Optional[Dict] = None
    open_issues_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    network_count: int = 0
    subscribers_count: int = 0

    def dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "html_url": self.html_url,
            "stargazers_count": self.stargazers_count,
            "language": self.language,
            "topics": self.topics,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "pushed_at": self.pushed_at,
            "size": self.size,
            "default_branch": self.default_branch,
            "archived": self.archived,
            "disabled": self.disabled,
            "private": self.private,
            "fork": self.fork,
            "license": self.license,
            "open_issues_count": self.open_issues_count,
            "forks_count": self.forks_count,
            "watchers_count": self.watchers_count,
            "network_count": self.network_count,
            "subscribers_count": self.subscribers_count,
        }

    @classmethod
    def from_api_response(cls, data: Dict) -> "Repository":
        """Create Repository from GitHub API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            stargazers_count=data["stargazers_count"],
            language=data.get("language"),
            topics=data.get("topics", []),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
            pushed_at=cls._parse_datetime(data.get("pushed_at")),
            size=data.get("size", 0),
            default_branch=data.get("default_branch", "main"),
            archived=data.get("archived", False),
            disabled=data.get("disabled", False),
            private=data.get("private", False),
            fork=data.get("fork", False),
            license=data.get("license"),
            open_issues_count=data.get("open_issues_count", 0),
            forks_count=data.get("forks_count", 0),
            watchers_count=data.get("watchers_count", 0),
            network_count=data.get("network_count", 0),
            subscribers_count=data.get("subscribers_count", 0),
        )

    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse GitHub API datetime string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None


class GitHubAPIError(Exception):
    """GitHub API error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(GitHubAPIError):
    """Rate limit exceeded error."""
    
    def __init__(self, reset_time: Optional[int] = None):
        super().__init__("GitHub API rate limit exceeded")
        self.reset_time = reset_time


class GitHubClient:
    """GitHub API client with rate limiting and caching."""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.session = self._create_session()
        self._rate_limit_remaining = config.rate_limit
        self._rate_limit_reset = 0
        
        logger.info("GitHub client initialized")
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Default headers
        session.headers.update({
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Reading-List-Generator/1.0",
        })
        
        return session
    
    def _check_rate_limit(self, response: requests.Response) -> None:
        """Check and update rate limit information."""
        if "X-RateLimit-Remaining" in response.headers:
            self._rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
        
        if "X-RateLimit-Reset" in response.headers:
            self._rate_limit_reset = int(response.headers["X-RateLimit-Reset"])
        
        if response.status_code == 403 and "rate limit" in response.text.lower():
            raise RateLimitError(self._rate_limit_reset)
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Union[Dict, List]:
        """Make HTTP request with error handling."""
        full_url = f"{self.config.base_url.rstrip('/')}/{url.lstrip('/')}"
        
        try:
            response = self.session.request(
                method,
                full_url,
                timeout=self.config.timeout,
                **kwargs
            )
            
            self._check_rate_limit(response)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise GitHubAPIError(f"Resource not found: {url}", 404)
            elif response.status_code == 401:
                raise GitHubAPIError("Authentication failed - check your token", 401)
            elif response.status_code == 403:
                if "rate limit" in response.text.lower():
                    raise RateLimitError(self._rate_limit_reset)
                else:
                    raise GitHubAPIError(f"Access forbidden: {response.text}", 403)
            else:
                raise GitHubAPIError(
                    f"API request failed with status {response.status_code}: {response.text}",
                    response.status_code
                )
                
        except requests.exceptions.Timeout:
            raise GitHubAPIError(f"Request timeout after {self.config.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise GitHubAPIError("Connection error - check your internet connection")
        except requests.exceptions.RequestException as e:
            raise GitHubAPIError(f"Request failed: {str(e)}")
    
    def get_starred_repositories_sync(
        self, 
        username: str, 
        per_page: int = 100
    ) -> List[Repository]:
        """Get starred repositories synchronously."""
        repositories = []
        page = 1
        
        while True:
            logger.info(f"Fetching page {page} of starred repositories for {username}")
            
            try:
                data = self._make_request(
                    "GET",
                    f"users/{username}/starred",
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "direction": "desc",
                    }
                )
                
                if not data:
                    break
                
                page_repos = [Repository.from_api_response(repo_data) for repo_data in data]
                repositories.extend(page_repos)
                
                logger.info(f"Fetched {len(page_repos)} repositories from page {page}")
                
                # If we got fewer repos than requested, we're done
                if len(data) < per_page:
                    break
                
                page += 1
                
                # Add delay to respect rate limits
                if self.config.request_delay > 0:
                    import time
                    time.sleep(self.config.request_delay)
                
            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded. Reset time: {e.reset_time}")
                raise
            except GitHubAPIError as e:
                logger.error(f"GitHub API error: {e}")
                raise
        
        logger.info(f"Total repositories fetched: {len(repositories)}")
        return repositories
    
    async def get_starred_repositories(
        self, 
        username: str, 
        per_page: int = 100
    ) -> AsyncIterator[Repository]:
        """Get starred repositories asynchronously."""
        page = 1
        
        async with aiohttp.ClientSession(
            headers={
                "Authorization": f"token {self.config.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "GitHub-Reading-List-Generator/1.0",
            },
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        ) as session:
            
            while True:
                url = f"{self.config.base_url}/users/{username}/starred"
                params = {
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc",
                }
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if not data:
                                break
                            
                            for repo_data in data:
                                yield Repository.from_api_response(repo_data)
                            
                            logger.info(f"Fetched {len(data)} repositories from page {page}")
                            
                            # If we got fewer repos than requested, we're done
                            if len(data) < per_page:
                                break
                            
                            page += 1
                            
                            # Add delay to respect rate limits
                            if self.config.request_delay > 0:
                                await asyncio.sleep(self.config.request_delay)
                        
                        elif response.status == 404:
                            raise GitHubAPIError(f"User not found: {username}", 404)
                        elif response.status == 401:
                            raise GitHubAPIError("Authentication failed - check your token", 401)
                        elif response.status == 403:
                            raise RateLimitError()
                        else:
                            error_text = await response.text()
                            raise GitHubAPIError(
                                f"API request failed with status {response.status}: {error_text}",
                                response.status
                            )
                
                except aiohttp.ClientTimeout:
                    raise GitHubAPIError(f"Request timeout after {self.config.timeout} seconds")
                except aiohttp.ClientError as e:
                    raise GitHubAPIError(f"Request failed: {str(e)}")
    
    def get_repository_content(
        self, 
        owner: str, 
        repo: str, 
        path: str = "README.md"
    ) -> Optional[str]:
        """Get repository file content."""
        try:
            data = self._make_request(
                "GET",
                f"repos/{owner}/{repo}/contents/{path}"
            )
            
            if isinstance(data, dict) and data.get("content"):
                import base64
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
            
        except GitHubAPIError as e:
            if e.status_code == 404:
                logger.debug(f"File not found: {path} in {owner}/{repo}")
            else:
                logger.error(f"Error fetching content: {e}")
        
        return None
    
    def get_repository_stats(self, owner: str, repo: str) -> Dict:
        """Get repository statistics."""
        try:
            data = self._make_request("GET", f"repos/{owner}/{repo}")
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "watchers": data.get("watchers_count", 0),
                "issues": data.get("open_issues_count", 0),
                "size": data.get("size", 0),
                "language": data.get("language"),
                "topics": data.get("topics", []),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "pushed_at": data.get("pushed_at"),
            }
        except GitHubAPIError as e:
            logger.error(f"Error fetching repository stats: {e}")
            return {}
    
    def check_api_limits(self) -> Dict:
        """Check current API rate limits."""
        try:
            data = self._make_request("GET", "rate_limit")
            return data.get("resources", {})
        except GitHubAPIError as e:
            logger.error(f"Error checking rate limits: {e}")
            return {}
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.session.close() 