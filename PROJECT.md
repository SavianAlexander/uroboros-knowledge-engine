# Project: Empirically True, Real-World Grounded Retrieval & Epistemic Invariant Engine

## Architecture
Decoupled Clean Architecture in Python (stdlib-first, zero unneeded dependencies):
- `src/domain/grounded_retrieval_engine.py`: Primary domain coordinator & modular sub-components for R1-R6.
- `src/domain/`:
  - `epistemic_tiering.py`: Tier classification & authority weighting.
  - `temporal_validity.py`: Date parsing, superseding/amendment detection & exponential staleness decay.
  - `dense_propositions.py`: Atomic proposition deconstruction with breadcrumb scopes (`Document > Section > Subsection > Scope`).
  - `consensus_matrix.py`: Cross-document NLI entailment, consensus boosting, and contradiction resolution hierarchy.
  - `boundary_invariants.py`: First-principles physical and mathematical boundary guards (Speed of Light, USL, CAP/PACELC, Carnot/Landauer, Shannon).
  - `grounding_scorecard.py`: Composite grounding confidence scoring, invariant veto, and >= 0.65 refusal gate with diagnostic reporting.
- `src/app/routers/grounded_retrieval.py`: FastAPI endpoint integration.
- `tests/`: Unit, integration, and E2E verification suites (`tests/test_grounded_retrieval.py`, `tests/test_grounded_retrieval_e2e.py`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1: Epistemic Evidentiary Tier Classifier | Authority coefficients: Tier 1 (1.00), Tier 2 (0.85), Tier 3 (0.70), Tier 4 (0.35) | M1 | ORIGINAL_REQUEST §R1 |
| 2 | F2: Authority-Weighted Hybrid RRF Fusion | Mathematical RRF score weighting across lexical FTS5 & dense vector search with temporal scalars | M1 | ORIGINAL_REQUEST §R1 |
| 3 | F3: Temporal Validity & Superseding Detection | Effective date range extraction & superseding/amendment marker detection with status tagging | M1 | ORIGINAL_REQUEST §R2 |
| 4 | F4: Exponential Staleness Decay | Domain half-life exponential decay curves and hard caps for superseded documents | M1 | ORIGINAL_REQUEST §R2 |
| 5 | F5: Dense Propositional Decomposition | Atomic proposition extraction preserving hierarchical breadcrumb scopes | M2 | ORIGINAL_REQUEST §R3 |
| 6 | F6: Cross-Document Consensus & Contradiction Matrix | Pairwise NLI entailment, consensus confidence boost, and 4-tier contradiction resolution hierarchy | M3 | ORIGINAL_REQUEST §R4 |
| 7 | F7: Optical Fiber Latency Invariant Guard | Speed of light propagation lower bounds ($c_{\text{fiber}} = c/n$, Haversine geodesic check) | M4 | ORIGINAL_REQUEST §R5 |
| 8 | F8: Universal Scalability Law (USL) Guard | Gunther USL concurrency contention ($\alpha$), coherency ($\beta$), retrograde peak & superlinear veto | M4 | ORIGINAL_REQUEST §R5 |
| 9 | F9: CAP & PACELC Invariant Guard | Impossibility of strong consistency + zero-latency availability under partition, quorum bounds | M4 | ORIGINAL_REQUEST §R5 |
| 10 | F10: Carnot & Landauer Thermodynamic Guard | Carnot efficiency upper bound ($\eta \le 1 - T_c/T_h$) & Landauer erasure minimum energy ($E \ge k_B T \ln 2$) | M4 | ORIGINAL_REQUEST §R5 |
| 11 | F11: Shannon Channel Capacity Guard | Shannon-Hartley capacity ceiling ($C = B \log_2(1+\text{SNR})$) & spectral efficiency limits | M4 | ORIGINAL_REQUEST §R5 |
| 12 | F12: Grounding Scorecard & Refusal Gate | Composite confidence score, binary invariant veto multiplier, and $\ge 0.65$ threshold refusal gate | M5 | ORIGINAL_REQUEST §R6 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Epistemic Tiering, Temporal Validity & Grounded RRF | F1, F2, F3, F4 | none | DONE |
| M2 | Dense Propositional Decomposition & Breadcrumb Scoping | F5 | M1 | DONE |
| M3 | Cross-Document Consensus & Contradiction Resolution Matrix | F6 | M1 | DONE |
| M4 | Physical, Mathematical & Computational Boundary Invariant Guards | F7, F8, F9, F10, F11 | none | DONE |
| M5 | Grounding Scorecard, Refusal Gate & Engine Integration | F12, Full Engine Integration | M1, M2, M3, M4 | DONE |
| M-E2E | Opaque-Box E2E Test Suite Creation | Test infra & Tiers 1-4 tests covering all 12 features | none | DONE |
| M6 | Final Verification & Adversarial Coverage Hardening | 100% E2E Pass + Tier 5 Adversarial Hardening | M5, M-E2E | DONE |

## Interface Contracts

### `src/domain/epistemic_tiering.py`
```python
def classify_source_epistemic_tier(source_metadata: dict | str) -> tuple[int, float]:
    """Returns (tier_int, authority_weight: float) where tier in 1..4."""
    ...

def compute_authority_weighted_rrf(
    lexical_ranks: list[dict],
    dense_ranks: list[dict],
    k: int = 60,
    intent_weights: dict | None = None
) -> list[dict]:
    """Computes RRF scores weighted by epistemic authority and temporal validity."""
    ...
```

### `src/domain/temporal_validity.py`
```python
def extract_temporal_metadata(text: str, metadata: dict | None = None) -> dict:
    """Extracts creation date, effective date range, and superseding markers."""
    ...

def compute_temporal_decay(
    document_date: datetime | str | None,
    domain: str = "general",
    status: str = "ACTIVE",
    half_life_days: float | None = None
) -> float:
    """Returns decay multiplier in (0.0, 1.0]. Hard cap <= 0.35 if superseded."""
    ...
```

### `src/domain/dense_propositions.py`
```python
def decompose_into_propositions(text: str, document_title: str = "") -> list[dict]:
    """Decomposes text into atomic factual propositions with breadcrumb scope:
    [{'id': ..., 'proposition': ..., 'breadcrumb': 'Doc > Sec > Sub > Scope', ...}]"""
    ...
```

### `src/domain/consensus_matrix.py`
```python
def evaluate_cross_document_consensus(passages: list[dict]) -> dict:
    """Evaluates NLI entailment, calculates consensus boost, detects contradictions,
    and applies 4-tier resolution hierarchy.
    Returns: {'consensus_score': float, 'contradictions': list, 'resolved_claims': list}"""
    ...
```

### `src/domain/boundary_invariants.py`
```python
def verify_optical_latency_invariant(distance_km: float, claimed_latency_ms: float, n_refractive: float = 1.4682) -> tuple[bool, str]: ...
def verify_usl_invariant(concurrency: int, throughput: float, gamma: float, alpha: float, beta: float) -> tuple[bool, str]: ...
def verify_cap_pacelc_invariant(claim: dict) -> tuple[bool, str]: ...
def verify_carnot_landauer_invariant(claim: dict) -> tuple[bool, str]: ...
def verify_shannon_capacity_invariant(bandwidth_hz: float, snr_linear: float, claimed_bps: float) -> tuple[bool, str]: ...
def evaluate_all_boundary_invariants(claims_or_text: str | list[dict]) -> dict:
    """Evaluates all physical invariants. Returns {'valid': bool, 'violations': list[dict], 'multiplier': 1.0 or 0.0}"""
    ...
```

### `src/domain/grounded_retrieval_engine.py`
```python
class GroundedRetrievalEngine:
    def evaluate_grounding(self, query: str, candidate_passages: list[dict], generated_claim: str = "") -> dict:
        """Calculates composite Grounding Confidence Score (0-100%) and returns refusal verdict
        if score < 0.65 with structured missing knowledge gap diagnostics."""
        ...
```

## Code Layout
- Clean Architecture: stdlib-first, modular sub-components in `src/domain/`, unified in `src/domain/grounded_retrieval_engine.py`.
- Tests: `tests/test_grounded_retrieval.py`, `tests/test_grounded_retrieval_e2e.py`.
