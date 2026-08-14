# Project: Adversarial AI Debate Auditor & Counter-Argument Engine

## Architecture
The Adversarial AI Debate Auditor & Counter-Argument Engine (`tools/ai_debate_auditor`) is a zero-dependency, stdlib-first verification system designed to ingest AI-generated arguments, detect structural fallacies and sycophancy biases, verify empirical claims against first-principles boundaries and indexed literature, and synthesize empirical counter-proofs with primary citations.

```
[ Input Text / Debate Transcript ]
               │
               ▼
   [ deconstructor.py (R1) ]  <───> [ patterns.py (10 Patterns) ]
       - Proposition & Claim Segmentation
       - Sycophancy & Framing Bias Detection
       - Bare Assertion Isolation
               │
               ▼
     [ verifier.py (R2) ]     <───> [ know.py / Local Vault / Physical Laws ]
       - Citation & Phantom DOI Cross-Check
       - First-Principles & Boundary Invariants
       - Empirical Grounding Verification
               │
               ▼
   [ synthesizer.py (R3) ]
       - Mechanism Failure Breakdown
       - Friction & Bottleneck Injection
       - First-Principles Counter-Proof Generation
       - Socratic Falsification Questions
               │
               ▼
     [ reporter.py ]          <───> [ models.py ]
       - Confidence & Severity Scoring (FSI, SPS, GCS, HRS)
       - Structured Markdown & JSON Report Generation
               │
               ▼
    [ cli.py / engine.py ] ──> Output Artifact / Terminal Display
```

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | Data Models & Contracts | Strongly-typed dataclasses for Claims, Findings, Checks, Reports in `models.py` | M1 | Survey |
| F02 | 10 Hallucination & Sycophancy Patterns | Formal taxonomy and regex/heuristic rules for P01-P10 in `patterns.py` | M1 | Survey |
| F03 | Argument AST & Claim Parser | Proposition segmentation, claim classification, and syntax extraction in `deconstructor.py` | M1 | R1 |
| F04 | Sycophancy & Acquiescence Detector | Detection of leading prompt echo, flattering qualifiers, and subservient consensus | M1 | R1 |
| F05 | Framing Bias & Bare Assertion Extractor | Isolation of presuppositional framing, forced dichotomies, and unsubstantiated claims | M1 | R1 |
| F06 | Citation & Phantom DOI Verifier | Regex extraction, DOI/arXiv format validation, and phantom citation detection | M2 | R2 |
| F07 | First-Principles & Physical Bounds Verifier | Hard invariant checking (Thermodynamics, Carnot, Landauer, Relativity, Complexity) | M2 | R2 |
| F08 | Local Knowledge Vault Cross-Examiner | Integration with `know.get_db()` and SQLite FTS5 for empirical claim verification | M2 | R2 |
| F09 | Empirical Grounding & Evidence Scoring | Quantitative calculation of Grounding Confidence Score (GCS) and Hallucination Risk | M2 | R2 |
| F10 | Mechanism Failure Analyzer | Step-by-step causal chain failure isolation in `synthesizer.py` | M3 | R3 |
| F11 | Friction & Real-World Bottleneck Injector | Identification of omitted friction, entropy, transaction costs, and latency | M3 | R3 |
| F12 | First-Principles Counter-Proof Generator | Synthesis of deductive refutations anchored in empirical constants and invariants | M3 | R3 |
| F13 | Socratic Falsification Question Synthesizer | Generation of sharp counter-questions exposing mechanism collapse | M3 | R3 |
| F14 | Executive Markdown Report Generator | Structured Markdown report synthesis with severity badges and citation audits in `reporter.py` | M3 | Acceptance Criteria |
| F15 | Mathematical Confidence Scorer | Computation of FSI, SPS, GCS, and HRS metrics in `reporter.py` | M3 | Acceptance Criteria |
| F16 | Interactive CLI & Engine API | Full CLI with file input, inline debate audit, and JSON/MD export in `cli.py` & `engine.py` | M3 | R1, R2, R3 |
| F17 | 4-Tier E2E Test Suite | Comprehensive unit/integration/E2E test suite covering 10 patterns in `tests/test_ai_debate_auditor.py` | E2E-Track | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Core Models, Taxonomy & Argument Deconstruction | `models.py`, `patterns.py`, `deconstructor.py` (F01-F05) | None | DONE |
| M2 | Empirical Evidence, Boundary Invariants & Citation Verifier | `verifier.py` (F06-F09) | M1 | DONE |
| M3 | Counter-Argument Synthesis, Reporting & CLI Engine | `synthesizer.py`, `reporter.py`, `engine.py`, `cli.py` (F10-F16) | M1, M2 | DONE |
| E2E | 4-Tier Opaque-Box E2E Test Suite | `tests/test_ai_debate_auditor.py` + stress harnesses (75 tests) | M1, M2, M3 | DONE |
| M_FINAL | Full E2E Pass, Stress Hardening & Forensic Integrity Audit | 100% Pass Rate across all test tiers, Reviewer Approval, Challenger Stress Pass, Clean Forensic Audit | M1, M2, M3, E2E | DONE |

## Interface Contracts
### `deconstructor.py` ↔ `verifier.py`
- `DeconstructionResult`: Dataclass containing `claims: List[Claim]`, `sycophancy_findings: List[Finding]`, `fallacy_findings: List[Finding]`, `unsubstantiated_assertions: List[str]`, `raw_text: str`.
- `Claim`: `id: str`, `text: str`, `category: ClaimCategory` (EMPIRICAL, PHYSICAL, MATHEMATICAL, DEFINITIONAL, POLICY), `citations: List[Citation]`, `confidence: float`.

### `verifier.py` ↔ `synthesizer.py`
- `VerificationResult`: Dataclass containing `verified_claims: List[ClaimVerification]`, `phantom_citations: List[CitationCheck]`, `boundary_violations: List[BoundaryViolation]`, `grounding_confidence_score: float`, `hallucination_risk_score: float`.

### `synthesizer.py` ↔ `reporter.py`
- `SynthesisResult`: Dataclass containing `counter_proofs: List[CounterProof]`, `mechanism_failures: List[MechanismFailure]`, `socratic_questions: List[str]`, `remediation_steps: List[str]`.
- `AuditReport`: Complete aggregated report object exportable to `.to_markdown()` and `.to_dict()`.

### `engine.py` / `cli.py` Public Interface
- `audit_text(text: str, context: Optional[str] = None, db_conn: Optional[Any] = None) -> AuditReport`
- `audit_file(file_path: str, output_path: Optional[str] = None) -> AuditReport`

## Code Layout
```
tools/ai_debate_auditor/
├── __init__.py           # Package exports and public API
├── models.py             # Strongly-typed data models & dataclasses
├── patterns.py           # Formal 10-pattern hallucination & sycophancy registry
├── deconstructor.py      # R1: Argument parsing, sycophancy and framing deconstruction
├── verifier.py           # R2: Empirical verification, citation and boundary checking
├── synthesizer.py        # R3: Mechanism failure, friction, and counter-argument synthesis
├── reporter.py           # Executive Markdown & JSON report generator
├── engine.py             # Main pipeline orchestrator
└── cli.py                # Standalone command-line interface

tests/
└── test_ai_debate_auditor.py  # 4-tier comprehensive E2E test suite (36+ tests)
```
