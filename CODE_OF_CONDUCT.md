# Uroboros Knowledge Engine Code of Conduct & Technical Governance Framework

## 1. Our Pledge

We as contributors, maintainers, security auditors, and community leaders of the **Uroboros Knowledge Engine (Neuro Alexander)** project pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, caste, color, religion, or sexual identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming, diverse, inclusive, air-gapped, secure, and technically rigorous community.

---

## 2. Our Standards

### 2.1 Positive Behaviors
Examples of behavior that contributes to a positive environment for our project include:
- Demonstrating empathy, kindness, and respect toward all community members, human collaborators, and autonomous AI agents.
- Being respectful of differing architectural viewpoints, performance trade-offs, and technical paradigms.
- Giving and gracefully accepting constructive peer-review feedback.
- Accepting responsibility and apologizing promptly to those affected by engineering mistakes or regressions.
- Prioritizing code simplicity, Ponytail engineering principles, zero-dependency efficiency, and air-gapped data privacy.
- Collaborating transparently with maintainers using Tududi Task Master orchestration tools (`tududi`).

### 2.2 Unacceptable Behaviors
Examples of unacceptable behavior include:
- The use of sexualized language or imagery, and sexual attention or advances of any kind.
- Trolling, insulting or derogatory comments, and personal or political attacks.
- Public or private harassment of any community participant.
- Publishing others' private information, such as a physical or electronic address, without explicit permission (doxxing).
- Malicious injection of unverified telemetry, cloud exfiltration hooks, tracking scripts, backdoors, or non-deterministic code.
- Masking underlying bugs, swallowing runtime exceptions, commenting out broken assertions, or deleting failing unit tests.
- Other conduct which could reasonably be considered inappropriate in a professional open-source engineering setting.

---

## 3. Technical Ethics, AI Safety & Air-Gapped Governance

In addition to interpersonal conduct standards, all contributors (human developers and autonomous AI coding agents) to **Uroboros Knowledge Engine** must adhere to strict technical ethics:

### 3.1 100% Zero-Cloud Data Sovereignty
- **Air-Gapped Guarantee**: Never re-introduce hidden tracking pixels, third-party analytics scripts, or un-consented telemetry to cloud endpoints.
- **Local Model Processing**: All model inference, embedding generation, and vector indexing must run strictly on local hardware (Ollama / GGUF) without external API dependencies unless explicitly authorized by the user.

### 3.2 Deterministic Security & Cryptographic Integrity
- **PII Scrubbing**: PII redaction rules ([`pii_privacy_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/pii_privacy_guard.py)) and Zero-Knowledge proofs ([`zk_data_masker.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/zk_data_masker.py)) must remain functional and enforced across all pull requests.
- **Audit Trail Compliance**: All administrative and file ingestion operations must log immutable entries to the cryptographic audit ledger ([`crypto_audit_ledger.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/crypto_audit_ledger.py)).

### 3.3 Ponytail Minimalist Dependency Guardrails
- **Standard Library First**: Avoid introducing third-party dependencies when native Python standard library modules or platform APIs solve the problem.
- **Zero-Boilerplate Standard**: Delete unused abstractions, dead code paths, and speculative complexity. Shortest working diff wins.

---

## 4. Autonomous Agent & Multi-AI Interaction Conduct

As an AI-native repository developed with pair-programming AI assistants, the following rules govern agentic contributions:

1. **Task Master Orchestration**: All multi-step execution plans, checklists, and tasks must be logged and tracked using Tududi Task Master MCP (`tududi`), syncing to `savianalexander@pm.me`.
2. **Empirical Log Integrity**: Agents must fetch and inspect un-truncated error logs before forming diagnostic hypotheses. Never guess file paths or internal schema definitions.
3. **No Superficial Symptom Patches**: Fix root causes at the function level rather than patching single call sites or returning dummy fallbacks.
4. **Preservation of Documentation & Code Comments**: Maintain all docstrings, architectural comments, and intentional simplification markers (`ponytail:`).

---

## 5. Scope

This Code of Conduct applies within all project spaces (including the GitHub repository, issue trackers, pull requests, project documentation, Tududi Task Master orchestration channels, and local CLI execution suites), and it also applies when an individual or agent is officially representing the project in public spaces.

---

## 6. Reporting Guidelines

Instances of abusive, harassing, insecure, or otherwise unacceptable behavior may be reported to the project lead at:

**Project Lead & Maintainer**: Savian Alexander  
**Email**: `savianalexander@pm.me`  
**Task Master User**: `savianalexander@pm.me`

All complaints will be reviewed and investigated promptly and fairly. All project maintainers are obligated to respect the privacy and security of the reporter of any incident.

---

## 7. Enforcement Responsibilities & Escalation Matrix

Community leaders will follow these Enforcement Responsibilities in determining consequences for any action deemed in violation of this Code of Conduct:

### 1. Correction
- **Community Impact**: Use of inappropriate language or minor technical violations (e.g., introducing unnecessary dependencies).
- **Consequence**: A written warning from community leaders explaining the violation and requesting code simplification or an apology.

### 2. Warning
- **Community Impact**: A serious single incident or sustained pattern of unprofessional behavior or unapproved architectural changes.
- **Consequence**: Formal warning with mandatory peer review required for all subsequent commits.

### 3. Temporary Ban
- **Community Impact**: Severe violation of community standards or injection of vulnerable code.
- **Consequence**: A temporary ban from submitting pull requests or communicating in project channels for a specified period.

### 4. Permanent Ban
- **Community Impact**: Demonstrating a pattern of violation, sustained harassment, intentional security sabotage, or malicious data exfiltration.
- **Consequence**: Permanent revocation of repository write access and permanent ban from community spaces.

---

## 8. Dispute Resolution & Community Arbitration

In cases of architectural disputes or enforcement disagreements, community leaders will convene a review panel to evaluate technical evidence, test ledgers, and git commit history to render a binding decision.

---

## 9. Continuous Compliance Auditing & SOC 2 Attestation

This Code of Conduct operates in alignment with our automated SOC 2 Type II trust controls ([`docs/soc2_type2_attestation.md`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/docs/soc2_type2_attestation.md)). Automated audit scripts ([`scripts/update_test_ledger.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/scripts/update_test_ledger.py)) continuously verify that repository changes maintain 100% compliance with access control, encryption, PII redaction, and clean architecture standards.

---

## 10. Algorithmic Neutrality, Bias Prevention & Grounding Proofs

1. **Zero Factual Hallucination Standard**: All RAG models and generative responses must be evaluated against retrieved source passages via [`rag_grounding_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/rag_grounding_guard.py). Unverified claims or low-confidence outputs ($< 0.65$) must trigger refusal reports rather than speculative generation.
2. **Algorithmic Neutrality**: Context weighting algorithms (BM25, Vector, RRF, ColBERT MaxSim) must remain mathematically objective and unbiased across all document categories, domains, and languages.

---

## 11. Autonomous Swarm Ethics & Memory Safety

1. **Swarm Collision Avoidance**: Multi-agent swarm searches ([`swarm_rag.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/swarm_rag.py)) must enforce thread isolation and memory bounds to prevent race conditions or resource starvation.
2. **Agent Memory Lifecycle**: Episodic agent memories ([`agent_memory.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/domain/agent_memory.py)) must be sanitized of PII and structured with explicit expiration timestamps to prevent memory leakage.

---

## 12. Hardware Circuit Breaker & Memory Panic Isolation

1. **Single-Instance Enforcement**: To prevent VRAM pagefile exhaustion, hardware process guards ([`model_manager.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/core/model_manager.py)) must strictly cap loaded LLM processes to 1 active instance (`OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=1`).
2. **Panic Recovery**: Process memory limit guards ([`system_stability_guard.py`](file:///c:/Users/Administrator/Desktop/Neuro%20Alexander/src/infrastructure/system_stability_guard.py)) are mandated to trigger automatic garbage collection and WAL connection resets whenever RAM utilization exceeds 90%.

---

## 13. Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.1, available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html, with additions for air-gapped zero-cloud data sovereignty, AI agent governance, and Ponytail minimalist engineering principles.
