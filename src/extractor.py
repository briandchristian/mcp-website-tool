"""
Data extraction for the MCP Website Tool actor.

This module handles extracting text, links, images, and other data from web pages.
"""

from typing import List

from playwright.sync_api import Page

from src.types import InputModel, PageData
from src.utils import normalize_url, sanitize_text, setup_logging


class DataExtractor:
    """
    Extracts data from web pages using Playwright.

    Handles extraction of text content, links, images, and metadata.
    """

    def __init__(self, config: InputModel) -> None:
        """
        Initialize the data extractor.

        Args:
            config: Actor input configuration.
        """
        self.config = config
        self.logger = setup_logging()
        self.extract_text = config.extractText
        self.extract_links = config.extractLinks
        self.extract_images = config.extractImages

    def extract_page_data(self, page: Page) -> PageData:
        """
        Extract data from a web page.

        Args:
            page: Playwright Page instance.

        Returns:
            PageData object containing extracted information.
        """
        self.logger.info("Extracting data from page", url=page.url)

        # Wait for the specified selector
        page.wait_for_selector(self.config.waitForSelector, timeout=30000)

        # Extract title
        title = page.title()
        title = sanitize_text(title) if title else None

        # Extract text content
        text = None
        if self.extract_text:
            text = page.inner_text("body")
            text = sanitize_text(text) if text else None

        # Extract links
        links: List[str] = []
        if self.extract_links:
            link_elements = page.query_selector_all("a")
            for link in link_elements:
                href = link.get_attribute("href")
                if href:
                    normalized = normalize_url(href)
                    if normalized and normalized not in links:
                        links.append(normalized)

        # Extract images
        images: List[str] = []
        if self.extract_images:
            image_elements = page.query_selector_all("img")
            for img in image_elements:
                src = img.get_attribute("src")
                if src:
                    normalized = normalize_url(src)
                    if normalized and normalized not in images:
                        images.append(normalized)

        page_data = PageData(
            url=normalize_url(page.url),
            title=title,
            text=text,
            links=links,
            images=images,
        )

        self.logger.info(
            "Page data extracted",
            url=page_data.url,
            title=page_data.title,
            links_count=len(page_data.links),
            images_count=len(page_data.images),
        )

        return page_data

    def extract_interactive_actions(self, page: Page) -> List[dict]:
        """
        Extract interactive actions from a web page.
        
        Removes cookie banners and extracts clickable/interactive elements
        with clean human-readable labels.
        
        Args:
            page: Playwright Page instance.
            
        Returns:
            List of action dictionaries with 'type', 'label', and 'selector' keys.
        """
        self.logger.info("Extracting interactive actions", url=page.url)
        
        # Remove cookie banners if configured
        if self.config.removeBanners:
            page.evaluate("""
                () => {
                    // Remove OneTrust banner
                    const onetrust = document.getElementById('onetrust-consent-sdk');
                    if (onetrust) {
                        onetrust.remove();
                    }
                    
                    // Remove Cookiebot banner
                    const cookiebot = document.getElementById('Cookiebot');
                    if (cookiebot) {
                        cookiebot.remove();
                    }
                    
                    // Remove common cookie banner classes
                    const cookieBanners = document.querySelectorAll(
                        '[id*="cookie"], [id*="Cookie"], [id*="onetrust"], ' +
                        '[class*="cookie"], [class*="Cookie"], [class*="onetrust"]'
                    );
                    cookieBanners.forEach(banner => {
                        if (banner.textContent && (
                            banner.textContent.toLowerCase().includes('cookie') ||
                            banner.textContent.toLowerCase().includes('consent')
                        )) {
                            banner.remove();
                        }
                    });
                }
            """)
            self.logger.info("Cookie banners removed")
        
        # Extract interactive elements using page.evaluate()
        actions = page.evaluate("""
            () => {
                const actions = [];
                
                // Helper function to generate clean label
                function getCleanLabel(element) {
                    // Try aria-label first
                    if (element.getAttribute('aria-label')) {
                        return element.getAttribute('aria-label').trim();
                    }
                    
                    // Try title attribute
                    if (element.getAttribute('title')) {
                        return element.getAttribute('title').trim();
                    }
                    
                    // Try text content
                    const text = element.textContent?.trim();
                    if (text && text.length > 0 && text.length < 100) {
                        return text;
                    }
                    
                    // Try placeholder for inputs
                    if (element.placeholder) {
                        return element.placeholder.trim();
                    }
                    
                    // Try value for buttons/inputs
                    if (element.value) {
                        return element.value.trim();
                    }
                    
                    // Try name attribute
                    if (element.name) {
                        return element.name.trim();
                    }
                    
                    // Fallback to id or class
                    if (element.id) {
                        return element.id.replace(/-/g, ' ').replace(/_/g, ' ');
                    }
                    
                    // Last resort: use tag name
                    return element.tagName.toLowerCase();
                }
                
                // Helper function to generate selector
                function getSelector(element) {
                    if (element.id) {
                        return `#${element.id}`;
                    }
                    if (element.className && typeof element.className === 'string') {
                        const classes = element.className.split(' ').filter(c => c).join('.');
                        if (classes) {
                            return `.${classes}`;
                        }
                    }
                    // Fallback to tag with attributes
                    let selector = element.tagName.toLowerCase();
                    if (element.name) {
                        selector += `[name="${element.name}"]`;
                    }
                    return selector;
                }
                
                // Extract buttons
                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                buttons.forEach(button => {
                    if (button.offsetParent !== null) { // Check if visible
                        actions.push({
                            type: 'button',
                            label: getCleanLabel(button),
                            selector: getSelector(button)
                        });
                    }
                });
                
                // Extract links
                const links = document.querySelectorAll('a[href]');
                links.forEach(link => {
                    if (link.offsetParent !== null && link.href) {
                        actions.push({
                            type: 'link',
                            label: getCleanLabel(link),
                            selector: getSelector(link)
                        });
                    }
                });
                
                // Extract input fields
                const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"], textarea');
                inputs.forEach(input => {
                    if (input.offsetParent !== null) {
                        actions.push({
                            type: 'input',
                            label: getCleanLabel(input),
                            selector: getSelector(input)
                        });
                    }
                });
                
                // Extract select dropdowns
                const selects = document.querySelectorAll('select');
                selects.forEach(select => {
                    if (select.offsetParent !== null) {
                        actions.push({
                            type: 'select',
                            label: getCleanLabel(select),
                            selector: getSelector(select)
                        });
                    }
                });
                
                return actions;
            }
        """)
        
        # Limit actions based on maxActions
        if len(actions) > self.config.maxActions:
            actions = actions[:self.config.maxActions]
            self.logger.info(
                "Actions limited",
                total=len(actions),
                max=self.config.maxActions
            )
        
        self.logger.info(
            "Interactive actions extracted",
            count=len(actions),
            types=list({action['type'] for action in actions})
        )
        
        return actions

