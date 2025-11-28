"""
Browser management for the MCP Website Tool actor.

This module handles Playwright browser setup, configuration, and lifecycle management.
"""

import time
from contextlib import contextmanager
from typing import Optional

from apify import Actor
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from src.types import InputModel
from src.utils import setup_logging


class BrowserManager:
    """
    Manages Playwright browser instance and context.

    Handles browser creation, configuration, and cleanup.
    """

    def __init__(self, config: InputModel) -> None:
        """
        Initialize the browser manager.

        Args:
            config: Actor input configuration.
        """
        self.config = config
        self.logger = setup_logging()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._initialize_browser()

    def _initialize_browser(self) -> None:
        """Initialize the Playwright browser and context."""
        self.logger.info("Initializing browser...")
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.config.headless
        )

        self.context = self.browser.new_context(
            viewport={
                "width": self.config.viewportWidth,
                "height": self.config.viewportHeight,
            }
        )

        # Set cookies if provided (safely check for cookies attribute)
        cookies = getattr(self.config, 'cookies', None)
        if cookies:
            # Cookies need to be set after context creation but before navigation
            # Format cookies for Playwright (ensure they have required fields)
            formatted_cookies = []
            for cookie in cookies:
                if isinstance(cookie, dict):
                    # Ensure cookie has required fields for Playwright
                    formatted_cookie = {
                        "name": cookie.get("name", ""),
                        "value": cookie.get("value", ""),
                        "domain": cookie.get("domain", ""),
                        "path": cookie.get("path", "/"),
                    }
                    if formatted_cookie["name"] and formatted_cookie["value"]:
                        formatted_cookies.append(formatted_cookie)
            if formatted_cookies:
                self.context.add_cookies(formatted_cookies)
                self.logger.info("Cookies set", count=len(formatted_cookies))

        self.logger.info(
            "Browser initialized",
            headless=self.config.headless,
            viewport_width=self.config.viewportWidth,
            viewport_height=self.config.viewportHeight,
        )

    def create_page(self) -> Page:
        """
        Create a new page in the browser context.

        Returns:
            A new Page instance.
        """
        if not self.context:
            raise RuntimeError("Browser context not initialized")

        return self.context.new_page()

    @contextmanager
    def safe_page(self):
        """
        Context manager that creates a page with error handling.
        
        On any exception:
        - Takes a screenshot and saves it to key-value store as error-*.png
        - Captures page content and pushes error data to dataset
        - Always closes the page
        
        Yields:
            Page: A Playwright Page instance with error handling.
        """
        page = None
        try:
            page = self.create_page()
            yield page
        except Exception as e:
            if page:
                try:
                    # Generate error screenshot filename with timestamp
                    timestamp = int(time.time() * 1000)
                    screenshot_key = f"error-{timestamp}.png"
                    
                    # Take screenshot
                    screenshot_data = page.screenshot(full_page=True)
                    
                    # Save screenshot to key-value store using synchronous API
                    key_value_store = Actor.open_key_value_store()
                    key_value_store.set_value(screenshot_key, screenshot_data, content_type="image/png")
                    self.logger.error(
                        "Error screenshot saved",
                        screenshot_key=screenshot_key,
                        error=str(e)
                    )
                    
                    # Get page content
                    page_content = page.content()
                    
                    # Push error data to dataset using synchronous API
                    error_data = {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "url": page.url,
                        "screenshot_key": screenshot_key,
                        "page_content": page_content,
                    }
                    Actor.push_data(error_data)
                    self.logger.error(
                        "Error data pushed to dataset",
                        error=str(e),
                        url=page.url
                    )
                except Exception as capture_error:
                    # If error capture itself fails, log it but don't hide original error
                    self.logger.error(
                        "Failed to capture error details",
                        capture_error=str(capture_error),
                        original_error=str(e)
                    )
            # Re-raise the original exception
            raise
        finally:
            # Always close the page
            if page:
                try:
                    page.close()
                except Exception as close_error:
                    self.logger.warning(
                        "Failed to close page",
                        error=str(close_error)
                    )

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Browser closed")

    def __enter__(self) -> "BrowserManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()

