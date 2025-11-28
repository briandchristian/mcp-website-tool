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

