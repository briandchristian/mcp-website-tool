# MCP.tools Actor – Turn any site into an AI tool

![Price](https://img.shields.io/badge/price-%240.03%2Frun-success)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Apify](https://img.shields.io/badge/Apify-Actor-green.svg)](https://apify.com/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-blue.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Transform any website into an AI tool with MCP (Model Context Protocol) tools. This Apify Actor automatically extracts interactive elements from web pages and generates MCP-compatible tool definitions that can be used with Cursor, Claude, and other AI assistants.

![Demo GIF](https://via.placeholder.com/800x400/667eea/ffffff?text=MCP.tools+Actor+Demo)

## 🚀 Features

- **🎯 Interactive Element Extraction**: Automatically finds buttons, inputs, dropdowns, and links
- **🍪 Cookie Banner Removal**: Removes OneTrust, Cookiebot, and other common cookie banners
- **🔧 MCP Tools Generation**: Creates MCP-compatible tool definitions with safe names and descriptions
- **📸 Visual Preview**: Generates beautiful preview pages with one-click integration buttons
- **🛡️ Error Handling**: Automatic screenshot capture and error logging
- **📊 Structured Output**: Clean JSON format ready for MCP integration

## 📋 Example Input

```json
{
  "url": "https://example.com",
  "cookies": [
    {"name": "session_id", "value": "abc123"}
  ],
  "removeBanners": true,
  "maxActions": 50
}
```

### Input Parameters

- **url** (required): The website URL to process
- **cookies** (optional): List of cookies to set for authenticated pages
- **removeBanners** (default: `true`): Automatically remove cookie consent banners
- **maxActions** (default: `50`, min: `5`, max: `200`): Maximum number of interactive elements to extract

## 📤 Example Output

The actor generates three outputs:

### 1. MCP Tools JSON (`mcp-{id}.json`)

```json
{
  "tools": [
    {
      "name": "button_submit_form",
      "description": "Click the Submit Form button",
      "input_schema": {
        "type": "object",
        "properties": {
          "selector": {
            "type": "string",
            "description": "CSS selector for the Submit Form button",
            "default": "#submit-btn"
          }
        },
        "required": ["selector"]
      }
    },
    {
      "name": "input_username",
      "description": "Enter text in the Enter username input field",
      "input_schema": {
        "type": "object",
        "properties": {
          "selector": {
            "type": "string",
            "description": "CSS selector for the Enter username input field",
            "default": "#username"
          }
        },
        "required": ["selector"]
      }
    }
  ]
}
```

### 2. Dataset Record

```json
{
  "mcpJsonUrl": "https://api.apify.com/v2/key-value-stores/.../records/mcp-abc123.json",
  "previewUrl": "https://api.apify.com/v2/key-value-stores/.../records/preview-abc123.html",
  "screenshotUrl": "https://api.apify.com/v2/key-value-stores/.../records/screenshot-abc123.png",
  "toolCount": 12,
  "url": "https://example.com",
  "runId": "abc123",
  "actionsCount": 12
}
```

### 3. Preview HTML Page

A beautiful preview page with:
- 📊 Statistics dashboard (tools count, actions count, run ID)
- 🚀 One-click buttons for Cursor and Claude integration
- 📋 Visual action cards showing all extracted elements
- 🔧 Pretty-printed MCP JSON for easy inspection

## 💰 Pricing

**$0.03 per run** - Affordable pricing for transforming websites into AI tools.

## 🛠️ Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-website-tool
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

### Running Tests

```bash
pytest
```

## 📖 Usage

### Via Apify Platform

1. Go to [Apify Console](https://console.apify.com)
2. Find the **MCP.tools Actor**
3. Configure input with your target URL
4. Run and get your MCP tools JSON!

### Via API

```bash
curl -X POST "https://api.apify.com/v2/acts/YOUR_ACTOR_ID/run-sync" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "maxActions": 50
  }'
```

## 🏗️ Project Structure

```
├── src/
│   ├── main.py              # Main Actor entry point
│   ├── types.py             # Pydantic models for validation
│   ├── browser.py           # Playwright browser management
│   ├── extractor.py          # Interactive element extraction
│   ├── mcp_generator.py      # MCP tools generation
│   └── utils.py             # Utility functions
├── tests/                   # Comprehensive test suite
├── input_schema.json        # Apify input schema
├── apify.json               # Apify actor configuration
└── README.md                # This file
```

## 🔧 Development

### Code Quality

```bash
black src tests
ruff check src tests
mypy src
pytest
```

### Test-Driven Development

This project follows TDD principles:
1. Write failing tests (red)
2. Implement minimal code (green)
3. Refactor while keeping tests passing

## 📦 Dependencies

- **apify**: Apify SDK for actor development
- **playwright**: Browser automation framework
- **pydantic**: Data validation using Python type annotations
- **structlog**: Structured logging

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD)
4. Implement the feature
5. Ensure all tests pass
6. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on the repository.

---

**Made with ❤️ for the AI community**
