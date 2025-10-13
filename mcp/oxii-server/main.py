"""
OXII Smart Home MCP Server
Provides tools for controlling OXII smart home devices
"""
from __future__ import annotations

import html
import traceback
from pathlib import Path
from typing import Annotated

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


def main():
    """Main function to start the OXII MCP server"""
    print("Starting OXII Smart Home MCP Server!")
    
    # Create FastMCP server instance
    mcp = FastMCP("oxii_smart_home", port=9031)
    load_dotenv()
    
    # Register all OXII tools
    tools = [
        get_device_list,
        switch_device_control,
        control_air_conditioner,
        one_touch_control_all_devices,
        one_touch_control_by_type,
        create_device_cronjob,
        room_one_touch_control,
    ]

    # Add tools to MCP server
    for tool in tools:
        try:
            mcp.add_tool(tool)
            print(f"Added tool: {tool.__name__}")
        except Exception as e:
            print(f"Error adding tool {tool.__name__}: {e}")
            traceback.print_exc()

    print(f"OXII MCP Server starting on port 9031 with {len(tools)} tools")

    # Build Starlette app so we can expose human-readable docs alongside SSE endpoints
    app = mcp.sse_app()

    # Prepare README preview for the docs endpoint
    readme_path = Path(__file__).with_name("README.md")
    try:
        readme_markup = html.escape(readme_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        readme_markup = "README.md not found."

    DOC_TEMPLATE = """<!DOCTYPE html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
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
            <div class=\"content\">
              <ul>
                <li><strong>SSE Endpoint:</strong> <code>http://{host}:{port}{sse_path}</code></li>
                <li><strong>Message Endpoint:</strong> <code>http://{host}:{port}{message_path}</code></li>
                <li><strong>Tool Catalogue (JSON):</strong> <a href=\"/docs.json\">/docs.json</a></li>
                <li><strong>Raw README:</strong> <a href=\"#readme\">Jump to README preview</a></li>
              </ul>
            </div>
          </section>
          <section>
            <h2>Registered Tools</h2>
            <div class=\"content\">
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
          <section id=\"readme\">
            <h2>README.md</h2>
            <div class=\"content\">
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