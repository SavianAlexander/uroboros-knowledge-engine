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

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "The search query"},
        "limit": {"type": "integer", "description": "Max results to return", "default": 5},
        "search_type": {"type": "string", "enum": ["hybrid", "vector", "fts"], "default": "hybrid"},
    },
    "required": ["query"],
}

INGEST_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string", "description": "URL or local file path to ingest"},
    },
    "required": ["url"],
}

TRIGGER_SCHEMA = {
    "type": "object",
    "properties": {
        "event_type": {"type": "string", "description": "Event type (e.g., 'system_start', 'manual_trigger')"},
        "payload": {"type": "object", "description": "Optional payload for the trigger"},
    },
    "required": ["event_type"],
}

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="neuro_search",
            description="Perform a semantic search against the Uroboros Knowledge Engine.",
            inputSchema=SEARCH_SCHEMA,
        ),
        types.Tool(
            name="neuro_ingest",
            description="Ingest a URL or file path into the Knowledge Engine.",
            inputSchema=INGEST_SCHEMA,
        ),
        types.Tool(
            name="neuro_trigger_workflow",
            description="Trigger a workflow rule in the Knowledge Engine.",
            inputSchema=TRIGGER_SCHEMA,
        ),
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

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri="neuro://vault/stats",
            name="Knowledge Vault Statistics",
            description="High-level indexing statistics, document count, and database size.",
            mimeType="application/json",
        ),
        types.Resource(
            uri="neuro://vault/recent",
            name="Recently Indexed Documents",
            description="List of recently ingested and modified documents in the vault.",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    if uri == "neuro://vault/stats":
        res = await make_request("GET", "/api/health")
        return json.dumps(res, indent=2)
    if uri == "neuro://vault/recent":
        res = await make_request("GET", "/api/file/tree")
        return json.dumps(res, indent=2)
    raise ValueError(f"Unknown resource URI: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="analyze_document",
            description="Analyze and extract key architectural insights from an ingested document.",
            arguments=[
                types.PromptArgument(name="filepath", description="Absolute or relative path of the file", required=True)
            ],
        ),
        types.Prompt(
            name="search_and_synthesize",
            description="Search the knowledge vault and synthesize an executive brief.",
            arguments=[
                types.PromptArgument(name="topic", description="The search topic or question", required=True)
            ],
        ),
    ]

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    args = arguments or {}
    if name == "analyze_document":
        fp = args.get("filepath", "")
        return types.GetPromptResult(
            description=f"Analyze document: {fp}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please analyze the document located at '{fp}' in the Uroboros Knowledge Vault. Extract key findings, concepts, and architectural takeaways."
                    )
                )
            ]
        )
    if name == "search_and_synthesize":
        topic = args.get("topic", "")
        return types.GetPromptResult(
            description=f"Synthesize brief on {topic}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Query the knowledge engine for '{topic}' and synthesize an executive summary with citations."
                    )
                )
            ]
        )
    raise ValueError(f"Unknown prompt name: {name}")

async def main():
    if not HAS_MCP:
        print("MCP library (mcp) is not installed on this system.")
        return
    capabilities = server.get_capabilities(
        notification_options=NotificationOptions(),
        experimental_capabilities={},
    )
    init_options = InitializationOptions(
        server_name="neuro-mcp",
        server_version="0.1.0",
        capabilities=capabilities,
    )
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_options)

if __name__ == "__main__":
    asyncio.run(main())
