"""
Tests for utils module.

This module contains utility functions for the actor.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.utils import (
    ensure_playwright_installed,
    normalize_url,
    sanitize_text,
    setup_logging,
)


class TestEnsurePlaywrightInstalled:
    """Test cases for ensure_playwright_installed function."""

    @patch("src.utils.sync_playwright")
    def test_playwright_already_installed(self, mock_sync_playwright):
        """Test that function works when Playwright is already installed."""
        mock_browser = MagicMock()
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_sync_playwright.return_value.__enter__.return_value = mock_playwright_context
        ensure_playwright_installed()
        # Should not raise an exception
        assert mock_browser.close.called

    @patch("src.utils.sync_playwright")
    @patch("src.utils.subprocess.run")
    def test_playwright_installation_on_error(
        self, mock_subprocess, mock_sync_playwright
    ):
        """Test that Playwright is installed when not available."""
        # First call raises error, second succeeds
        mock_sync_playwright.side_effect = [
            Exception("Browser not installed"),
            MagicMock(),
        ]
        mock_sync_playwright.return_value.__enter__.return_value.chromium.launch.return_value = MagicMock()

        ensure_playwright_installed()

        # Should have called playwright install
        mock_subprocess.assert_called_once()
        assert "playwright" in str(mock_subprocess.call_args)
        assert "install" in str(mock_subprocess.call_args)


class TestNormalizeUrl:
    """Test cases for normalize_url function."""

    def test_normalize_url_with_http(self):
        """Test that HTTP URLs are normalized correctly."""
        url = "http://example.com"
        result = normalize_url(url)
        assert result == "http://example.com"

    def test_normalize_url_with_https(self):
        """Test that HTTPS URLs are normalized correctly."""
        url = "https://example.com"
        result = normalize_url(url)
        assert result == "https://example.com"

    def test_normalize_url_without_protocol(self):
        """Test that URLs without protocol get https:// prefix."""
        url = "example.com"
        result = normalize_url(url)
        assert result == "https://example.com"

    def test_normalize_url_with_path(self):
        """Test that URLs with paths are preserved."""
        url = "https://example.com/path/to/page"
        result = normalize_url(url)
        assert result == "https://example.com/path/to/page"

    def test_normalize_url_with_query_params(self):
        """Test that URLs with query parameters are preserved."""
        url = "https://example.com?param=value"
        result = normalize_url(url)
        assert result == "https://example.com?param=value"

    def test_normalize_url_removes_trailing_slash(self):
        """Test that trailing slashes are removed."""
        url = "https://example.com/"
        result = normalize_url(url)
        assert result == "https://example.com"

    def test_normalize_url_with_fragment(self):
        """Test that URLs with fragments are preserved."""
        url = "https://example.com#section"
        result = normalize_url(url)
        assert result == "https://example.com#section"


class TestSanitizeText:
    """Test cases for sanitize_text function."""

    def test_sanitize_text_removes_whitespace(self):
        """Test that excessive whitespace is removed."""
        text = "Hello    world\n\n\nTest"
        result = sanitize_text(text)
        assert "  " not in result
        assert "\n\n" not in result

    def test_sanitize_text_strips_edges(self):
        """Test that leading and trailing whitespace is removed."""
        text = "   Hello world   "
        result = sanitize_text(text)
        assert result == "Hello world"

    def test_sanitize_text_handles_empty_string(self):
        """Test that empty strings are handled."""
        text = ""
        result = sanitize_text(text)
        assert result == ""

    def test_sanitize_text_handles_whitespace_only(self):
        """Test that whitespace-only strings return empty."""
        text = "   \n\t  "
        result = sanitize_text(text)
        assert result == ""

    def test_sanitize_text_preserves_content(self):
        """Test that actual content is preserved."""
        text = "This is a test with multiple lines.\nSecond line here."
        result = sanitize_text(text)
        assert "This is a test" in result
        assert "Second line here" in result

    def test_sanitize_text_handles_none(self):
        """Test that None is handled gracefully."""
        result = sanitize_text(None)
        assert result == ""


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging()
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")

    def test_setup_logging_is_consistent(self):
        """Test that multiple calls return consistent loggers."""
        logger1 = setup_logging()
        logger2 = setup_logging()
        # Should return the same configured logger
        assert logger1 is not None
        assert logger2 is not None

