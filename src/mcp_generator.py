"""
MCP resource generation for the MCP Website Tool actor.

This module generates MCP (Model Context Protocol) resources from extracted page data.
"""

import html as html_module
import json
import re
from typing import Any, Dict, List
from urllib.parse import urlparse

from src.types import InputModel, ExtractedData, PageData
from src.utils import setup_logging


class MCPResourceGenerator:
    """
    Generates MCP resources from extracted page data.

    Converts PageData objects into MCP-compatible resource format.
    """

    def __init__(self, config: InputModel) -> None:
        """
        Initialize the MCP resource generator.

        Args:
            config: Actor input configuration.
        """
        self.config = config
        self.logger = setup_logging()

    def _normalize_uri(self, url: str) -> str:
        """
        Normalize URI by removing trailing slash from base URLs.

        Args:
            url: URL string to normalize.

        Returns:
            Normalized URL string.
        """
        parsed = urlparse(str(url))
        # If path is empty or just '/', remove trailing slash
        if parsed.path in ("", "/"):
            return str(url).rstrip("/")
        return str(url)

    def generate_resources(
        self, extracted_data: ExtractedData
    ) -> List[Dict[str, Any]]:
        """
        Generate MCP resources from extracted data.

        Args:
            extracted_data: ExtractedData containing pages to convert.

        Returns:
            List of MCP resource dictionaries.
        """
        self.logger.info(
            "Generating MCP resources", total_pages=len(extracted_data.pages)
        )

        resources: List[Dict[str, Any]] = []

        for page in extracted_data.pages:
            resource: Dict[str, Any] = {
                "uri": self._normalize_uri(page.url),
                "name": page.title or str(page.url),
                "mimeType": "text/html",
            }

            if page.text:
                resource["text"] = page.text

            if page.links:
                resource["links"] = page.links

            if page.images:
                resource["images"] = page.images

            resources.append(resource)

        self.logger.info("MCP resources generated", count=len(resources))
        return resources

    def save_resources_to_file(
        self, resources: List[Dict[str, Any]], filepath: str
    ) -> None:
        """
        Save MCP resources to a JSON file.

        Args:
            resources: List of MCP resource dictionaries.
            filepath: Path to save the JSON file.
        """
        self.logger.info("Saving MCP resources to file", filepath=filepath)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(resources, f, indent=2, ensure_ascii=False)

        self.logger.info("MCP resources saved", filepath=filepath, count=len(resources))

    def _sanitize_tool_name(self, label: str, action_type: str) -> str:
        """
        Sanitize tool name to be safe: lowercase, underscores, max 40 chars.
        
        Args:
            label: Human-readable label for the action.
            action_type: Type of action (button, input, select, link).
            
        Returns:
            Sanitized tool name.
        """
        # Start with action type and label
        name = f"{action_type}_{label}"
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace spaces and special characters with underscores
        name = re.sub(r'[^a-z0-9_]', '_', name)
        
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        # Truncate to max 40 chars
        if len(name) > 40:
            name = name[:40].rstrip('_')
        
        # Ensure it's not empty
        if not name:
            name = f"{action_type}_action"
        
        return name

    def _sanitize_label(self, label: str) -> str:
        """
        Sanitize label by stripping HTML tags and escaping special characters.
        
        Removes HTML tags and escapes HTML entities to prevent XSS when
        labels are used in JSON descriptions that get inserted into HTML.
        
        Args:
            label: Raw label string potentially containing HTML.
            
        Returns:
            Sanitized label string safe for use in JSON/HTML contexts.
        """
        if not label:
            return ""
        
        # Strip HTML tags using regex (simple and safe for our use case)
        # This removes <tag> and </tag> patterns
        label = re.sub(r'<[^>]+>', '', label)
        
        # Normalize whitespace (replace multiple spaces with single space)
        label = re.sub(r'\s+', ' ', label)
        
        # Escape HTML entities to prevent XSS
        # This converts <, >, &, ", ' to their HTML entity equivalents
        # This ensures any remaining < or > characters are escaped
        label = html_module.escape(label)
        
        return label.strip()

    def _generate_tool_description(self, action_type: str, label: str) -> str:
        """
        Generate human-readable description for a tool.
        
        Args:
            action_type: Type of action (button, input, select, link).
            label: Human-readable label for the action (will be sanitized).
            
        Returns:
            Tool description with sanitized label.
        """
        # Sanitize label to remove HTML and escape special characters
        sanitized_label = self._sanitize_label(label)
        
        descriptions = {
            "button": f"Click the {sanitized_label} button",
            "input": f"Enter text in the {sanitized_label} input field",
            "select": f"Select an option from the {sanitized_label} dropdown",
            "link": f"Click the {sanitized_label} link",
        }
        return descriptions.get(action_type, f"Interact with the {sanitized_label} {action_type}")

    def generate_tools_from_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate MCP tools JSON from interactive actions.
        
        Creates a tools array following the 2025 MCP schema format with:
        - name: Safe tool name (lowercase, underscores, max 40 chars)
        - description: Human-readable description
        - input_schema: JSON schema for tool inputs
        
        Args:
            actions: List of action dictionaries with 'type', 'label', and 'selector'.
            
        Returns:
            Dictionary with 'tools' array containing MCP tool definitions.
        """
        self.logger.info("Generating MCP tools from actions", count=len(actions))

        tools = []

        for action in actions:
            action_type = action.get("type", "unknown")
            label = action.get("label", "Unknown")
            selector = action.get("selector", "")

            # Sanitize label to prevent XSS (strip HTML tags and escape entities)
            sanitized_label = self._sanitize_label(label)
            
            # Generate safe tool name (using original label for name generation is OK since it's further sanitized)
            tool_name = self._sanitize_tool_name(label, action_type)

            # Generate description (uses sanitized_label internally)
            description = self._generate_tool_description(action_type, label)

            # Generate input schema with sanitized label in description
            input_schema = {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": f"CSS selector for the {sanitized_label} {action_type}",
                        "default": selector,
                    }
                },
                "required": ["selector"],
            }

            tool = {
                "name": tool_name,
                "description": description,
                "input_schema": input_schema,
            }

            tools.append(tool)

        self.logger.info("MCP tools generated", count=len(tools))

        return {"tools": tools}

