"""
Type definitions for the MCP Website Tool actor.

This module contains Pydantic models for input validation and data structures.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, computed_field, field_validator


class ActorInput(BaseModel):
    """
    Input schema for the Actor.

    Validates and structures the input configuration for website scraping.
    """

    startUrls: List[dict] = Field(
        ..., description="List of URLs to scrape", min_length=1
    )
    maxPages: int = Field(
        default=10, description="Maximum number of pages to scrape", ge=1, le=1000
    )
    waitForSelector: str = Field(
        default="body", description="CSS selector to wait for before extracting data"
    )
    extractText: bool = Field(
        default=True, description="Whether to extract text content from pages"
    )
    extractLinks: bool = Field(
        default=True, description="Whether to extract links from pages"
    )
    extractImages: bool = Field(
        default=False, description="Whether to extract images from pages"
    )
    headless: bool = Field(
        default=True, description="Run browser in headless mode"
    )
    viewportWidth: int = Field(
        default=1920, description="Browser viewport width in pixels", ge=320, le=3840
    )
    viewportHeight: int = Field(
        default=1080, description="Browser viewport height in pixels", ge=240, le=2160
    )


class InputModel(BaseModel):
    """
    Input model for MCP website tool.

    Validates and structures the input configuration for website interaction.
    """

    url: HttpUrl = Field(..., description="URL to interact with")
    cookies: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Optional list of cookies to set (can be JSON string or array)"
    )
    
    @field_validator('cookies', mode='before')
    @classmethod
    def parse_cookies(cls, value: Any) -> Optional[List[Dict[str, str]]]:
        """Parse cookies from JSON string or return as-is if already a list."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return None
            except (json.JSONDecodeError, TypeError):
                return None
        if isinstance(value, list):
            return value
        return None
    removeBanners: bool = Field(
        default=True, description="Whether to remove banners from the page"
    )
    maxActions: int = Field(
        default=50,
        description="Maximum number of actions to perform",
        ge=5,
        le=200,
    )
    # Additional fields for compatibility with existing components
    headless: bool = Field(
        default=True, description="Run browser in headless mode"
    )
    viewportWidth: int = Field(
        default=1920, description="Browser viewport width in pixels", ge=320, le=3840
    )
    viewportHeight: int = Field(
        default=1080, description="Browser viewport height in pixels", ge=240, le=2160
    )
    waitForSelector: str = Field(
        default="body", description="CSS selector to wait for before extracting data"
    )
    extractText: bool = Field(
        default=True, description="Whether to extract text content from pages"
    )
    extractLinks: bool = Field(
        default=True, description="Whether to extract links from pages"
    )
    extractImages: bool = Field(
        default=False, description="Whether to extract images from pages"
    )


class PageData(BaseModel):
    """
    Data extracted from a single page.

    Represents all the information extracted from a webpage.
    """

    url: HttpUrl = Field(..., description="URL of the page")
    title: Optional[str] = Field(default=None, description="Page title")
    text: Optional[str] = Field(default=None, description="Extracted text content")
    links: List[str] = Field(default_factory=list, description="List of links found")
    images: List[str] = Field(
        default_factory=list, description="List of image URLs found"
    )


class ExtractedData(BaseModel):
    """
    Collection of extracted page data.

    Contains all pages scraped and metadata about the extraction.
    """

    pages: List[PageData] = Field(
        default_factory=list, description="List of extracted page data"
    )

    @computed_field
    @property
    def totalPages(self) -> int:
        """Calculate total pages from the pages list."""
        return len(self.pages)

