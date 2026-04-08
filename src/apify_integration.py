"""
Helpers for integrating this actor with the Apify Actor API.
"""

import json
from typing import Any, Dict, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen


APIFY_API_BASE_URL = "https://api.apify.com/v2"


def build_apify_actor_api_url(actor_id: str) -> str:
    """Build Apify API URL for a specific actor id."""
    safe_actor_id = quote(actor_id, safe="")
    return f"{APIFY_API_BASE_URL}/acts/{safe_actor_id}"


def build_apify_actor_console_url(actor_id: str) -> str:
    """Build Apify Console URL for a specific actor id."""
    safe_actor_id = quote(actor_id, safe="")
    return f"https://console.apify.com/actors/{safe_actor_id}"


def fetch_apify_actor_details(
    actor_id: str, token: Optional[str] = None, timeout_seconds: int = 20
) -> Dict[str, Any]:
    """
    Fetch core actor metadata from Apify API.

    Returns a normalized dictionary used by `main.py` to enrich run output.
    """
    url = build_apify_actor_api_url(actor_id)
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url=url, headers=headers, method="GET")
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))

    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("Apify API response missing 'data' object")

    latest_build = (
        data.get("taggedBuilds", {}).get("latest", {}).get("buildNumber")
        if isinstance(data.get("taggedBuilds"), dict)
        else None
    )

    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "username": data.get("username"),
        "title": data.get("title"),
        "description": data.get("description"),
        "isPublic": data.get("isPublic"),
        "latestBuild": latest_build,
        "apiUrl": url,
        "consoleUrl": build_apify_actor_console_url(actor_id),
    }
