# ADK ↔ MCP Integration Reference

The Model Context Protocol (MCP) is an open standard for LLMs to communicate with external apps, data sources, and tools. It follows a **client-server architecture**: servers expose resources, prompts, and tools; clients consume them. ADK supports both directions.

---

## Pattern A — ADK Agent as MCP Client

Use an external MCP server's tools inside an ADK agent via `McpToolset`.

### Local stdio MCP server (e.g., filesystem)

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='my_agent',
    instruction='Help the user.',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=["-y", "@modelcontextprotocol/server-filesystem", "/absolute/path/to/folder"],
                )
            ),
            tool_filter=['list_directory', 'read_file']  # optional: restrict which tools are exposed
        )
    ],
)
```

Notes:
- `command`/`args` launch the MCP server as a subprocess over stdio.
- Use an **absolute path** for the folder the filesystem server can access.
- `tool_filter` is optional — omit it to expose all tools the server offers.

### Remote HTTP MCP server (e.g., Google Maps Grounding Lite)

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

root_agent = LlmAgent(
    model='gemini-flash-latest',
    name='travel_planner_agent',
    tools=[
        McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mapstools.googleapis.com/mcp",
                headers={
                    "X-Goog-Api-Key": "YOUR_MAPS_API_KEY",
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
        )
    ]
)
```

Notes:
- Use `StreamableHTTPConnectionParams` for remote HTTP MCP endpoints.
- Pass auth (API keys) and content-negotiation via `headers`.
- Keep secrets out of source — load `YOUR_MAPS_API_KEY` from an env var / `.env`.

---

## Pattern B — Expose ADK Tools as an MCP Server

Serve ADK tools over MCP so any MCP client can call them.

```python
# my_adk_mcp_server.py
import asyncio, json
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.load_web_page import load_web_page
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type

adk_tool = FunctionTool(load_web_page)
app = Server("adk-tool-exposing-mcp-server")

@app.list_tools()
async def list_mcp_tools():
    return [adk_to_mcp_tool_type(adk_tool)]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict):
    if name == adk_tool.name:
        result = await adk_tool.run_async(args=arguments, tool_context=None)
        return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]

async def run():
    async with mcp.server.stdio.stdio_server() as (r, w):
        await app.run(r, w, InitializationOptions(
            server_name=app.name, server_version="0.1.0",
            capabilities=app.get_capabilities(
                notification_options=NotificationOptions(), experimental_capabilities={}
            )
        ))

if __name__ == "__main__":
    asyncio.run(run())
```

Notes:
- `adk_to_mcp_tool_type` converts an ADK tool's schema into an MCP tool definition for `list_tools`.
- In `call_tool`, dispatch by `name` and run the matching ADK tool with `run_async`.
- Return results as MCP `TextContent`; serialize structured data with `json.dumps`.
- This example serves over **stdio**; a client (Pattern A stdio config) can launch it with `command="python"`, `args=["my_adk_mcp_server.py"]`.
