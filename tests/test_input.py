"""
Tests for InputModel validation.

This module tests the InputModel Pydantic model for input validation.
"""

import pytest
from pydantic import ValidationError

from src.types import InputModel


def test_input_requires_valid_url():
    """Test that InputModel requires a valid URL."""
    with pytest.raises(ValidationError):
        InputModel(url="not-a-url")

    InputModel(url="https://google.com")
    InputModel(url="https://example.com", maxActions=25)


def test_input_accepts_valid_apify_actor_id():
    """Test that InputModel accepts a valid Apify actor identifier."""
    model = InputModel(url="https://example.com", apifyActorId="2eLvo5XF9TcYOW1Xo")
    assert model.apifyActorId == "2eLvo5XF9TcYOW1Xo"


def test_input_rejects_invalid_apify_actor_id():
    """Test that InputModel rejects malformed Apify actor identifiers."""
    with pytest.raises(ValidationError):
        InputModel(url="https://example.com", apifyActorId="invalid-actor-id")

