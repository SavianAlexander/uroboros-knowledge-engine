"""
Domain 29: Frontier Reasoning & Cognitive Scaffolding Architecture Test Suite
Verifies:
1. Execution-Based Verification Gate (AST syntax validation & error detection).
2. Tree-of-Thoughts (ToT) Candidate Heuristic Scoring and Ranking.
3. Chain-of-Verification (CoVe) 3-Phase Reflection System Prompt Construction.
4. Model Router Reasoning Complexity Calculation & Frontier Escalation Gate.
5. Golden Reasoning Trace Retrieval from Knowledge Vault.
6. Action Parser & Dispatcher for Frontier Actions (verify, golden_traces).
"""

import unittest
import os
import sys

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

scripts_dir = os.path.join(root_dir, ".agents", "skills", "neuro-copilot", "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from src.core.model_router import calculate_reasoning_complexity, route_prompt_model
import react_agent_bridge


class TestDomain29FrontierReasoning(unittest.TestCase):

    def test_01_execution_verifier_ast_valid(self):
        """Verify execution verifier approves valid Python functions and classes."""
        valid_code = (
            "class MemoryPool:\n"
            "    def __init__(self, size: int = 1024):\n"
            "        self.size = size\n\n"
            "    def allocate(self) -> bytes:\n"
            "        return b'\\x00' * self.size\n"
        )
        res = react_agent_bridge.tool_verify_solution(valid_code)
        self.assertIn("[VERIFICATION PASSED: AST VALID]", res)
        self.assertIn("MemoryPool", res)
        self.assertIn("allocate", res)

    def test_02_execution_verifier_syntax_error(self):
        """Verify execution verifier catches syntax errors with line/column context."""
        broken_code = "def invalid_syntax(x, y:\n    return x + y"
        res = react_agent_bridge.tool_verify_solution(broken_code)
        self.assertIn("[VERIFICATION FAILED: SYNTAX ERROR]", res)
        self.assertIn("Line", res)

    def test_03_tree_of_thoughts_candidate_scoring(self):
        """Verify ToT scoring ranks deductive actions and AST lookups above premature finish."""
        # AST query candidate
        score_ast = react_agent_bridge.score_candidate_thought_action(
            thought="Look up definition and callers in AST graph",
            action='[ACTION: ast_query symbol="get_db"]',
            task="Investigate database connection leak in know.py",
            step_num=1
        )

        # Verification candidate
        score_verify = react_agent_bridge.score_candidate_thought_action(
            thought="Verify syntax of candidate patch",
            action='[ACTION: verify code="def fix(): pass"]',
            task="Investigate database connection leak in know.py",
            step_num=2
        )

        # Premature finish candidate on step 1
        score_premature_finish = react_agent_bridge.score_candidate_thought_action(
            thought="I guess it is done",
            action='[ACTION: finish answer="Done"]',
            task="Investigate database connection leak in know.py",
            step_num=1
        )

        self.assertGreater(score_ast, score_premature_finish)
        self.assertGreater(score_verify, score_premature_finish)
        self.assertGreaterEqual(score_ast, 0.70)

    def test_04_chain_of_verification_system_prompt(self):
        """Verify CoVe system prompt includes all 3 mandatory reflection phases."""
        prompt_with_cove = react_agent_bridge.build_system_instruction(enable_cove=True)
        self.assertIn("CHAIN-OF-VERIFICATION (CoVe) PROTOCOL", prompt_with_cove)
        self.assertIn("Phase 1 (Premise)", prompt_with_cove)
        self.assertIn("Phase 2 (Edge Cases)", prompt_with_cove)
        self.assertIn("Phase 3 (Ponytail)", prompt_with_cove)

        prompt_without_cove = react_agent_bridge.build_system_instruction(enable_cove=False)
        self.assertNotIn("CHAIN-OF-VERIFICATION (CoVe) PROTOCOL", prompt_without_cove)

    def test_05_model_router_complexity_calculation(self):
        """Verify model router computes complexity scores and identifies frontier escalation tasks."""
        # Low complexity micro task
        meta_low = calculate_reasoning_complexity("expand query: neural", task_type="micro")
        self.assertLess(meta_low["complexity_score"], 0.40)
        self.assertFalse(meta_low["frontier_escalation_eligible"])
        self.assertEqual(meta_low["confidence_tier"], "local_optimal")

        # High complexity multi-architecture reasoning task
        meta_high = calculate_reasoning_complexity(
            "Perform formal verification and prove concurrency race condition freedom across monolithic refactor",
            task_type="proof"
        )
        self.assertGreaterEqual(meta_high["complexity_score"], 0.70)
        self.assertTrue(meta_high["frontier_escalation_eligible"])
        self.assertIn(meta_high["suggested_frontier_engine"], ["gemini-3.7-flash", "claude-3.7-sonnet"])
        self.assertEqual(meta_high["confidence_tier"], "frontier_recommended")

    def test_06_golden_reasoning_traces_retrieval(self):
        """Verify golden reasoning traces return relevant architectural exemplars."""
        res_sqlite = react_agent_bridge.retrieve_golden_traces("sqlite connection pool locks")
        self.assertIn("SQLITE EXEMPLAR", res_sqlite)
        self.assertIn("WAL", res_sqlite)

        res_ast = react_agent_bridge.retrieve_golden_traces("AST call graph symbol indexing")
        self.assertIn("AST EXEMPLAR", res_ast)

        res_rag = react_agent_bridge.retrieve_golden_traces("hybrid RAG vector MMR")
        self.assertIn("RAG EXEMPLAR", res_rag)

    def test_07_action_parser_dispatch(self):
        """Verify action parser routes verify and golden_traces actions correctly."""
        obs_v, fin_v = react_agent_bridge.execute_parsed_action('[ACTION: verify code="def check(): return 42"]')
        self.assertFalse(fin_v)
        self.assertIn("[VERIFICATION PASSED: AST VALID]", obs_v)

        obs_g, fin_g = react_agent_bridge.execute_parsed_action('[ACTION: golden_traces topic="sqlite"]')
        self.assertFalse(fin_g)
        self.assertIn("SQLITE EXEMPLAR", obs_g)

    def test_08_reasoning_budget_and_scratchpad_parsing(self):
        """Verify adaptive reasoning budget tiers and structured tagged thinking scratchpads."""
        from frontier_reasoning_bridge import ReasoningBudget, ReasoningScratchpad

        # 1. Budget estimation
        b_low = ReasoningBudget.estimate_budget_from_prompt("quick check", complexity_score=0.2)
        self.assertEqual(b_low.tier, "low")
        self.assertEqual(b_low.max_thinking_tokens, 256)

        b_ext = ReasoningBudget.estimate_budget_from_prompt("prove deadlock-free distributed consensus", complexity_score=0.9)
        self.assertEqual(b_ext.tier, "extended")
        self.assertEqual(b_ext.max_thinking_tokens, 8192)

        # 2. Tagged scratchpad parsing
        raw_output = (
            "<thought> Deconstruct ring buffer pointer arithmetic </thought>\n"
            "<lemma> Modulo operation on powers of 2 optimizes to bitwise AND </lemma>\n"
            "<invariant_check> Buffer capacity is always 2^N </invariant_check>\n"
            "def ring_buffer_size(): return 1024"
        )
        state = ReasoningScratchpad.parse(raw_output)
        self.assertEqual(len(state.thoughts), 1)
        self.assertEqual(len(state.lemmas), 1)
        self.assertEqual(len(state.invariants), 1)
        self.assertEqual(state.final_output, "def ring_buffer_size(): return 1024")

        # 3. Invariant validation
        valid, issues = ReasoningScratchpad.validate_invariants(state, ["bitwise AND", "2^N"])
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)

    def test_09_consensus_debate_proposer_redteam_arbiter(self):
        """Verify multi-agent Proposer / Red-Team Critic / Arbiter consensus debate engine."""
        from frontier_reasoning_bridge import ConsensusArbiter

        # Mock debate round
        round_res = ConsensusArbiter.run_debate("Design lock-free queue in Python")
        self.assertTrue(round_res.passed)
        self.assertGreaterEqual(round_res.consensus_score, 0.70)
        self.assertIn("Proposer", round_res.proposer_output)
        self.assertIn("CLEAN_VERIFIED", round_res.critic_critique)
        self.assertIn("Arbiter", round_res.arbiter_verdict)

        # Score parser
        score_high = ConsensusArbiter.parse_consensus_score("Solution verified. [CONSENSUS_SCORE: 0.98]")
        self.assertAlmostEqual(score_high, 0.98)

    def test_10_graph_of_thoughts_dag_execution(self):
        """Verify non-linear Graph-of-Thoughts DAG topological execution via stdlib graphlib."""
        from frontier_reasoning_bridge import GraphOfThoughtsEngine

        got = GraphOfThoughtsEngine("Architect zero-dependency vector cache")
        got.build_standard_decomposition()
        self.assertEqual(len(got.nodes), 6)

        # Execute DAG
        nodes = got.execute_dag()
        for nid in ["root", "branch_arch", "branch_edge", "aggregate_solution", "refine_solution", "final_conclusion"]:
            self.assertTrue(nodes[nid].completed)
            self.assertGreater(len(nodes[nid].result), 0)

        final_res = got.get_final_result()
        self.assertIn("Result for task", final_res)

    def test_11_ephemeral_test_sandbox_execution(self):
        """Verify EphemeralTestSandbox executes code in isolated subprocess and detects errors."""
        from frontier_reasoning_bridge import EphemeralTestSandbox

        # Valid execution
        valid_code = "def multiply(a: int, b: int) -> int:\n    return a * b\nassert multiply(3, 4) == 12\n"
        res_ok = EphemeralTestSandbox.execute_code_sandboxed(valid_code)
        self.assertTrue(res_ok["passed"])
        self.assertEqual(res_ok["returncode"], 0)

        # Syntax error detection
        bad_syntax = "def broken(:\n    pass"
        res_syn = EphemeralTestSandbox.execute_code_sandboxed(bad_syntax)
        self.assertFalse(res_syn["passed"])
        self.assertEqual(res_syn["error_type"], "SyntaxError")

        # Test synthesis
        test_suite = EphemeralTestSandbox.synthesize_test_suite("def hello(): return 'world'")
        self.assertIn("class EphemeralVerificationTest", test_suite)
        self.assertIn("TextTestRunner", test_suite)

    def test_12_react_agent_bridge_phase2_actions(self):
        """Verify action parser routes debate, got_solve, and sandbox_test actions."""
        obs_d, fin_d = react_agent_bridge.execute_parsed_action('[ACTION: debate prompt="Design lock-free stack"]')
        self.assertFalse(fin_d)
        self.assertIn("CONSENSUS DEBATE", obs_d)

        obs_g, fin_g = react_agent_bridge.execute_parsed_action('[ACTION: got_solve goal="Design distributed ring"]')
        self.assertFalse(fin_g)
        self.assertIn("GRAPH-OF-THOUGHTS DAG COMPLETED", obs_g)

        obs_s, fin_s = react_agent_bridge.execute_parsed_action('[ACTION: sandbox_test code="def add(x, y): return x + y\nassert add(1, 2) == 3"]')
        self.assertFalse(fin_s)
        self.assertIn("SANDBOX VERIFICATION PASSED", obs_s)


if __name__ == "__main__":
    unittest.main()
