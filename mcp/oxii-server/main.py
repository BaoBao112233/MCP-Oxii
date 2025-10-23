"""
OXII Smart Home MCP Server
Provides tools for controlling OXII smart home devices
"""
from __future__ import annotations

import html
import traceback
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Callable, Any
from functools import wraps

import uvicorn
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from starlette.responses import HTMLResponse, JSONResponse

# Import OXII tools
from tools.device_control import get_device_list, switch_device_control
from tools.ac_control import control_air_conditioner
from tools.one_touch_control import one_touch_control_all_devices, one_touch_control_by_type
from tools.cronjob import create_device_cronjob
from tools.room_control import room_one_touch_control

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/supervisor/mcp-tools.log', mode='a') if Path('/var/log/supervisor').exists() else logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Tool call statistics
tool_stats = {
    "total_calls": 0,
    "tool_calls": {},
    "start_time": datetime.now().isoformat()
}

def log_tool_call(tool_name: str, args: dict = None, result: Any = None, error: str = None):
    """Log tool call with details"""
    global tool_stats
    
    # Update statistics
    tool_stats["total_calls"] += 1
    if tool_name not in tool_stats["tool_calls"]:
        tool_stats["tool_calls"][tool_name] = {
            "count": 0,
            "last_called": None,
            "success_count": 0,
            "error_count": 0
        }
    
    tool_stats["tool_calls"][tool_name]["count"] += 1
    tool_stats["tool_calls"][tool_name]["last_called"] = datetime.now().isoformat()
    
    if error:
        tool_stats["tool_calls"][tool_name]["error_count"] += 1
        logger.error(
            f"🔧❌ TOOL_CALL_ERROR - Tool: {tool_name} | Args: {json.dumps(args, default=str)} | Error: {error}"
        )
    else:
        tool_stats["tool_calls"][tool_name]["success_count"] += 1
        logger.info(
            f"🔧✅ TOOL_CALL_SUCCESS - Tool: {tool_name} | Args: {json.dumps(args, default=str)} | Result: {json.dumps(result, default=str)[:200]}..."
        )

def create_logged_tool(original_func: Callable) -> Callable:
    """Create a wrapper that logs tool calls"""
    @wraps(original_func)
    async def async_wrapper(*args, **kwargs):
        tool_name = original_func.__name__
        all_args = {**dict(enumerate(args)), **kwargs}
        
        logger.info(f"🔧🚀 TOOL_CALLED - {tool_name} with args: {json.dumps(all_args, default=str)}")
        
        try:
            result = await original_func(*args, **kwargs)
            log_tool_call(tool_name, all_args, result)
            return result
        except Exception as e:
            error_msg = str(e)
            log_tool_call(tool_name, all_args, error=error_msg)
            raise
    
    @wraps(original_func)
    def sync_wrapper(*args, **kwargs):
        tool_name = original_func.__name__
        all_args = {**dict(enumerate(args)), **kwargs}
        
        logger.info(f"🔧🚀 TOOL_CALLED - {tool_name} with args: {json.dumps(all_args, default=str)}")
        
        try:
            result = original_func(*args, **kwargs)
            log_tool_call(tool_name, all_args, result)
            return result
        except Exception as e:
            error_msg = str(e)
            log_tool_call(tool_name, all_args, error=error_msg)
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(original_func):
        return async_wrapper
    else:
        return sync_wrapper


def main():
    """Main function to start the OXII MCP server"""
    logger.info("🚀 Starting OXII Smart Home MCP Server!")
    
    # Create FastMCP server instance
    mcp = FastMCP("oxii_smart_home", port=9031)
    
    load_dotenv()
    
    # Register all OXII tools with logging
    tools = [
        get_device_list,
        switch_device_control,
        control_air_conditioner,
        one_touch_control_all_devices,
        one_touch_control_by_type,
        create_device_cronjob,
        room_one_touch_control,
    ]

    # Add tools to MCP server with logging wrapper
    logged_tools = []
    for tool in tools:
        try:
            # Wrap tool with logging
            logged_tool = create_logged_tool(tool)
            # Preserve original attributes
            logged_tool.__name__ = tool.__name__
            logged_tool.__doc__ = tool.__doc__
            if hasattr(tool, '__annotations__'):
                logged_tool.__annotations__ = tool.__annotations__
            
            mcp.add_tool(logged_tool)
            logged_tools.append(logged_tool)
            logger.info(f"✅ Added tool with logging: {tool.__name__}")
        except Exception as e:
            logger.error(f"❌ Error adding tool {tool.__name__}: {e}")
            traceback.print_exc()

    logger.info(f"🔧 OXII MCP Server starting on port 9031 with {len(logged_tools)} tools")
    logger.info(f"📊 Available tools: {[tool.__name__ for tool in tools]}")

    # Build Starlette app so we can expose human-readable docs alongside SSE endpoints
    app = mcp.sse_app()
    
    # Add health check endpoint
    @app.route("/health", methods=["GET"])
    async def health_check(_: object) -> JSONResponse:
        """Health check endpoint for Docker"""
        return JSONResponse({"status": "healthy", "service": "oxii-mcp-server"})

    # Add tool statistics endpoint
    @app.route("/stats", methods=["GET"])
    async def tool_stats_endpoint(_: object) -> JSONResponse:
        """Tool usage statistics endpoint"""
        current_stats = tool_stats.copy()
        current_stats["current_time"] = datetime.now().isoformat()
        return JSONResponse(current_stats)

    # Add tool logs endpoint
    @app.route("/logs", methods=["GET"])
    async def tool_logs_endpoint(_: object) -> JSONResponse:
        """Recent tool call logs"""
        try:
            log_file = '/var/log/supervisor/mcp-tools.log'
            if Path(log_file).exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Return last 50 lines
                    recent_logs = lines[-50:] if len(lines) > 50 else lines
                    return JSONResponse({
                        "logs": [line.strip() for line in recent_logs],
                        "total_lines": len(lines)
                    })
            else:
                return JSONResponse({"logs": [], "message": "Log file not found"})
        except Exception as e:
            return JSONResponse({"error": str(e)})

    # Add reset stats endpoint
    @app.route("/stats/reset", methods=["POST"])
    async def reset_stats_endpoint(_: object) -> JSONResponse:
        """Reset tool usage statistics"""
        global tool_stats
        tool_stats = {
            "total_calls": 0,
            "tool_calls": {},
            "start_time": datetime.now().isoformat()
        }
        logger.info("📊 Tool statistics reset")
        return JSONResponse({"message": "Statistics reset successfully"})

    # Prepare README preview for the docs endpoint
    readme_path = Path(__file__).with_name("README.md")
    try:
        readme_markup = html.escape(readme_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        readme_markup = "README.md not found."

    DOC_TEMPLATE = """<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>OXII MCP Server Docs</title>
        <style>
          body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #0f172a; color: #e2e8f0; }}
          header {{ padding: 2.5rem 2rem; background: linear-gradient(135deg, #1e293b, #334155); }}
          header h1 {{ margin: 0; font-size: 2rem; letter-spacing: 0.05em; }}
          header p {{ margin: 0.5rem 0 0; color: #cbd5f5; }}
          main {{ padding: 2rem; max-width: 960px; margin: 0 auto; }}
          section {{ margin-bottom: 2rem; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 1rem; overflow: hidden; }}
          section h2 {{ margin: 0; padding: 1.25rem 1.5rem; background: rgba(148, 163, 184, 0.08); font-size: 1.2rem; }}
          .content {{ padding: 1.5rem; overflow-x: auto; }}
          pre {{ white-space: pre-wrap; word-break: break-word; background: rgba(15, 23, 42, 0.85); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(148, 163, 184, 0.15); }}
          table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
          th, td {{ border-bottom: 1px solid rgba(148, 163, 184, 0.12); padding: 0.75rem; text-align: left; }}
          th {{ color: #cbd5f5; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.08em; }}
          a {{ color: #38bdf8; text-decoration: none; }}
          footer {{ text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.9rem; }}
        </style>
      </head>
      <body>
        <header>
          <h1>OXII Smart Home MCP Server</h1>
          <p>Model Context Protocol tools for smart-home automation — browse quick docs or jump into the README.</p>
        </header>
        <main>
          <section>
            <h2>Quick Links</h2>
            <div class="content">
              <ul>
                <li><strong>SSE Endpoint:</strong> <code>http://{host}:{port}{sse_path}</code></li>
                <li><strong>Message Endpoint:</strong> <code>http://{host}:{port}{message_path}</code></li>
                <li><strong>Tool Catalogue (JSON):</strong> <a href="/docs.json">/docs.json</a></li>
                <li><strong>Health Check:</strong> <a href="/health">/health</a></li>
                <li><strong>Tool Statistics:</strong> <a href="/stats">/stats</a></li>
                <li><strong>Tool Logs:</strong> <a href="/logs">/logs</a></li>
                <li><strong>Raw README:</strong> <a href="#readme">Jump to README preview</a></li>
              </ul>
            </div>
          </section>
          <section>
            <h2>Monitoring & Logging</h2>
            <div class="content">
              <p>This server includes comprehensive tool call logging and monitoring:</p>
              <ul>
                <li><strong>Real-time Logging:</strong> All tool calls are logged with arguments and results</li>
                <li><strong>Usage Statistics:</strong> View tool usage counts at <a href="/stats">/stats</a></li>
                <li><strong>Recent Logs:</strong> See recent tool call logs at <a href="/logs">/logs</a></li>
                <li><strong>Reset Stats:</strong> POST to <code>/stats/reset</code> to reset statistics</li>
              </ul>
              <p><strong>Log Format:</strong></p>
              <pre>🔧🚀 TOOL_CALLED - tool_name with args: {{...}}
🔧✅ TOOL_CALL_SUCCESS - Tool: tool_name | Args: {{...}} | Result: {{...}}
🔧❌ TOOL_CALL_ERROR - Tool: tool_name | Args: {{...}} | Error: ...</pre>
            </div>
          </section>
          <section>
            <h2>Registered Tools</h2>
            <div class="content">
              <table>
                <thead>
                  <tr><th>Name</th><th>Description</th><th>Input schema</th></tr>
                </thead>
                <tbody>
                  {rows}
                </tbody>
              </table>
            </div>
          </section>
          <section id="readme">
            <h2>README.md</h2>
            <div class="content">
              <pre>{readme_markup}</pre>
            </div>
          </section>
        </main>
        <footer>Served by FastMCP • {tool_count} tools registered • Documentation preview generated at runtime.</footer>
      </body>
    </html>
    """

    @app.route("/", methods=["GET"])
    async def landing(_: object) -> HTMLResponse:
        return HTMLResponse(
            """<html><head><meta http-equiv='refresh' content='0; url=/docx' /></head><body></body></html>"""
        )

    @app.route("/docx", methods=["GET"])
    async def render_docs(_: object) -> HTMLResponse:
        tools_info = mcp._tool_manager.list_tools()
        host = mcp.settings.host if mcp.settings.host != "0.0.0.0" else "localhost"
        rows = "".join(
            f"<tr><td><code>{html.escape(info.name)}</code></td>"
            f"<td>{html.escape(info.description or '—')}</td>"
            f"<td><pre>{html.escape(str(info.parameters))}</pre></td></tr>"
            for info in tools_info
        )
        populated = DOC_TEMPLATE.format(
            host=host,
            port=mcp.settings.port,
            sse_path=mcp.settings.sse_path,
            message_path=mcp.settings.message_path,
            rows=rows,
            readme_markup=readme_markup,
            tool_count=len(tools_info),
        )
        return HTMLResponse(populated)

    @app.route("/docs.json", methods=["GET"])
    async def docs_json(_: object) -> JSONResponse:
        tools_payload = [
            {
                "name": info.name,
                "description": info.description,
                "parameters": info.parameters,
            }
            for info in mcp._tool_manager.list_tools()
        ]

        return JSONResponse(
            {
                "name": mcp.name,
                "transport": {
                    "type": "sse",
                    "endpoint": mcp.settings.sse_path,
                    "message_path": mcp.settings.message_path,
                    "host": mcp.settings.host,
                    "port": mcp.settings.port,
                },
                "tool_count": len(tools_payload),
                "tools": tools_payload,
            }
        )

    # Start the Starlette/uvicorn server which now also hosts documentation routes
    uvicorn.run(
        app,
        host=mcp.settings.host,
        port=mcp.settings.port,
        log_level=mcp.settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()