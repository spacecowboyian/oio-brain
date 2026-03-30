#!/usr/bin/env python3
"""
OIO Racing - PostBridge API Client Library

Python client for PostBridge API integration to enable draft creation,
scheduling, and publishing to Instagram/Facebook.

Usage:
    from postbridge_client import PostBridgeClient

    # Initialize client (reads POSTBRIDGE_API_KEY from environment)
    client = PostBridgeClient()

    # List connected accounts
    accounts = client.list_accounts()

    # Create a draft post
    draft = client.create_draft(
        caption="Check out our latest race highlights! 🏁",
        account_ids=[12345],
        media_urls=["https://example.com/image.jpg"]
    )

    # Schedule post for future publish
    scheduled = client.schedule_post(
        caption="Race day is here!",
        account_ids=[12345],
        scheduled_at="2026-04-01T09:00:00Z"
    )

    # Publish immediately
    published = client.publish_post(
        caption="We just won! 🏆",
        account_ids=[12345]
    )

Credentials:
    Set POSTBRIDGE_API_KEY environment variable with your API key.
    Get your API key from: https://postbridge.app/settings/api
"""

import os
import sys
import time
from typing import Dict, List, Optional, Any

try:
    import requests
except ImportError:
    print("Error: requests is not installed.")
    print("Run: pip install requests")
    raise

# PostBridge API configuration
POSTBRIDGE_API_BASE = "https://api.postbridge.app/v1"
DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 3
RATE_LIMIT_WAIT = 60  # seconds to wait on rate limit


class PostBridgeError(Exception):
    """Base exception for PostBridge API errors."""
    pass


class PostBridgeAuthError(PostBridgeError):
    """Authentication error (invalid or missing API key)."""
    pass


class PostBridgeRateLimitError(PostBridgeError):
    """Rate limit exceeded."""
    pass


class PostBridgeClient:
    """
    Client for PostBridge API operations.

    Handles authentication, error handling, and retry logic for all
    PostBridge API endpoints.

    Args:
        api_key: PostBridge API key. If not provided, reads from
                 POSTBRIDGE_API_KEY environment variable.
        base_url: API base URL (default: https://api.postbridge.app/v1)
        timeout: Request timeout in seconds (default: 30)
        retries: Number of retry attempts for transient errors (default: 3)

    Raises:
        PostBridgeAuthError: If API key is not provided or invalid.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = POSTBRIDGE_API_BASE,
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES
    ):
        self.api_key = api_key or os.environ.get("POSTBRIDGE_API_KEY", "").strip()
        if not self.api_key:
            raise PostBridgeAuthError(
                "POSTBRIDGE_API_KEY not set. "
                "Get your API key from https://postbridge.app/settings/api"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an API request with retry logic.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path (e.g. "/posts")
            params: Query parameters
            json: JSON request body

        Returns:
            Parsed JSON response

        Raises:
            PostBridgeAuthError: On 401/403 responses
            PostBridgeRateLimitError: On 429 responses
            PostBridgeError: On other API errors
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )

                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    wait_time = RATE_LIMIT_WAIT * (attempt + 1)
                    if attempt < self.retries - 1:
                        print(f"Rate limited — waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    raise PostBridgeRateLimitError(
                        f"Rate limit exceeded after {self.retries} attempts"
                    )

                # Handle authentication errors
                if response.status_code in (401, 403):
                    raise PostBridgeAuthError(
                        f"Authentication failed: {response.text}"
                    )

                # Raise for other HTTP errors
                response.raise_for_status()

                # Return parsed JSON response
                return response.json()

            except requests.RequestException as exc:
                if attempt < self.retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"Request failed — retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                raise PostBridgeError(
                    f"API request failed after {self.retries} attempts: {exc}"
                ) from exc

        return {}

    def list_accounts(self) -> List[Dict[str, Any]]:
        """
        List all connected social media accounts.

        Returns:
            List of account dictionaries with id, platform, and username.

        Example:
            >>> client = PostBridgeClient()
            >>> accounts = client.list_accounts()
            >>> for account in accounts:
            ...     print(f"{account['platform']}: {account['username']} (ID: {account['id']})")
            instagram: oioracing (ID: 12345)
            facebook: OIO Racing (ID: 67890)
        """
        response = self._request("GET", "/social-accounts")
        return response.get("data", [])

    def create_draft(
        self,
        caption: str,
        account_ids: List[int],
        media_urls: Optional[List[str]] = None,
        media_ids: Optional[List[str]] = None,
        platform_configurations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a draft post (saved in PostBridge only, not published).

        Args:
            caption: Post caption/text content
            account_ids: List of social account IDs to post to
            media_urls: List of publicly accessible image/video URLs
            media_ids: List of previously uploaded media IDs
            platform_configurations: Per-platform caption/media overrides

        Returns:
            Created draft post data including id and status.

        Note:
            Drafts are saved in PostBridge with is_draft=true.
            They will publish immediately (not as platform drafts) when sent.

        Example:
            >>> client = PostBridgeClient()
            >>> draft = client.create_draft(
            ...     caption="Race highlights from last weekend! 🏁",
            ...     account_ids=[12345],
            ...     media_urls=["https://example.com/race-photo.jpg"]
            ... )
            >>> print(f"Draft created with ID: {draft['id']}")
        """
        payload = {
            "caption": caption,
            "social_accounts": account_ids,
            "is_draft": True,
        }

        if media_urls:
            payload["media_urls"] = media_urls
        if media_ids:
            payload["media"] = media_ids
        if platform_configurations:
            payload["platform_configurations"] = platform_configurations

        response = self._request("POST", "/posts", json=payload)
        return response.get("data", {})

    def list_drafts(
        self,
        limit: int = 50,
        offset: int = 0,
        platform: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List pending draft posts.

        Args:
            limit: Number of drafts to return (default: 50)
            offset: Pagination offset (default: 0)
            platform: Filter by platform (instagram, facebook, etc.)

        Returns:
            List of draft posts with id, caption, status, and accounts.

        Note:
            Drafts have status='scheduled' and is_draft=true.

        Example:
            >>> client = PostBridgeClient()
            >>> drafts = client.list_drafts()
            >>> for draft in drafts:
            ...     if draft.get('is_draft'):
            ...         print(f"Draft {draft['id']}: {draft['caption'][:50]}...")
        """
        params = {
            "limit": limit,
            "offset": offset,
            "status": "scheduled",  # Drafts have status='scheduled'
        }

        if platform:
            params["platform"] = platform

        response = self._request("GET", "/posts", params=params)
        posts = response.get("data", [])

        # Filter to only drafts (is_draft=true)
        return [post for post in posts if post.get("is_draft")]

    def update_draft(
        self,
        post_id: str,
        caption: Optional[str] = None,
        account_ids: Optional[List[int]] = None,
        media_urls: Optional[List[str]] = None,
        media_ids: Optional[List[str]] = None,
        platform_configurations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a draft post.

        Args:
            post_id: The draft post ID to update
            caption: New caption text
            account_ids: New list of social account IDs
            media_urls: New list of public media URLs
            media_ids: New list of media IDs
            platform_configurations: New platform-specific overrides

        Returns:
            Updated post data.

        Example:
            >>> client = PostBridgeClient()
            >>> updated = client.update_draft(
            ...     post_id="abc123",
            ...     caption="Updated race highlights! 🏁 #Racing"
            ... )
        """
        payload = {"id": post_id}

        if caption is not None:
            payload["caption"] = caption
        if account_ids is not None:
            payload["social_accounts"] = account_ids
        if media_urls is not None:
            payload["media_urls"] = media_urls
        if media_ids is not None:
            payload["media"] = media_ids
        if platform_configurations is not None:
            payload["platform_configurations"] = platform_configurations

        response = self._request("PATCH", f"/posts/{post_id}", json=payload)
        return response.get("data", {})

    def schedule_post(
        self,
        caption: str,
        account_ids: List[int],
        scheduled_at: str,
        media_urls: Optional[List[str]] = None,
        media_ids: Optional[List[str]] = None,
        platform_configurations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a post for future publishing.

        Args:
            caption: Post caption/text content
            account_ids: List of social account IDs to post to
            scheduled_at: ISO 8601 datetime (e.g. "2026-04-01T09:00:00Z")
            media_urls: List of publicly accessible image/video URLs
            media_ids: List of previously uploaded media IDs
            platform_configurations: Per-platform caption/media overrides

        Returns:
            Scheduled post data including id and scheduled_at.

        Example:
            >>> client = PostBridgeClient()
            >>> scheduled = client.schedule_post(
            ...     caption="Race day is here! 🏁",
            ...     account_ids=[12345],
            ...     scheduled_at="2026-04-01T09:00:00Z",
            ...     media_urls=["https://example.com/race-day.jpg"]
            ... )
            >>> print(f"Post scheduled for {scheduled['scheduled_at']}")
        """
        payload = {
            "caption": caption,
            "social_accounts": account_ids,
            "scheduled_at": scheduled_at,
        }

        if media_urls:
            payload["media_urls"] = media_urls
        if media_ids:
            payload["media"] = media_ids
        if platform_configurations:
            payload["platform_configurations"] = platform_configurations

        response = self._request("POST", "/posts", json=payload)
        return response.get("data", {})

    def publish_post(
        self,
        caption: str,
        account_ids: List[int],
        media_urls: Optional[List[str]] = None,
        media_ids: Optional[List[str]] = None,
        platform_configurations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Publish a post immediately.

        Args:
            caption: Post caption/text content
            account_ids: List of social account IDs to post to
            media_urls: List of publicly accessible image/video URLs
            media_ids: List of previously uploaded media IDs
            platform_configurations: Per-platform caption/media overrides

        Returns:
            Published post data including id and status.

        Note:
            Omitting scheduled_at publishes the post immediately.

        Example:
            >>> client = PostBridgeClient()
            >>> published = client.publish_post(
            ...     caption="We just won the race! 🏆 #Victory",
            ...     account_ids=[12345, 67890],
            ...     media_urls=["https://example.com/victory.jpg"]
            ... )
            >>> print(f"Post published with ID: {published['id']}")
        """
        payload = {
            "caption": caption,
            "social_accounts": account_ids,
        }
        # Omitting scheduled_at publishes immediately

        if media_urls:
            payload["media_urls"] = media_urls
        if media_ids:
            payload["media"] = media_ids
        if platform_configurations:
            payload["platform_configurations"] = platform_configurations

        response = self._request("POST", "/posts", json=payload)
        return response.get("data", {})

    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get details of a single post by ID.

        Args:
            post_id: The post ID

        Returns:
            Post data including status, caption, media, and platform results.

        Example:
            >>> client = PostBridgeClient()
            >>> post = client.get_post("abc123")
            >>> print(f"Status: {post['status']}")
        """
        response = self._request("GET", f"/posts/{post_id}")
        return response.get("data", {})

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a scheduled or draft post.

        Args:
            post_id: The post ID to delete

        Returns:
            Deletion confirmation response.

        Note:
            Published posts cannot be deleted via the API.

        Example:
            >>> client = PostBridgeClient()
            >>> client.delete_post("abc123")
        """
        response = self._request("DELETE", f"/posts/{post_id}")
        return response

    def list_posts(
        self,
        limit: int = 50,
        offset: int = 0,
        platform: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List posts with optional filters.

        Args:
            limit: Number of posts to return (default: 50)
            offset: Pagination offset (default: 0)
            platform: Filter by platform (instagram, facebook, etc.)
            status: Filter by status (scheduled, processing, posted)

        Returns:
            List of posts with id, caption, status, and accounts.

        Example:
            >>> client = PostBridgeClient()
            >>> posts = client.list_posts(status="posted", limit=10)
            >>> for post in posts:
            ...     print(f"{post['status']}: {post['caption'][:50]}...")
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        if platform:
            params["platform"] = platform
        if status:
            params["status"] = status

        response = self._request("GET", "/posts", params=params)
        return response.get("data", [])


# ---------------------------------------------------------------------------
# CLI example
# ---------------------------------------------------------------------------

def main():
    """
    Simple CLI example showing basic usage.
    Run: python scripts/postbridge_client.py
    """
    try:
        client = PostBridgeClient()
    except PostBridgeAuthError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("PostBridge API Client - Connected Accounts")
    print("=" * 50)

    try:
        accounts = client.list_accounts()
        if not accounts:
            print("No connected accounts found.")
            print("Connect accounts at: https://postbridge.app/settings/accounts")
        else:
            for account in accounts:
                platform = account.get("platform", "unknown")
                username = account.get("username", "unknown")
                account_id = account.get("id", "unknown")
                print(f"  {platform:12} {username:20} (ID: {account_id})")

        print("\nRecent Posts")
        print("=" * 50)
        posts = client.list_posts(limit=5)
        if not posts:
            print("No posts found.")
        else:
            for post in posts:
                post_id = post.get("id", "unknown")
                status = post.get("status", "unknown")
                is_draft = post.get("is_draft", False)
                caption = post.get("caption", "")[:60]
                draft_label = " [DRAFT]" if is_draft else ""
                print(f"  {post_id}: {status}{draft_label}")
                print(f"    {caption}...")
                print()

    except PostBridgeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
