"""
Main entry point for the MCP Website Tool Apify Actor.

This module orchestrates the complete production workflow:
1. Get and validate input
2. Launch browser with error handling
3. Navigate to URL (with cookies if provided)
4. Wait for networkidle
5. Extract interactive actions
6. Generate MCP JSON tools
7. Generate unique IDs
8. Save files to Key-Value Store
9. Push results to dataset
10. Full error handling with screenshots
"""

import html as html_module
import json
import uuid
from typing import Any, Dict

from apify import Actor
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.browser import BrowserManager
from src.extractor import DataExtractor
from src.mcp_generator import MCPResourceGenerator
from src.types import InputModel
from src.utils import ensure_playwright_installed, setup_logging


def generate_preview_html(
    url: str, actions: list[Dict[str, Any]], mcp_json: Dict[str, Any], run_id: str
) -> str:
    """
    Generate a beautiful preview HTML page with one-click Cursor/Claude buttons.
    
    Args:
        url: The URL that was processed.
        actions: List of extracted actions.
        mcp_json: Generated MCP tools JSON.
        run_id: Unique run identifier.
        
    Returns:
        HTML string for the preview page.
    """
    # Escape all user-controlled data to prevent XSS
    escaped_url = html_module.escape(url)
    escaped_run_id = html_module.escape(run_id)
    
    # JSON is safe in <pre> tags, but escape </pre> to prevent breaking out of the tag
    # This keeps JSON readable while preventing HTML injection
    tools_json = json.dumps(mcp_json, indent=2).replace("</pre>", "&lt;/pre&gt;")
    actions_json = json.dumps(actions, indent=2)  # Not used in HTML, but kept for consistency
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Tools Preview - {escaped_url}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            padding: 30px;
        }}
        .actions-section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }}
        .actions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .action-card {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
        }}
        .action-type {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .action-label {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        .action-selector {{
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #666;
            word-break: break-all;
        }}
        .buttons-section {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .button-group {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        .action-button {{
            flex: 1;
            min-width: 200px;
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}
        .button-cursor {{
            background: #0070f3;
            color: white;
        }}
        .button-cursor:hover {{
            background: #0051cc;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,112,243,0.4);
        }}
        .button-claude {{
            background: #ff6b35;
            color: white;
        }}
        .button-claude:hover {{
            background: #e55a2b;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255,107,53,0.4);
        }}
        .json-section {{
            margin-top: 30px;
        }}
        .json-container {{
            background: #1e1e1e;
            color: #d4d4d4;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        .stat {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            flex: 1;
            min-width: 150px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MCP Tools Generated</h1>
            <p>{escaped_url}</p>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Tools Generated</div>
                    <div class="stat-value">{len(mcp_json.get('tools', []))}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Actions Found</div>
                    <div class="stat-value">{len(actions)}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Run ID</div>
                    <div class="stat-value" style="font-size: 16px;">{escaped_run_id}</div>
                </div>
            </div>
            
            <div class="buttons-section">
                <div class="section-title">🚀 Quick Actions</div>
                <div class="button-group">
                    <a href="https://cursor.sh" target="_blank" class="action-button button-cursor">
                        📝 Open in Cursor
                    </a>
                    <a href="https://claude.ai" target="_blank" class="action-button button-claude">
                        🤖 Open in Claude
                    </a>
                </div>
            </div>
            
            <div class="actions-section">
                <div class="section-title">📋 Extracted Actions</div>
                <div class="actions-grid">
"""
    
    for action in actions:
        # Escape all user-controlled action data to prevent XSS
        action_type = html_module.escape(action.get('type', 'unknown'))
        label = html_module.escape(action.get('label', 'Unknown'))
        selector = html_module.escape(action.get('selector', ''))
        html += f"""
                    <div class="action-card">
                        <span class="action-type">{action_type}</span>
                        <div class="action-label">{label}</div>
                        <div class="action-selector">{selector}</div>
                    </div>
"""
    
    html += f"""
                </div>
            </div>
            
            <div class="json-section">
                <div class="section-title">🔧 MCP Tools JSON</div>
                <div class="json-container">
                    <pre>{tools_json}</pre>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html


def main() -> None:
    """
    Main Actor function - Production-ready workflow.
    
    Complete production flow:
    1. Get and validate input
    2. Launch browser with error handling
    3. Navigate to URL (with cookies if provided)
    4. Wait for networkidle
    5. Extract interactive actions
    6. Generate MCP JSON tools
    7. Generate unique IDs
    8. Save files to Key-Value Store
    9. Push results to dataset
    10. Full error handling with screenshots
    """
    logger = setup_logging()
    run_id = str(uuid.uuid4())[:8]
    logger.info(event="actor_started", message="Starting MCP Website Tool Actor", run_id=run_id)
    
    browser_manager = None
    page = None
    
    try:
        # 1. Ensure Playwright is installed
        logger.info(event="playwright_check", message="Ensuring Playwright is installed")
        ensure_playwright_installed()
        
        # 2. Get and validate input
        logger.info(event="input_validation", message="Getting and validating input")
        actor_input = Actor.get_input()
        config = InputModel(**actor_input)
        logger.info(
            event="input_validated",
            message="Input validated",
            url=str(config.url),
            max_actions=config.maxActions,
            remove_banners=config.removeBanners,
        )
        
        # 3. Initialize components
        extractor = DataExtractor(config)
        mcp_generator = MCPResourceGenerator(config)
        
        # 4. Launch browser with error handling
        logger.info(event="browser_launch", message="Launching browser")
        browser_manager = BrowserManager(config)
        
        # 5. Navigate to URL with error handling
        url = str(config.url)
        logger.info(event="navigation_start", message="Navigating to URL", url=url)
        
        with browser_manager.safe_page() as page:
            # Navigate to page
            page.goto(url, wait_until="networkidle", timeout=30000)
            logger.info(event="page_loaded", message="Page loaded", url=url)
            
            # 6. Extract interactive actions
            logger.info(event="action_extraction_start", message="Extracting interactive actions")
            actions = extractor.extract_interactive_actions(page)
            logger.info(
                event="action_extraction_complete",
                message="Actions extracted",
                count=len(actions),
            )
            
            # 7. Generate MCP JSON tools
            logger.info(event="mcp_generation_start", message="Generating MCP tools JSON")
            mcp_json = mcp_generator.generate_tools_from_actions(actions)
            logger.info(
                event="mcp_generation_complete",
                message="MCP tools generated",
                tool_count=len(mcp_json.get("tools", [])),
            )
            
            # 8. Take screenshot
            logger.info(event="screenshot_capture", message="Taking screenshot")
            screenshot_data = page.screenshot(full_page=True)
            
            # 9. Generate preview HTML
            logger.info(event="preview_generation", message="Generating preview HTML")
            preview_html = generate_preview_html(url, actions, mcp_json, run_id)
            
            # 10. Save files to Key-Value Store
            logger.info(event="kv_store_save", message="Saving files to Key-Value Store")
            key_value_store = Actor.open_key_value_store()
            
            # Save MCP JSON
            mcp_key = f"mcp-{run_id}.json"
            key_value_store.set_value(mcp_key, mcp_json)
            logger.info(event="mcp_json_saved", message="MCP JSON saved", key=mcp_key)
            
            # Save preview HTML
            preview_key = f"preview-{run_id}.html"
            key_value_store.set_value(preview_key, preview_html, content_type="text/html")
            logger.info(event="preview_saved", message="Preview HTML saved", key=preview_key)
            
            # Save screenshot
            screenshot_key = f"screenshot-{run_id}.png"
            key_value_store.set_value(screenshot_key, screenshot_data, content_type="image/png")
            logger.info(event="screenshot_saved", message="Screenshot saved", key=screenshot_key)
            
            # Get public URLs
            store_id = key_value_store.store_id
            base_url = f"https://api.apify.com/v2/key-value-stores/{store_id}/records"
            
            mcp_json_url = f"{base_url}/{mcp_key}"
            preview_url = f"{base_url}/{preview_key}"
            screenshot_url = f"{base_url}/{screenshot_key}"
            
            logger.info(
                event="urls_generated",
                message="Public URLs generated",
                mcp_url=mcp_json_url,
                preview_url=preview_url,
                screenshot_url=screenshot_url,
            )
            
            # 11. Push data to dataset
            tool_count = len(mcp_json.get("tools", []))
            result_data = {
                "mcpJsonUrl": mcp_json_url,
                "previewUrl": preview_url,
                "screenshotUrl": screenshot_url,
                "toolCount": tool_count,
                "url": url,
                "runId": run_id,
                "actionsCount": len(actions),
            }
            
            Actor.push_data(result_data)
            logger.info(
                event="data_pushed",
                message="Results pushed to dataset",
                tool_count=tool_count,
            )
            
            logger.info(
                event="actor_completed",
                message="Actor completed successfully",
                run_id=run_id,
                tool_count=tool_count,
                url=url,
            )
    
    except PlaywrightTimeoutError as e:
        logger.error(
            event="navigation_timeout",
            message="Navigation timeout",
            error=str(e),
            url=url if 'url' in locals() else "unknown",
        )
        # Error screenshot is already handled by safe_page context manager
        raise
    
    except Exception as e:
        logger.error(
            event="actor_error",
            message="Actor failed with error",
            error=str(e),
            error_type=type(e).__name__,
            url=url if 'url' in locals() else "unknown",
        )
        # Error screenshot is already handled by safe_page context manager
        raise
    
    finally:
        # Always close browser
        if browser_manager:
            try:
                browser_manager.close()
                logger.info(event="browser_closed", message="Browser closed")
            except Exception as e:
                logger.warning(
                    event="browser_close_error",
                    message="Error closing browser",
                    error=str(e),
                )


# Apify Actor entry point
if __name__ == "__main__":
    # SDK v2 sync pattern
    with Actor:
        main()
