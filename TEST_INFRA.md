# E2E Test Infra: Adversarial AI Debate Auditor & Counter-Argument Engine

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on internal private implementation design.
- Complete coverage across 10 standard AI hallucination and sycophancy patterns (P01-P10), empirical citations, physical boundaries, and counter-proof synthesis.
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinatorial Testing + Real-World Workload Testing.

## Feature Inventory & Test Mapping
| # | Feature / Pattern | Source (Requirement) | Tier 1 (Coverage) | Tier 2 (Boundary) | Tier 3 (Pairwise) | Tier 4 (Scenario) |
|---|-------------------|----------------------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| P01 | Sycophantic Acquiescence / Echo | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P02 | Uncritical Confirmation Bias | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P03 | Phantom Academic Citations | R2 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P04 | Boundary & Physical Law Violations | R2 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P05 | False Dilemma / Forced Dichotomy | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P06 | Circular / Teleological Logic | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P07 | Quantifier Inflation / Overreach | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P08 | Premise Contradiction | R1 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| P09 | Spurious Causation (Post-Hoc) | R1 (§243) | ✓ (1 test)  | ✓ | ✓ | ✓ |
| P10 | Reification of Metaphors | R1 (§243) | ✓ (1 test)  | ✓ | ✓ | ✓ |
| F11 | Mechanism Failure & Friction | R3 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| F12 | First-Principles Counter-Proof | R3 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| F13 | Socratic Question Synthesis | R3 (§243) | ✓ (2 tests) | ✓ | ✓ | ✓ |
| F14 | Structured Markdown Reporting | Acceptance Criteria | ✓ (2 tests) | ✓ | ✓ | ✓ |
| F15 | Mathematical Scoring (FSI/SPS/GCS/HRS) | Acceptance Criteria | ✓ (2 tests) | ✓ | ✓ | ✓ |

## Test Architecture
- Test Runner: `pytest tests/test_ai_debate_auditor.py -v` (and `python -m unittest tests/test_ai_debate_auditor.py`)
- Standalone execution with zero external network dependencies (100% deterministic offline execution).
- Test Case File: `tests/test_ai_debate_auditor.py`

## 4-Tier Test Suite Structure
1. **Tier 1 — Feature Coverage (18 tests)**:
   - Covers R1 deconstruction, R2 empirical & boundary verification, and R3 counter-argument synthesis and report generation in isolation.
2. **Tier 2 — Boundary & Corner Cases (8 tests)**:
   - 25-angle matrix: empty input, null characters `\x00`, 100k+ character payload, malformed citations, Unicode NFC normalization, prompt injection defense, edge boundary constants.
3. **Tier 3 — Cross-Feature Combinations (6 tests)**:
   - Sycophancy + Phantom Citation, Physical Violation + Leading Prompt, Mathematical Invariant + Authority Appeal, Scale Extrapolation + Bare Assertion, Vault Contradiction + Local Retrieval, Multi-Round Transcript Trajectory.
4. **Tier 4 — Real-World Application Scenarios (4 tests)**:
   - Scenario 1: Perpetual Motion Free Energy Generator ($COP = 16.6$, violates 1st & 2nd Laws of Thermodynamics).
   - Scenario 2: AI Consciousness / Quantum Telepathy Fallacy (reification, definitional drift, circular reasoning).
   - Scenario 3: Macroeconomic Price Ceiling & Shortage Denial (unbounded scaling, spurious causation, mechanism erasure).
   - Scenario 4: Polynomial Deterministic TSP $O(N^2)$ Complexity Proof (mathematical boundary violation, phantom citation, proof gap).

## Acceptance Criteria
- Total tests: 36 test cases.
- Pass rate: 100% (36/36 passing with exit code 0).
- Runtime: < 3.0 seconds total.
- Memory leak & file lock safety: Enforces `reset_db_connections()` during test teardown.
