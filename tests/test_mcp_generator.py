"""
Tests for mcp_generator module.

This module handles MCP resource generation from extracted data.
"""

import json
import pytest
from unittest.mock import Mock, patch, mock_open

from src.mcp_generator import MCPResourceGenerator
from src.types import ActorInput, ExtractedData, PageData


class TestMCPResourceGenerator:
    """Test cases for MCPResourceGenerator class."""

    def test_init_with_config(self):
        """Test that MCPResourceGenerator initializes with config."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)
        assert generator.config == config

    def test_generate_resources_from_extracted_data(self):
        """Test generating MCP resources from extracted data."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(
                url="https://example.com",
                title="Example Page",
                text="Some content",
                links=["https://example.com/page1"],
            ),
            PageData(
                url="https://example.org",
                title="Another Page",
                text="More content",
                links=["https://example.org/page2"],
            ),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert len(resources) == 2
        assert all("uri" in resource for resource in resources)
        assert all("name" in resource for resource in resources)
        assert all("mimeType" in resource for resource in resources)

    def test_generate_resources_uri_format(self):
        """Test that generated resources have correct URI format."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(url="https://example.com", title="Test Page"),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert resources[0]["uri"] == "https://example.com"
        assert resources[0]["name"] == "Test Page"

    def test_generate_resources_mime_type(self):
        """Test that generated resources have correct MIME type."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(url="https://example.com", title="Test Page"),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert resources[0]["mimeType"] == "text/html"

    def test_generate_resources_with_text_content(self):
        """Test that resources include text content when available."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(
                url="https://example.com",
                title="Test Page",
                text="This is test content",
            ),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert "text" in resources[0]
        assert resources[0]["text"] == "This is test content"

    def test_generate_resources_without_text_content(self):
        """Test that resources work without text content."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(url="https://example.com", title="Test Page", text=None),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert "text" not in resources[0] or resources[0]["text"] is None

    def test_generate_resources_with_links(self):
        """Test that resources include links when available."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(
                url="https://example.com",
                title="Test Page",
                links=["https://example.com/link1", "https://example.com/link2"],
            ),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert "links" in resources[0]
        assert len(resources[0]["links"]) == 2

    def test_generate_resources_with_images(self):
        """Test that resources include images when available."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(
                url="https://example.com",
                title="Test Page",
                images=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
            ),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)

        assert "images" in resources[0]
        assert len(resources[0]["images"]) == 2

    def test_generate_resources_empty_data(self):
        """Test that generator handles empty extracted data."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        extracted_data = ExtractedData(pages=[])

        resources = generator.generate_resources(extracted_data)

        assert resources == []

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_resources_to_file(self, mock_json_dump, mock_file):
        """Test saving resources to a JSON file."""
        config = ActorInput(startUrls=[{"url": "https://example.com"}])
        generator = MCPResourceGenerator(config)

        pages = [
            PageData(url="https://example.com", title="Test Page"),
        ]
        extracted_data = ExtractedData(pages=pages)

        resources = generator.generate_resources(extracted_data)
        generator.save_resources_to_file(resources, "test_output.json")

        mock_file.assert_called_once_with("test_output.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()


class TestMCPToolsGenerator:
    """Test cases for MCP tools generation from actions."""

    def test_generate_tools_from_actions(self):
        """Test generating MCP tools JSON from interactive actions."""
        from src.types import InputModel
        from src.mcp_generator import MCPResourceGenerator

        config = InputModel(url="https://example.com")
        generator = MCPResourceGenerator(config)

        # Sample actions (4 actions as specified)
        actions = [
            {"type": "button", "label": "Submit Form", "selector": "#submit-btn"},
            {"type": "input", "label": "Enter username", "selector": "#username"},
            {"type": "select", "label": "Select Country", "selector": "#country"},
            {"type": "link", "label": "About Us", "selector": "#about-link"},
        ]

        # Generate MCP tools JSON
        mcp_json = generator.generate_tools_from_actions(actions)

        # Verify structure
        assert "tools" in mcp_json
        assert isinstance(mcp_json["tools"], list)
        assert len(mcp_json["tools"]) == 4

        # Verify each tool has required fields
        for tool in mcp_json["tools"]:
            assert "name" in tool, "Tool should have 'name' field"
            assert "description" in tool, "Tool should have 'description' field"
            assert "input_schema" in tool, "Tool should have 'input_schema' field"
            assert isinstance(tool["name"], str), "Tool name should be a string"
            assert isinstance(tool["description"], str), "Tool description should be a string"
            assert isinstance(tool["input_schema"], dict), "Tool input_schema should be a dict"

        # Verify tool names are safe (lowercase, underscores, max 40 chars)
        for tool in mcp_json["tools"]:
            name = tool["name"]
            assert name.islower() or name.replace("_", "").islower(), f"Tool name should be lowercase: {name}"
            assert len(name) <= 40, f"Tool name should be max 40 chars: {name} (length: {len(name)})"
            # Should only contain lowercase letters, numbers, and underscores
            assert all(c.islower() or c.isdigit() or c == "_" for c in name), f"Tool name should only contain lowercase, digits, and underscores: {name}"

        # Verify descriptions are meaningful
        assert mcp_json["tools"][0]["description"] == "Click the Submit Form button"
        assert mcp_json["tools"][1]["description"] == "Enter text in the Enter username input field"
        assert mcp_json["tools"][2]["description"] == "Select an option from the Select Country dropdown"
        assert mcp_json["tools"][3]["description"] == "Click the About Us link"

        # Verify input_schema structure (should be valid JSON schema)
        for tool in mcp_json["tools"]:
            schema = tool["input_schema"]
            assert "type" in schema, "input_schema should have 'type' field"
            assert "properties" in schema, "input_schema should have 'properties' field"
            assert schema["type"] == "object", "input_schema type should be 'object'"
            assert "selector" in schema["properties"], "input_schema should have 'selector' property"
