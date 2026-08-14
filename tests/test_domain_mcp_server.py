import os
import sys
import unittest
import unittest.mock
import asyncio

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import src.mcp_server as mcp_server


class TestDomainMCPServer(unittest.TestCase):
    """Domain test suite for Model Context Protocol (MCP) server tools, resources, and prompt handlers."""

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_01_mcp_list_tools_schema_contracts(self):
        """Verify MCP list_tools exposes standard tool schemas with required parameters.

        Preconditions: MCP server initialized.
        Invariants: handle_list_tools returns Tool objects for neuro_search, neuro_ingest, and neuro_trigger_workflow.
        Expected Outcomes: 3 tools registered with valid inputSchema property structures.
        """
        tools = self.loop.run_until_complete(mcp_server.handle_list_tools())
        self.assertGreaterEqual(len(tools), 3)
        tool_names = [t.name for t in tools]
        self.assertIn("neuro_search", tool_names)
        self.assertIn("neuro_ingest", tool_names)
        self.assertIn("neuro_trigger_workflow", tool_names)

        search_tool = next(t for t in tools if t.name == "neuro_search")
        self.assertIn("query", search_tool.inputSchema.get("required", []))

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_02_mcp_call_tool_neuro_search_success(self, mock_req):
        """Verify (Angle 16) handle_call_tool executes neuro_search and formats document score snippets.

        Preconditions: Mocked API response with 2 search results.
        Invariants: handle_call_tool formats results into TextContent blocks.
        Expected Outcomes: Returns list of TextContent containing formatted scores and filenames.
        """
        mock_req.return_value = {
            "status": "success",
            "results": [
                {"filename": "quantum.txt", "score": 0.94, "content": "Quantum superposition details."},
                {"filename": "entropy.txt", "score": 0.82, "content": "Semantic entropy boundaries."}
            ]
        }

        res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_search", {"query": "quantum computing", "limit": 5})
        )
        self.assertIsInstance(res, list)
        self.assertGreater(len(res), 0)
        self.assertIn("Search Results for 'quantum computing'", res[0].text)
        self.assertIn("[0.94]", res[0].text)
        self.assertIn("Quantum superposition", res[0].text)

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_03_mcp_call_tool_missing_arguments(self, mock_req):
        """Verify (Angle 12) handle_call_tool handles None and empty arguments without raising unhandled errors.

        Preconditions: None passed as arguments dictionary to handle_call_tool.
        Invariants: Default dictionary substitution prevents NoneType attribute errors.
        Expected Outcomes: Returns TextContent without server crash.
        """
        mock_req.return_value = {"results": []}
        res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_search", None)
        )
        self.assertIsInstance(res, list)
        self.assertIn("Search Results", res[0].text)

    def test_04_mcp_call_tool_unknown_tool_error(self):
        """Verify handle_call_tool returns clean error message on unknown tool invocation.

        Preconditions: Invalid tool name 'unregistered_tool_xyz' invoked.
        Invariants: ValueError caught internally and converted to error TextContent.
        Expected Outcomes: Output text begins with 'Error: Unknown tool'.
        """
        res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("unregistered_tool_xyz", {})
        )
        self.assertIsInstance(res, list)
        self.assertIn("Error:", res[0].text)
        self.assertIn("Unknown tool", res[0].text)

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_05_mcp_call_tool_ingest_and_workflows(self, mock_req):
        """Verify handle_call_tool dispatch for neuro_ingest and neuro_trigger_workflow.

        Preconditions: Valid URL ingest and workflow trigger arguments passed.
        Invariants: Dispatches POST to target endpoints and formats response messages.
        Expected Outcomes: Ingest and trigger return formatted confirmation TextContent blocks.
        """
        mock_req.return_value = {"status": "ok", "ingested": True}

        # URL ingest
        ingest_res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_ingest", {"url": "https://example.org/spec.pdf"})
        )
        self.assertIn("Successfully ingested", ingest_res[0].text)

        # Local path ingest notice
        local_res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_ingest", {"url": "C:/docs/vault.txt"})
        )
        self.assertIn("Local file ingestion", local_res[0].text)

        # Workflow trigger
        wf_res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_trigger_workflow", {"event_type": "manual_audit", "payload": {}})
        )
        self.assertIn("Triggered manual_audit workflow", wf_res[0].text)

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_06_mcp_list_resources_and_read_resource(self, mock_req):
        """Verify handle_list_resources and handle_read_resource for vault statistics and recent docs.

        Preconditions: Mocked health and file tree API responses.
        Invariants: Reads JSON payloads for neuro://vault/stats and neuro://vault/recent.
        Expected Outcomes: Valid serialized JSON strings returned for both resource URIs.
        """
        resources = self.loop.run_until_complete(mcp_server.handle_list_resources())
        self.assertEqual(len(resources), 2)
        uris = [str(r.uri) for r in resources]
        self.assertIn("neuro://vault/stats", uris)
        self.assertIn("neuro://vault/recent", uris)

        mock_req.return_value = {"status": "healthy", "documents_count": 42}
        stats_data = self.loop.run_until_complete(
            mcp_server.handle_read_resource("neuro://vault/stats")
        )
        self.assertIn('"documents_count": 42', stats_data)

    def test_07_mcp_list_prompts_and_get_prompt(self):
        """Verify handle_list_prompts and handle_get_prompt for document analysis and briefing prompts.

        Preconditions: Prompts 'analyze_document' and 'search_and_synthesize' registered.
        Invariants: handle_get_prompt returns populated GetPromptResult with user messages.
        Expected Outcomes: Prompt messages contain filepath and topic variables.
        """
        prompts = self.loop.run_until_complete(mcp_server.handle_list_prompts())
        self.assertEqual(len(prompts), 2)
        p_names = [p.name for p in prompts]
        self.assertIn("analyze_document", p_names)
        self.assertIn("search_and_synthesize", p_names)

        doc_prompt = self.loop.run_until_complete(
            mcp_server.handle_get_prompt("analyze_document", {"filepath": "/docs/whitepaper.md"})
        )
        self.assertIn("/docs/whitepaper.md", doc_prompt.messages[0].content.text)

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_08_angle_null_bytes_and_unbalanced_quotes_in_mcp_queries(self, mock_req):
        """Verify (Angle 1 & 2) resilience against null bytes and unbalanced quotes in MCP tool calls.

        Preconditions: Malicious queries with embedded \\x00 bytes and unbalanced quotes.
        Invariants: MCP tool call completes cleanly without serialization crashes.
        Expected Outcomes: TextContent block returned with search results.
        """
        mock_req.return_value = {"results": []}
        bad_query = "quantum \"unclosed quote \x00\x01\x02 test"
        res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_search", {"query": bad_query})
        )
        self.assertIsInstance(res, list)
        self.assertIn("Search Results", res[0].text)

    @unittest.mock.patch("src.mcp_server.make_request")
    def test_09_mcp_http_error_handling(self, mock_req):
        """Verify (Angle 25) HTTP exceptions during tool execution are formatted cleanly as TextContent.

        Preconditions: make_request raises connection error.
        Invariants: Exception caught in handle_call_tool and converted to error response.
        Expected Outcomes: Output text begins with 'Error:' without uncaught traceback crashes.
        """
        mock_req.side_effect = RuntimeError("Backend API unreachable on port 8085")
        res = self.loop.run_until_complete(
            mcp_server.handle_call_tool("neuro_search", {"query": "test"})
        )
        self.assertIsInstance(res, list)
        self.assertIn("Error:", res[0].text)
        self.assertIn("unreachable", res[0].text)

    def test_10_mcp_server_initialization_capabilities(self):
        """Verify MCP Server instance exists and exposes server name.

        Preconditions: mcp_server module imported.
        Invariants: Server instance name is 'neuro-mcp' when HAS_MCP is True.
        Expected Outcomes: server is not None and has name 'neuro-mcp'.
        """
        self.assertTrue(mcp_server.HAS_MCP)
        self.assertIsNotNone(mcp_server.server)
        self.assertEqual(mcp_server.server.name, "neuro-mcp")


if __name__ == "__main__":
    unittest.main()
