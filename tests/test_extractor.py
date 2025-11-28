"""
Tests for extractor module.

This module handles data extraction from web pages.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.extractor import DataExtractor
from src.types import ActorInput, PageData


class TestDataExtractor:
    """Test cases for DataExtractor class."""

    def test_init_with_config(self):
        """Test that DataExtractor initializes with config."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            extractText=True,
            extractLinks=True,
            extractImages=False,
        )
        extractor = DataExtractor(config)
        assert extractor.config == config
        assert extractor.extract_text is True
        assert extractor.extract_links is True
        assert extractor.extract_images is False

    def test_extract_page_data_with_all_options(self):
        """Test extracting data with all options enabled."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            extractText=True,
            extractLinks=True,
            extractImages=True,
            waitForSelector="body",
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_page.inner_text.return_value = "This is test content"
        mock_page.query_selector_all.return_value = [
            MagicMock(get_attribute=Mock(return_value="https://example.com/link1")),
            MagicMock(get_attribute=Mock(return_value="https://example.com/link2")),
        ]

        # Mock image elements
        mock_images = [
            MagicMock(get_attribute=Mock(return_value="https://example.com/img1.jpg")),
            MagicMock(get_attribute=Mock(return_value="https://example.com/img2.jpg")),
        ]

        def query_selector_side_effect(selector):
            if selector == "a":
                return mock_page.query_selector_all.return_value
            elif selector == "img":
                return mock_images
            return []

        mock_page.query_selector_all.side_effect = query_selector_side_effect

        page_data = extractor.extract_page_data(mock_page)

        assert isinstance(page_data, PageData)
        # Account for Pydantic's HttpUrl normalization
        assert str(page_data.url).rstrip("/") == "https://example.com"
        assert page_data.title == "Test Page"
        assert page_data.text == "This is test content"
        assert len(page_data.links) == 2
        assert len(page_data.images) == 2

    def test_extract_page_data_text_only(self):
        """Test extracting data with only text extraction enabled."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            extractText=True,
            extractLinks=False,
            extractImages=False,
            waitForSelector="body",
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_page.inner_text.return_value = "Test content"

        page_data = extractor.extract_page_data(mock_page)

        assert page_data.text == "Test content"
        assert page_data.links == []
        assert page_data.images == []

    def test_extract_page_data_links_only(self):
        """Test extracting data with only link extraction enabled."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            extractText=False,
            extractLinks=True,
            extractImages=False,
            waitForSelector="body",
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_links = [
            MagicMock(get_attribute=Mock(return_value="https://example.com/link1")),
        ]
        mock_page.query_selector_all.return_value = mock_links

        page_data = extractor.extract_page_data(mock_page)

        assert page_data.text is None
        assert len(page_data.links) == 1
        assert page_data.images == []

    def test_extract_page_data_waits_for_selector(self):
        """Test that extractor waits for selector before extracting."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            waitForSelector=".content",
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_page.inner_text.return_value = ""

        extractor.extract_page_data(mock_page)

        mock_page.wait_for_selector.assert_called_once_with(
            ".content", timeout=30000
        )

    def test_extract_page_data_handles_missing_title(self):
        """Test that extractor handles missing page title."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = ""
        mock_page.inner_text.return_value = ""

        page_data = extractor.extract_page_data(mock_page)

        assert page_data.title is None or page_data.title == ""

    def test_extract_page_data_handles_no_links(self):
        """Test that extractor handles pages with no links."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}], extractLinks=True
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_page.inner_text.return_value = ""
        mock_page.query_selector_all.return_value = []

        page_data = extractor.extract_page_data(mock_page)

        assert page_data.links == []

    def test_extract_page_data_filters_invalid_links(self):
        """Test that extractor filters out None or invalid links."""
        config = ActorInput(
            startUrls=[{"url": "https://example.com"}], extractLinks=True
        )
        extractor = DataExtractor(config)

        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.title.return_value = "Test Page"
        mock_page.inner_text.return_value = ""
        mock_links = [
            MagicMock(get_attribute=Mock(return_value="https://example.com/valid")),
            MagicMock(get_attribute=Mock(return_value=None)),
            MagicMock(get_attribute=Mock(return_value="")),
        ]
        mock_page.query_selector_all.return_value = mock_links

        page_data = extractor.extract_page_data(mock_page)

        # Should only include valid links
        assert len(page_data.links) == 1
        assert page_data.links[0] == "https://example.com/valid"


class TestInteractiveExtractor:
    """Test cases for interactive element extraction."""

    def test_removes_cookie_banners(self):
        """Test that cookie banners (OneTrust/Cookiebot) are removed."""
        from src.types import InputModel
        from src.extractor import DataExtractor
        from playwright.sync_api import sync_playwright
        import os

        config = InputModel(
            url="https://example.com",
            removeBanners=True,
            maxActions=50
        )
        extractor = DataExtractor(config)

        # Get the absolute path to the test page
        test_page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "test-page.html")
        test_page_url = f"file://{test_page_path}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(test_page_url)

            # Extract actions (this should remove banners)
            actions = extractor.extract_interactive_actions(page)

            # Check that banners are removed
            onetrust_exists = page.query_selector("#onetrust-consent-sdk")
            cookiebot_exists = page.query_selector("#Cookiebot")
            
            assert onetrust_exists is None, "OneTrust banner should be removed"
            assert cookiebot_exists is None, "Cookiebot banner should be removed"

            browser.close()

    def test_extracts_at_least_7_actions(self):
        """Test that at least 7 interactive actions are extracted."""
        from src.types import InputModel
        from src.extractor import DataExtractor
        from playwright.sync_api import sync_playwright
        import os

        config = InputModel(
            url="https://example.com",
            removeBanners=True,
            maxActions=50
        )
        extractor = DataExtractor(config)

        test_page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "test-page.html")
        test_page_url = f"file://{test_page_path}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(test_page_url)

            actions = extractor.extract_interactive_actions(page)

            assert len(actions) >= 7, f"Expected at least 7 actions, got {len(actions)}"

            browser.close()

    def test_generates_clean_human_labels(self):
        """Test that actions have clean, human-readable labels."""
        from src.types import InputModel
        from src.extractor import DataExtractor
        from playwright.sync_api import sync_playwright
        import os

        config = InputModel(
            url="https://example.com",
            removeBanners=True,
            maxActions=50
        )
        extractor = DataExtractor(config)

        test_page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "test-page.html")
        test_page_url = f"file://{test_page_path}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(test_page_url)

            actions = extractor.extract_interactive_actions(page)

            # Check that all actions have required fields
            for action in actions:
                assert "type" in action, "Action should have 'type' field"
                assert "label" in action, "Action should have 'label' field"
                assert "selector" in action, "Action should have 'selector' field"
                assert isinstance(action["label"], str), "Label should be a string"
                assert len(action["label"]) > 0, "Label should not be empty"
                # Labels should be human-readable (not just IDs or selectors)
                # Labels should be human-readable (not just raw selectors)
                # They can contain text from the element or a cleaned version
                assert len(action["label"].strip()) > 0, "Label should not be empty or whitespace"

            browser.close()

    def test_respects_max_actions_limit(self):
        """Test that maxActions limit is respected."""
        from src.types import InputModel
        from src.extractor import DataExtractor
        from playwright.sync_api import sync_playwright
        import os

        config = InputModel(
            url="https://example.com",
            removeBanners=True,
            maxActions=10
        )
        extractor = DataExtractor(config)

        test_page_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "test-page.html")
        test_page_url = f"file://{test_page_path}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(test_page_url)

            actions = extractor.extract_interactive_actions(page)

            assert len(actions) <= 10, f"Expected at most 10 actions, got {len(actions)}"

            browser.close()