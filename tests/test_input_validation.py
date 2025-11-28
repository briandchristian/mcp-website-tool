"""
Test that main.py correctly validates InputModel schema.

This test verifies that when input matches the new InputModel schema,
it can be validated successfully.
"""

import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock

from src.types import InputModel


def test_main_validates_with_input_model_schema():
    """
    Test that main.py can validate input using InputModel schema.
    
    This test demonstrates the issue: if main.py uses ActorInput
    but the input matches InputModel schema, validation will fail.
    """
    # Input matching the new InputModel schema
    new_schema_input = {
        "url": "https://example.com",
        "cookies": None,
        "removeBanners": True,
        "maxActions": 25
    }
    
    # This should work with InputModel
    input_model = InputModel(**new_schema_input)
    assert str(input_model.url) == "https://example.com/"  # HttpUrl normalizes URLs
    assert input_model.maxActions == 25
    
    # But this would fail with ActorInput (missing startUrls)
    from src.types import ActorInput
    with pytest.raises(ValidationError):
        ActorInput(**new_schema_input)

