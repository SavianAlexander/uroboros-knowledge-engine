# E2E Test Infra: Empirically True Grounded Retrieval & Epistemic Invariant Engine

## Test Philosophy
- Opaque-box, requirement-driven. No dependency on internal module shortcuts.
- Systematic 4-tier methodology: Category-Partition, Boundary Value Analysis, Pairwise Combinatorial, Real-World Workload.

## Feature Inventory & Test Matrix
| # | Feature | Requirement | Tier 1 (>=5) | Tier 2 (>=5) | Tier 3 (Pairwise) | Tier 4 (Scenario) |
|---|---------|-------------|:------------:|:------------:|:-----------------:|:-----------------:|
| 1 | F1: Epistemic Evidentiary Tiering | R1 | 5 | 5 | ✓ | ✓ |
| 2 | F2: Authority-Weighted Hybrid RRF | R1 | 5 | 5 | ✓ | ✓ |
| 3 | F3: Temporal Validity & Superseding | R2 | 5 | 5 | ✓ | ✓ |
| 4 | F4: Exponential Staleness Decay | R2 | 5 | 5 | ✓ | ✓ |
| 5 | F5: Dense Propositional Decomposition | R3 | 5 | 5 | ✓ | ✓ |
| 6 | F6: Consensus & Contradiction Matrix | R4 | 5 | 5 | ✓ | ✓ |
| 7 | F7: Optical Fiber Latency Bounds | R5 | 5 | 5 | ✓ | ✓ |
| 8 | F8: Universal Scalability Law (USL) | R5 | 5 | 5 | ✓ | ✓ |
| 9 | F9: CAP / PACELC Invariant Bounds | R5 | 5 | 5 | ✓ | ✓ |
| 10 | F10: Carnot & Landauer Thermodynamic Limits | R5 | 5 | 5 | ✓ | ✓ |
| 11 | F11: Shannon Channel Capacity Limit | R5 | 5 | 5 | ✓ | ✓ |
| 12 | F12: Grounding Scorecard & Refusal Gate | R6 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test Suite Runner: `pytest -q tests/test_grounded_retrieval.py tests/test_grounded_retrieval_e2e.py`
- Deterministic assertions, zero network/socket dependencies, robust fixtures.

## Real-World Application Scenarios (Tier 4)
1. High-frequency distributed database replication across transatlantic fiber cables (Optical bounds + PACELC + USL scaling).
2. Superseded engineering standard comparison (RFC 2616 vs RFC 7230 vs RFC 9110 with temporal decay and contradiction resolution).
3. Nanoscale computing thermal dissipation evaluation (Landauer erasure limit at cryogenic vs ambient temperatures).
4. Deep-space satellite transmission link capacity verification (Shannon-Hartley channel limit with low SNR).
5. Multi-source contradictory medical / statutory claim adjudication (Authority dominance, cross-document consensus, refusal gate).
6. High-concurrency cluster throughput benchmark verification (USL retrograde concurrency contention and coherency penalty).
