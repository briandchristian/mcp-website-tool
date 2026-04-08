"""
Tests for Apify API integration helpers.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.apify_integration import (
    build_apify_actor_api_url,
    fetch_apify_actor_details,
)


def test_build_apify_actor_api_url():
    """Builds the canonical Apify Actor API URL."""
    actor_id = "2eLvo5XF9TcYOW1Xo"
    assert (
        build_apify_actor_api_url(actor_id)
        == "https://api.apify.com/v2/acts/2eLvo5XF9TcYOW1Xo"
    )


@patch("src.apify_integration.urlopen")
def test_fetch_apify_actor_details_parses_response(mock_urlopen):
    """Parses key actor details from the Apify API response."""
    payload = {
        "data": {
            "id": "2eLvo5XF9TcYOW1Xo",
            "name": "mcp-website-tool",
            "username": "clever_fashion",
            "title": "MCP tools - Turn Any Website into an AI Tool in 60 Seconds",
            "description": "Test description",
            "isPublic": True,
            "taggedBuilds": {"latest": {"buildNumber": "0.0.37"}},
        }
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    details = fetch_apify_actor_details("2eLvo5XF9TcYOW1Xo")

    assert details["id"] == "2eLvo5XF9TcYOW1Xo"
    assert details["name"] == "mcp-website-tool"
    assert details["username"] == "clever_fashion"
    assert details["title"] == "MCP tools - Turn Any Website into an AI Tool in 60 Seconds"
    assert details["latestBuild"] == "0.0.37"
    assert details["apiUrl"] == "https://api.apify.com/v2/acts/2eLvo5XF9TcYOW1Xo"


@patch("src.apify_integration.urlopen")
def test_fetch_apify_actor_details_uses_auth_header_when_token_set(mock_urlopen):
    """Adds Bearer auth when token is provided."""
    payload = {
        "data": {
            "id": "2eLvo5XF9TcYOW1Xo",
            "name": "mcp-website-tool",
            "username": "clever_fashion",
            "title": "MCP tools",
        }
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(payload).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    fetch_apify_actor_details("2eLvo5XF9TcYOW1Xo", token="secret-token")

    request_obj = mock_urlopen.call_args[0][0]
    assert request_obj.headers["Authorization"] == "Bearer secret-token"


@patch("src.apify_integration.urlopen")
def test_fetch_apify_actor_details_raises_for_invalid_payload(mock_urlopen):
    """Raises ValueError when response payload does not include actor data."""
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({"unexpected": "payload"}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    with pytest.raises(ValueError, match="missing 'data' object"):
        fetch_apify_actor_details("2eLvo5XF9TcYOW1Xo")
