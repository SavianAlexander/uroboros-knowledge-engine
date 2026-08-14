import os
import sys
import unittest
import tempfile
import shutil

# Ensure root directory is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.domain.code_ast_extractor import extract_code_structure, analyze_file_callgraph
from src.domain.ast_parser import parse_python_ast
from src.domain.code_diff_synthesizer import generate_refactoring_patch, generate_html_diff_view
from src.domain.code_self_refactor import analyze_and_propose_refactoring


class TestDomainCodeAST(unittest.TestCase):
    """Domain test suite for Code AST analysis, call graphs, diff synthesis, and refactoring."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_domain_code_ast_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_ast_extract_classes_and_functions(self):
        """Verify AST extraction of class hierarchies, async functions, decorators, and docstrings.

        Preconditions: Valid Python code string with class, method, and function declarations.
        Invariants: Extracted metadata contains class names, base classes, function signatures, and docstrings.
        Expected Outcomes: Correct count of classes and functions extracted with language='python'.
        """
        code = '''
"""Module docstring."""
import os
from math import sqrt

class BaseEngine:
    """Base docstring."""
    pass

class QueryEngine(BaseEngine):
    """Query engine implementation."""
    def __init__(self, name: str):
        self.name = name

    async def execute_query(self, query: str):
        """Execute asynchronous query."""
        return os.path.exists(query)
'''
        res = extract_code_structure(code, filename="query_engine.py")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["language"], "python")
        self.assertEqual(len(res["classes"]), 2)
        self.assertEqual(res["classes"][0]["name"], "BaseEngine")
        self.assertEqual(res["classes"][1]["name"], "QueryEngine")
        self.assertIn("BaseEngine", res["classes"][1]["bases"])

        fn_names = [f["name"] for f in res["functions"]]
        self.assertIn("__init__", fn_names)
        self.assertIn("execute_query", fn_names)
        async_fns = [f for f in res["functions"] if f.get("is_async")]
        self.assertEqual(len(async_fns), 1)
        self.assertEqual(async_fns[0]["name"], "execute_query")

    def test_02_ast_cyclomatic_complexity_calculation(self):
        """Verify cyclomatic complexity calculation across branching logic.

        Preconditions: Python code with multiple branching statements (if, for, while, try-except, bool ops).
        Invariants: Complexity score increments proportionally with each branching path.
        Expected Outcomes: Calculated cyclomatic complexity is greater than 5 for highly branched code.
        """
        code = '''
def complex_decision(a, b, c):
    if a > 0 and b > 0:
        for i in range(10):
            if c:
                while a < 100:
                    a += 1
            else:
                try:
                    b /= a
                except ZeroDivisionError:
                    return None
    return a + b
'''
        res = extract_code_structure(code, filename="complex.py")
        self.assertEqual(res["status"], "success")
        self.assertGreaterEqual(res["cyclomatic_complexity"], 6)

    def test_03_ast_call_graph_dependency_extraction(self):
        """Verify caller-callee relationship and graph edge extraction.

        Preconditions: Python code where functions invoke other functions and library methods.
        Invariants: Call graph logs caller, callee name, and line numbers.
        Expected Outcomes: AST analysis records internal function calls and external import edges.
        """
        code = '''
def helper():
    return 42

def process_data():
    val = helper()
    print(val)
'''
        res = extract_code_structure(code, filename="workflow.py")
        self.assertEqual(res["status"], "success")
        calls = res["calls"]
        self.assertGreater(len(calls), 0)
        callers = [c["caller"] for c in calls]
        callees = [c["callee"] for c in calls]
        self.assertIn("process_data", callers)
        self.assertIn("helper", callees)

        ast_edges = parse_python_ast(code, filename="workflow.py")
        self.assertEqual(ast_edges["status"], "success")
        self.assertIn("helper", ast_edges["functions"])
        self.assertIn("process_data", ast_edges["functions"])

    def test_04_angle_corrupt_syntax_payload_handling(self):
        """Verify (Angle 25) corrupt syntax payload handling does not crash the parser.

        Preconditions: Invalid Python syntax with unmatched brackets and illegal keywords.
        Invariants: AST parser falls back gracefully without unhandled exceptions.
        Expected Outcomes: Fallback generic extractor returns partial structural tokens.
        """
        corrupted_code = "def broken_func(a, b: return { class 999 123 !! ?? }} }}"
        res = extract_code_structure(corrupted_code, filename="broken.py")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["language"], "generic")

        ast_res = parse_python_ast(corrupted_code, filename="broken.py")
        self.assertEqual(ast_res["status"], "error")
        self.assertIn("error", ast_res)

    def test_05_angle_unbalanced_quotes_and_null_bytes(self):
        """Verify (Angle 1 & 2) resilience against unbalanced quotes and null byte injection.

        Preconditions: Code snippet containing unbalanced quotes and embedded \\x00 bytes.
        Invariants: Functions handle malformed strings cleanly without raising unhandled errors.
        Expected Outcomes: extract_code_structure completes cleanly.
        """
        malformed = "def inject_test():\n    msg = \"unbalanced quote\n    val = '\x00\x01\x02'\n"
        res = extract_code_structure(malformed, filename="malformed.py")
        self.assertIn(res["status"], ["success", "error"])

    def test_06_angle_0_byte_empty_file_handling(self):
        """Verify (Angle 4) 0-byte empty file handling returns clean empty structure.

        Preconditions: Empty string and whitespace-only inputs passed to extractors.
        Invariants: Empty structures returned with zero classes, functions, or imports.
        Expected Outcomes: status='error' or status='empty' with empty lists.
        """
        res_empty = extract_code_structure("", filename="empty.py")
        self.assertEqual(res_empty["status"], "error")
        self.assertEqual(res_empty["classes"], [])
        self.assertEqual(res_empty["functions"], [])

        res_ws = parse_python_ast("   \n\t  ", filename="ws.py")
        self.assertEqual(res_ws["status"], "empty")

    def test_07_angle_unicode_nfc_function_names(self):
        """Verify (Angle 10) multibyte UTF-8 and NFC-normalized function and class identifiers.

        Preconditions: Source code containing non-ASCII function and class names.
        Invariants: AST parses valid Unicode identifiers cleanly.
        Expected Outcomes: Unicode identifiers preserved in extracted entities.
        """
        code = '''
class 𝒞alculator:
    def calcular_métrica(self):
        return 100
'''
        res = parse_python_ast(code, filename="unicode.py")
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["classes"]), 1)
        self.assertEqual(len(res["functions"]), 1)
        self.assertEqual(res["functions"][0], "calcular_métrica")

    def test_08_code_diff_synthesizer_and_refactor(self):
        """Verify unified git diff patch generation and HTML diff viewer.

        Preconditions: Original code string and refactored modified code string.
        Invariants: unified diff accurately computes additions, deletions, and total line changes.
        Expected Outcomes: has_changes=True, patch contains standard +/- hunk markers, HTML diff is generated.
        """
        orig = "def foo():\n    x = 1\n    return x\n"
        mod = "def foo():\n    # Optimized\n    return 1\n"
        patch_info = generate_refactoring_patch(orig, mod, filepath="src/foo.py")
        self.assertEqual(patch_info["status"], "success")
        self.assertTrue(patch_info["has_changes"])
        self.assertGreater(patch_info["additions_count"], 0)
        self.assertGreater(patch_info["deletions_count"], 0)
        self.assertIn("+++ b/src/foo.py", patch_info["patch"])

        html = generate_html_diff_view(orig, mod, filepath="src/foo.py")
        self.assertIn("<table", html)
        self.assertIn("Original (src/foo.py)", html)

    def test_09_code_self_refactor_proposals(self):
        """Verify code self-refactoring proposals on long functions and broad except catches.

        Preconditions: Code snippet with long function body (>15 statements) and bare/broad except handlers.
        Invariants: Proposes decomposition and specific exception handling.
        Expected Outcomes: Proposals array contains targeted improvement suggestions.
        """
        code = '''
def oversized_monolith():
    x = 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    x += 1
    try:
        y = 10 / x
    except Exception:
        y = 0
    return y
'''
        proposals = analyze_and_propose_refactoring(code)
        self.assertEqual(proposals["status"], "success")
        self.assertTrue(proposals["refactor_needed"])
        issues = [p["issue"] for p in proposals["proposals"]]
        self.assertIn("high_cyclomatic_complexity", issues)
        self.assertIn("broad_or_bare_exception_catch", issues)

    def test_10_analyze_file_callgraph_sandbox_file(self):
        """Verify reading and analyzing callgraph from physical filesystem file.

        Preconditions: Python file written to isolated temporary sandbox directory.
        Invariants: analyze_file_callgraph opens file and parses AST structure.
        Expected Outcomes: Returns success with extracted functions and non-zero cyclomatic complexity.
        """
        file_path = os.path.join(self.test_dir, "sample_service.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("def start_service():\n    return True\n")

        res = analyze_file_callgraph(file_path)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["filename"], "sample_service.py")
        self.assertEqual(len(res["functions"]), 1)

        # Test non-existent file handling
        missing_res = analyze_file_callgraph(os.path.join(self.test_dir, "non_existent.py"))
        self.assertEqual(missing_res["status"], "error")


if __name__ == "__main__":
    unittest.main()
