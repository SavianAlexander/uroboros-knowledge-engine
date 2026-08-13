import os
import asyncio
import httpx
try:
    from mcp.server.models import InitializationOptions
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    import mcp.server.stdio
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

if HAS_MCP:
    server = Server("neuro-mcp")
else:
    server = None

NEURO_API_URL = os.environ.get("NEURO_API_URL", "http://127.0.0.1:8085")
API_KEY = os.environ.get("NEURO_API_KEY", "")

async def make_request(method: str, endpoint: str, **kwargs):
    url = f"{NEURO_API_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))
    
    async with httpx.AsyncClient() as client:
        response = await client.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="neuro_search",
            description="Perform a semantic search against the Uroboros Knowledge Engine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "limit": {"type": "integer", "description": "Max results to return", "default": 5},
                    "search_type": {"type": "string", "enum": ["hybrid", "vector", "fts"], "default": "hybrid"}
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="neuro_ingest",
            description="Ingest a URL or file path into the Knowledge Engine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL or local file path to ingest"}
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="neuro_trigger_workflow",
            description="Trigger a workflow rule in the Knowledge Engine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {"type": "string", "description": "Event type (e.g., 'system_start', 'manual_trigger')"},
                    "payload": {"type": "object", "description": "Optional payload for the trigger"}
                },
                "required": ["event_type"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if arguments is None:
        arguments = {}

    try:
        if name == "neuro_search":
            query = arguments.get("query")
            limit = arguments.get("limit", 5)
            search_type = arguments.get("search_type", "hybrid")
            
            res = await make_request("POST", "/api/search", json={
                "query": query,
                "limit": limit,
                "search_type": search_type
            })
            
            # Format results
            text_out = f"Search Results for '{query}':\n\n"
            for doc in res.get("results", []):
                text_out += f"- [{doc.get('score', 0):.2f}] {doc.get('content', '')[:300]}...\n"
                
            return [types.TextContent(type="text", text=text_out)]
            
        if name == "neuro_ingest":
            url = arguments.get("url")
            # Determine if it's a file or url
            if url.startswith("http"):
                res = await make_request("POST", "/api/file/ingest-url", json={"url": url})
                return [types.TextContent(type="text", text=f"Successfully ingested: {url}\nResponse: {res}")]
            
            return [types.TextContent(type="text", text=f"Local file ingestion via MCP requires explicit path routing. Use HTTP ingest for: {url}")]
            
        if name == "neuro_trigger_workflow":
            event_type = arguments.get("event_type")
            payload = arguments.get("payload", {})
            
            res = await make_request("POST", "/api/workflows/trigger", json={
                "event_type": event_type,
                "payload": payload
            })
            return [types.TextContent(type="text", text=f"Triggered {event_type} workflow.\nResponse: {res}")]
            
        raise ValueError(f"Unknown tool: {name}")
            
    except httpx.HTTPStatusError as e:
        return [types.TextContent(type="text", text=f"HTTP Error: {e.response.text}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    if not HAS_MCP:
        print("MCP library (mcp) is not installed on this system.")
        return
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="neuro-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
