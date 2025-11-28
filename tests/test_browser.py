"""
Tests for browser module.

This module handles Playwright browser setup and management.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from playwright.sync_api import Browser, BrowserContext, Page

from src.browser import BrowserManager
from src.types import ActorInput


class TestBrowserManager:
    """Test cases for BrowserManager class."""

    @patch("src.browser.sync_playwright")
    def test_init_creates_browser(self, mock_sync_playwright):
        """Test that BrowserManager initializes browser correctly."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        manager = BrowserManager(config)

        assert manager.browser is not None
        mock_playwright_instance.chromium.launch.assert_called_once()

    @patch("src.browser.sync_playwright")
    def test_init_with_headless_config(self, mock_sync_playwright):
        """Test that BrowserManager respects headless configuration."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(
            startUrls=[{"url": "https://example.com"}], headless=False
        )
        manager = BrowserManager(config)

        # Check that launch was called with headless=False
        call_args = mock_playwright_instance.chromium.launch.call_args
        assert call_args[1]["headless"] is False

    @patch("src.browser.sync_playwright")
    def test_init_with_viewport_config(self, mock_sync_playwright):
        """Test that BrowserManager respects viewport configuration."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(
            startUrls=[{"url": "https://example.com"}],
            viewportWidth=1280,
            viewportHeight=720,
        )
        manager = BrowserManager(config)

        # Check that new_context was called with correct viewport
        call_args = mock_browser.new_context.call_args
        assert call_args[1]["viewport"]["width"] == 1280
        assert call_args[1]["viewport"]["height"] == 720

    @patch("src.browser.sync_playwright")
    def test_create_page(self, mock_sync_playwright):
        """Test that create_page returns a Page instance."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_page = MagicMock(spec=Page)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        manager = BrowserManager(config)

        page = manager.create_page()
        assert page is not None
        mock_context.new_page.assert_called_once()

    @patch("src.browser.sync_playwright")
    def test_close_cleans_up_resources(self, mock_sync_playwright):
        """Test that close properly cleans up browser resources."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        manager = BrowserManager(config)

        manager.close()

        mock_browser.close.assert_called_once()
        mock_context.close.assert_called_once()
        mock_playwright_instance.stop.assert_called_once()

    @patch("src.browser.sync_playwright")
    def test_context_manager_usage(self, mock_sync_playwright):
        """Test that BrowserManager works as a context manager."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance

        config = ActorInput(startUrls=[{"url": "https://example.com"}])

        with BrowserManager(config) as manager:
            assert manager.browser is not None

        # Should have closed on exit
        mock_browser.close.assert_called_once()
        mock_context.close.assert_called_once()
        mock_playwright_instance.stop.assert_called_once()

    @patch("src.browser.Actor")
    @patch("src.browser.sync_playwright")
    def test_error_capture_saves_screenshot_to_key_value_store(
        self, mock_sync_playwright, mock_actor_module
    ):
        """
        Test that when an error occurs, a screenshot is saved to key-value store.
        
        This test verifies that:
        - A page is launched
        - An error is forced
        - A screenshot named error-*.png is saved to key-value store
        - Page content is pushed to dataset
        """
        from src.types import InputModel
        from src.browser import BrowserManager
        
        # Setup mocks - Actor should be a regular MagicMock, not AsyncMock
        mock_kv_store = MagicMock()
        mock_kv_store.set_value = MagicMock()
        mock_actor_module.open_key_value_store = MagicMock(return_value=mock_kv_store)
        mock_actor_module.push_data = MagicMock()
        
        # Setup playwright mocks
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock(spec=Browser)
        mock_context = MagicMock(spec=BrowserContext)
        mock_page = MagicMock(spec=Page)
        
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_sync_playwright.return_value.start.return_value = mock_playwright_instance
        
        # Mock page methods
        mock_page.url = "https://example.com"
        mock_page.content.return_value = "<html><body>Error page</body></html>"
        mock_page.screenshot.return_value = b"fake_screenshot_data"
        
        # Force an error when navigating
        mock_page.goto.side_effect = Exception("Navigation failed")
        
        config = InputModel(url="https://example.com")
        
        # Use the error-handling context manager
        # The exception should be caught and handled, then re-raised
        with BrowserManager(config) as manager:
            with pytest.raises(Exception, match="Navigation failed"):
                with manager.safe_page() as page:
                    # This should raise an error
                    page.goto("https://example.com")
        
        # Verify screenshot was saved to key-value store
        # Check that set_value was called with a key matching error-*.png pattern
        set_value_calls = mock_kv_store.set_value.call_args_list
        screenshot_calls = [
            call for call in set_value_calls
            if len(call[0]) > 0 and call[0][0].startswith("error-") and call[0][0].endswith(".png")
        ]
        assert len(screenshot_calls) > 0, "Screenshot should be saved to key-value store"
        
        # Verify error data was pushed to dataset
        assert mock_actor_module.push_data.called, "Error data should be pushed to dataset"
        
        # Verify the screenshot key matches the pattern
        screenshot_key = screenshot_calls[0][0][0]
        assert screenshot_key.startswith("error-"), f"Screenshot key should start with 'error-', got {screenshot_key}"
        assert screenshot_key.endswith(".png"), f"Screenshot key should end with '.png', got {screenshot_key}"
        
        # Verify screenshot data was passed
        assert screenshot_calls[0][0][1] == b"fake_screenshot_data", "Screenshot data should be passed"
        
        # Verify page content was pushed to dataset
        push_data_calls = mock_actor_module.push_data.call_args_list
        assert len(push_data_calls) > 0, "Error data should be pushed to dataset"
        
        # Verify error data structure
        error_data = push_data_calls[0][0][0]
        assert "error" in error_data, "Error data should contain 'error' field"
        assert "error_type" in error_data, "Error data should contain 'error_type' field"
        assert "url" in error_data, "Error data should contain 'url' field"
        assert "screenshot_key" in error_data, "Error data should contain 'screenshot_key' field"
        assert "page_content" in error_data, "Error data should contain 'page_content' field"
        assert error_data["error"] == "Navigation failed", "Error message should match"
        assert error_data["url"] == "https://example.com", "URL should match"

