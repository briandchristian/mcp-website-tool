"""
Utility functions for the MCP Website Tool actor.

This module contains helper functions for logging, URL normalization,
text sanitization, and Playwright setup.
"""

import re
import subprocess
import sys
from typing import Optional
from urllib.parse import urlparse

import structlog
from playwright.sync_api import sync_playwright


def setup_logging() -> structlog.BoundLogger:
    """
    Configure and return a structured logger.

    Returns:
        A configured structlog logger instance.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def ensure_playwright_installed() -> None:
    """
    Ensure Playwright Chromium browser is installed.

    Attempts to use Playwright, and if it fails due to missing browser,
    automatically runs 'playwright install chromium'.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
    except Exception:
        # Browser not installed, install it
        logger = setup_logging()
        logger.info("Installing Playwright Chromium browser...")
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
        logger.info("Playwright Chromium browser installed successfully")


def normalize_url(url: str) -> str:
    """
    Normalize a URL string.

    Adds https:// protocol if missing, removes trailing slashes,
    and ensures proper formatting.

    Args:
        url: The URL string to normalize.

    Returns:
        Normalized URL string.
    """
    if not url:
        return ""

    url = url.strip()

    # Add protocol if missing
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    # Remove trailing slash from base URLs (URLs with no path or just root path)
    # Parse URL to check path component separately from query/fragment
    parsed = urlparse(url)
    if parsed.path in ("", "/") and url.endswith("/"):
        # Reconstruct URL without trailing slash, preserving query and fragment
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        if parsed.query:
            base_url += f"?{parsed.query}"
        if parsed.fragment:
            base_url += f"#{parsed.fragment}"
        url = base_url

    return url


def sanitize_text(text: Optional[str]) -> str:
    """
    Sanitize text content by removing excessive whitespace.

    Removes multiple consecutive spaces, newlines, and tabs,
    replacing them with single spaces. Strips leading and trailing whitespace.

    Args:
        text: The text to sanitize.

    Returns:
        Sanitized text string.
    """
    if not text:
        return ""

    # Replace multiple whitespace characters with single space
    text = re.sub(r"\s+", " ", text)

    # Strip leading and trailing whitespace
    text = text.strip()

    return text

