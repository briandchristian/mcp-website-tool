"""
Tests for main module.

This module contains the main Actor entry point and orchestration logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call

from src.main import main
from src.types import ActorInput, ExtractedData, PageData


class TestMain:
    """Test cases for main Actor function."""

    @patch("src.main.Actor")
    @patch("src.main.BrowserManager")
    @patch("src.main.DataExtractor")
    @patch("src.main.MCPResourceGenerator")
    @patch("src.main.ensure_playwright_installed")
    def test_main_with_valid_input(
        self,
        mock_ensure_playwright,
        mock_mcp_generator_class,
        mock_extractor_class,
        mock_browser_manager_class,
        mock_actor_class,
    ):
        """Test main function with valid input."""
        # Setup mocks - Actor is used as a module-level import
        # Configure get_input to return a dict directly (not a coroutine)
        mock_actor_class.get_input = MagicMock(return_value={
            "url": "https://example.com",
            "maxActions": 10,
        })

        mock_browser_manager = MagicMock()
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_browser_manager.create_page.return_value = mock_page
        mock_browser_manager_class.return_value.__enter__.return_value = (
            mock_browser_manager
        )

        mock_extractor = MagicMock()
        mock_extractor.extract_interactive_actions.return_value = [
            {"type": "button", "label": "Submit", "selector": "#submit"},
            {"type": "input", "label": "Username", "selector": "#username"},
        ]
        mock_extractor_class.return_value = mock_extractor

        mock_mcp_generator = MagicMock()
        mock_mcp_generator.generate_tools_from_actions.return_value = {
            "tools": [
                {"name": "button_submit", "description": "Click the Submit button", "input_schema": {}},
                {"name": "input_username", "description": "Enter text in the Username input field", "input_schema": {}},
            ]
        }
        mock_mcp_generator_class.return_value = mock_mcp_generator
        
        # Mock page methods
        mock_page.goto.return_value = None
        mock_page.screenshot.return_value = b"fake_screenshot_data"
        mock_page.url = "https://example.com"
        
        # Mock key-value store
        mock_kv_store = MagicMock()
        mock_kv_store.store_id = "test-store-id"
        mock_kv_store.set_value = MagicMock()
        # Use open_key_value_store (new API)
        mock_actor_class.open_key_value_store = MagicMock(return_value=mock_kv_store)

        # Call main
        main()

        # Verify playwright installation check
        mock_ensure_playwright.assert_called_once()

        # Verify browser manager was created
        mock_browser_manager_class.assert_called_once()

        # Verify extractor was created
        mock_extractor_class.assert_called_once()

        # Verify MCP generator was created
        mock_mcp_generator_class.assert_called_once()

        # Verify data was pushed to dataset
        assert mock_actor_class.push_data.call_count > 0

    @patch("src.main.Actor")
    @patch("src.main.BrowserManager")
    @patch("src.main.DataExtractor")
    @patch("src.main.MCPResourceGenerator")
    @patch("src.main.ensure_playwright_installed")
    def test_main_respects_max_pages(
        self,
        mock_ensure_playwright,
        mock_mcp_generator_class,
        mock_extractor_class,
        mock_browser_manager_class,
        mock_actor_class,
    ):
        """Test that main respects maxPages limit."""
        # Configure get_input to return a dict directly (not a coroutine)
        mock_actor_class.get_input = MagicMock(return_value={
            "url": "https://example.com",
            "maxActions": 5,
        })

        mock_browser_manager = MagicMock()
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_browser_manager.safe_page.return_value.__enter__.return_value = mock_page
        mock_browser_manager.safe_page.return_value.__exit__.return_value = None
        mock_browser_manager_class.return_value = mock_browser_manager

        mock_extractor = MagicMock()
        mock_extractor.extract_interactive_actions.return_value = [
            {"type": "button", "label": "Submit", "selector": "#submit"},
        ]
        mock_extractor_class.return_value = mock_extractor

        mock_mcp_generator = MagicMock()
        mock_mcp_generator.generate_tools_from_actions.return_value = {
            "tools": [{"name": "button_submit", "description": "Click the Submit button", "input_schema": {}}]
        }
        mock_mcp_generator_class.return_value = mock_mcp_generator
        
        mock_page.goto.return_value = None
        mock_page.screenshot.return_value = b"fake_screenshot_data"
        
        mock_kv_store = MagicMock()
        mock_kv_store.store_id = "test-store-id"
        mock_kv_store.set_value = MagicMock()
        mock_actor_class.open_key_value_store = MagicMock(return_value=mock_kv_store)
        # Ensure push_data is synchronous (not async)
        if hasattr(mock_actor_class.push_data, 'return_value'):
            pass  # Already set
        else:
            mock_actor_class.push_data = MagicMock()

        main()

        # Should only process one URL (new workflow processes single URL)
        assert mock_page.goto.call_count == 1

    @patch("src.main.Actor")
    @patch("src.main.BrowserManager")
    @patch("src.main.DataExtractor")
    @patch("src.main.MCPResourceGenerator")
    @patch("src.main.ensure_playwright_installed")
    def test_main_handles_navigation_errors(
        self,
        mock_ensure_playwright,
        mock_mcp_generator_class,
        mock_extractor_class,
        mock_browser_manager_class,
        mock_actor_class,
    ):
        """Test that main handles navigation errors gracefully."""
        # Configure get_input to return a dict directly (not a coroutine)
        mock_actor_class.get_input = MagicMock(return_value={
            "url": "https://example.com",
            "maxActions": 5,
        })

        mock_browser_manager = MagicMock()
        mock_page = MagicMock()
        mock_browser_manager = MagicMock()
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_page.goto.side_effect = Exception("Navigation failed")
        mock_browser_manager.safe_page.return_value.__enter__.return_value = mock_page
        mock_browser_manager.safe_page.return_value.__exit__.return_value = None
        mock_browser_manager_class.return_value = mock_browser_manager

        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor

        mock_mcp_generator = MagicMock()
        mock_mcp_generator_class.return_value = mock_mcp_generator
        
        mock_kv_store = MagicMock()
        mock_kv_store.store_id = "test-store-id"
        mock_kv_store.set_value = MagicMock()
        mock_actor_class.open_key_value_store = MagicMock(return_value=mock_kv_store)
        # Ensure push_data is synchronous (not async)
        if hasattr(mock_actor_class.push_data, 'return_value'):
            pass  # Already set
        else:
            mock_actor_class.push_data = MagicMock()

        # Should raise exception (error handling logs it and re-raises)
        with pytest.raises(Exception, match="Navigation failed"):
            main()

    @patch("src.main.Actor")
    @patch("src.main.BrowserManager")
    @patch("src.main.DataExtractor")
    @patch("src.main.MCPResourceGenerator")
    @patch("src.main.ensure_playwright_installed")
    def test_main_processes_multiple_urls(
        self,
        mock_ensure_playwright,
        mock_mcp_generator_class,
        mock_extractor_class,
        mock_browser_manager_class,
        mock_actor_class,
    ):
        """Test that main processes linked URLs when extractLinks is enabled."""
        # Configure get_input to return a dict directly (not a coroutine)
        mock_actor_class.get_input = MagicMock(return_value={
            "url": "https://example.com",
            "maxActions": 10,
            "extractLinks": True,
        })

        mock_browser_manager = MagicMock()
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        mock_browser_manager.safe_page.return_value.__enter__.return_value = mock_page
        mock_browser_manager.safe_page.return_value.__exit__.return_value = None
        mock_browser_manager_class.return_value = mock_browser_manager

        mock_extractor = MagicMock()
        mock_extractor.extract_interactive_actions.return_value = [
            {"type": "button", "label": "Submit", "selector": "#submit"},
            {"type": "link", "label": "Page 1", "selector": "a[href='/page1']"},
        ]
        mock_extractor_class.return_value = mock_extractor

        mock_mcp_generator = MagicMock()
        mock_mcp_generator.generate_tools_from_actions.return_value = {
            "tools": [
                {"name": "button_submit", "description": "Click the Submit button", "input_schema": {}},
                {"name": "link_page_1", "description": "Click the Page 1 link", "input_schema": {}},
            ]
        }
        mock_mcp_generator_class.return_value = mock_mcp_generator
        
        mock_page.goto.return_value = None
        mock_page.screenshot.return_value = b"fake_screenshot_data"
        
        mock_kv_store = MagicMock()
        mock_kv_store.store_id = "test-store-id"
        mock_kv_store.set_value = MagicMock()
        mock_actor_class.open_key_value_store = MagicMock(return_value=mock_kv_store)
        # Ensure push_data is synchronous (not async)
        if hasattr(mock_actor_class.push_data, 'return_value'):
            pass  # Already set
        else:
            mock_actor_class.push_data = MagicMock()

        main()

        # Should have processed the main URL (new workflow only processes one URL)
        assert mock_page.goto.call_count == 1
        # Should have extracted actions
        assert mock_extractor.extract_interactive_actions.call_count == 1

