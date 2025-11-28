"""
Tests for types module.

This module contains Pydantic models for input validation and data structures.
"""

import pytest
from pydantic import ValidationError

from src.types import ActorInput, ExtractedData, PageData


class TestActorInput:
    """Test cases for ActorInput model."""

    def test_valid_input_with_required_fields(self):
        """Test that valid input with required fields passes validation."""
        input_data = {
            "startUrls": [
                {"url": "https://example.com"},
                {"url": "https://example.org"},
            ],
        }
        actor_input = ActorInput(**input_data)
        assert len(actor_input.startUrls) == 2
        assert actor_input.maxPages == 10  # default value
        assert actor_input.headless is True  # default value

    def test_valid_input_with_all_fields(self):
        """Test that valid input with all fields passes validation."""
        input_data = {
            "startUrls": [{"url": "https://example.com"}],
            "maxPages": 5,
            "waitForSelector": ".content",
            "extractText": True,
            "extractLinks": True,
            "extractImages": False,
            "headless": False,
            "viewportWidth": 1280,
            "viewportHeight": 720,
        }
        actor_input = ActorInput(**input_data)
        assert actor_input.maxPages == 5
        assert actor_input.waitForSelector == ".content"
        assert actor_input.extractText is True
        assert actor_input.headless is False
        assert actor_input.viewportWidth == 1280
        assert actor_input.viewportHeight == 720

    def test_missing_required_field(self):
        """Test that missing required field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ActorInput(**{})
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("startUrls",) for error in errors)

    def test_empty_start_urls(self):
        """Test that empty startUrls list is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            ActorInput(startUrls=[])
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("startUrls",) for error in errors)

    def test_invalid_max_pages(self):
        """Test that invalid maxPages values are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ActorInput(startUrls=[{"url": "https://example.com"}], maxPages=0)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("maxPages",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            ActorInput(startUrls=[{"url": "https://example.com"}], maxPages=2000)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("maxPages",) for error in errors)

    def test_invalid_viewport_dimensions(self):
        """Test that invalid viewport dimensions are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ActorInput(
                startUrls=[{"url": "https://example.com"}], viewportWidth=100
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("viewportWidth",) for error in errors)

        with pytest.raises(ValidationError) as exc_info:
            ActorInput(
                startUrls=[{"url": "https://example.com"}], viewportHeight=100
            )
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("viewportHeight",) for error in errors)


class TestPageData:
    """Test cases for PageData model."""

    def test_valid_page_data(self):
        """Test that valid page data passes validation."""
        page_data = PageData(
            url="https://example.com",
            title="Example",
            text="Some text content",
            links=["https://example.com/page1"],
            images=["https://example.com/image.jpg"],
        )
        assert str(page_data.url) == "https://example.com/"
        assert page_data.title == "Example"
        assert len(page_data.links) == 1
        assert len(page_data.images) == 1

    def test_page_data_with_minimal_fields(self):
        """Test that page data with minimal fields passes validation."""
        page_data = PageData(url="https://example.com")
        assert str(page_data.url) == "https://example.com/"
        assert page_data.title is None
        assert page_data.text is None
        assert page_data.links == []
        assert page_data.images == []

    def test_invalid_url(self):
        """Test that invalid URL format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PageData(url="not-a-url")
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("url",) for error in errors)


class TestExtractedData:
    """Test cases for ExtractedData model."""

    def test_valid_extracted_data(self):
        """Test that valid extracted data passes validation."""
        pages = [
            PageData(url="https://example.com", title="Page 1"),
            PageData(url="https://example.org", title="Page 2"),
        ]
        extracted = ExtractedData(pages=pages)
        assert len(extracted.pages) == 2
        assert extracted.totalPages == 2

    def test_empty_extracted_data(self):
        """Test that empty extracted data is valid."""
        extracted = ExtractedData(pages=[])
        assert len(extracted.pages) == 0
        assert extracted.totalPages == 0

    def test_total_pages_calculation(self):
        """Test that totalPages is correctly calculated."""
        pages = [PageData(url=f"https://example.com/page{i}") for i in range(5)]
        extracted = ExtractedData(pages=pages)
        # totalPages is now a computed property
        assert extracted.totalPages == 5

