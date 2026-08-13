# Contributor Covenant Code of Conduct

## 1. Our Pledge

We as contributors, maintainers, and community leaders of the **Uroboros Knowledge Engine (Neuro Alexander)** project pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, caste, color, religion, or sexual identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming, diverse, inclusive, and healthy community.

---

## 2. Our Standards

### 2.1 Positive Behaviors
Examples of behavior that contributes to a positive environment for our project include:
- Demonstrating empathy, kindness, and respect toward other community members.
- Being respectful of differing opinions, architectural viewpoints, and technical experiences.
- Giving and gracefully accepting constructive feedback.
- Accepting responsibility and apologizing promptly to those affected by our mistakes.
- Prioritizing code simplicity, ponytail engineering principles, zero-dependency efficiency, and air-gapped data privacy.
- Collaborating transparently with fellow maintainers, contributors, and autonomous AI agents.

### 2.2 Unacceptable Behaviors
Examples of unacceptable behavior include:
- The use of sexualized language or imagery, and sexual attention or advances of any kind.
- Trolling, insulting or derogatory comments, and personal or political attacks.
- Public or private harassment of any community participant.
- Publishing others' private information, such as a physical or electronic address, without explicit permission (doxxing).
- Malicious injection of unverified telemetry, cloud data exfiltration hooks, backdoors, or non-deterministic code.
- Other conduct which could reasonably be considered inappropriate in a professional setting.

---

## 3. Enforcement Responsibilities

Community leaders and maintainers are responsible for clarifying and enforcing our standards of acceptable behavior and will take appropriate, fair corrective action in response to any behavior they deem inappropriate, threatening, offensive, or harmful.

Community leaders have the right and responsibility to remove, edit, or reject comments, commits, code edits, wiki pages, issues, and other contributions that are not aligned to this Code of Conduct, and will communicate reasons for enforcement decisions when appropriate.

---

## 4. Scope

This Code of Conduct applies within all project spaces (including the GitHub repository, issue trackers, pull requests, project documentation, and Tududi Task Master orchestration channels), and it also applies when an individual is officially representing the project in public spaces.

---

## 5. Reporting Guidelines

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project lead at:

**Email**: `savianalexander@pm.me`

All complaints will be reviewed and investigated promptly and fairly. All project maintainers are obligated to respect the privacy and security of the reporter of any incident.

---

## 6. Enforcement Guidelines

Community leaders will follow these Enforcement Responsibilities in determining the consequences for any action they deem in violation of this Code of Conduct:

### 6.1 Correction
- **Community Impact**: Use of inappropriate language or other behavior deemed unprofessional or unwelcome in the community.
- **Consequence**: A private, written warning from community leaders, providing clarity around the nature of the violation and an explanation of why the behavior was inappropriate. An apology may be requested.

### 6.2 Warning
- **Community Impact**: A violation through a single incident or series of actions.
- **Consequence**: A warning with consequences for continued behavior. No interaction with the people involved, including unsolicited interaction with those enforcing the Code of Conduct, for a specified period of time. Violating these terms may lead to a temporary or permanent ban.

### 6.3 Temporary Ban
- **Community Impact**: A serious violation of community standards, including sustained inappropriate behavior.
- **Consequence**: A temporary ban from any sort of interaction or public communication with the community for a specified period of time.

### 6.4 Permanent Ban
- **Community Impact**: Demonstrating a pattern of violation of community standards, including sustained harassment, discrimination, or malicious exfiltration/sabotage of project code or security controls.
- **Consequence**: A permanent ban from any sort of public interaction within the community.

---

## 7. Data Privacy, AI Ethics & Security Guardrails

In addition to interpersonal conduct standards, all contributors to **Uroboros Knowledge Engine** must adhere to strict technical ethics:

1. **100% Zero-Cloud Data Sovereignty**: Never re-introduce hidden tracking pixels, third-party analytics scripts, or un-consented telemetry to cloud endpoints.
2. **Deterministic Security Controls**: Ensure that PII redaction rules (`pii_privacy_guard.py`) and Zero-Knowledge proofs (`zk_data_masker.py`) remain functional across all PRs.
3. **No Malicious Dependencies**: Avoid adding unvetted or bloated third-party dependencies when standard library or native platform features cover the use case (Ponytail Principles).

---

## 8. AI Agent & Autonomous System Conduct Standards

Autonomous AI assistants, subagents, and automated developer bots operating within this repository are bound by the following operational directives:

1. **Task Master Orchestration**: All task planning, checklists, and execution logs MUST use the Tududi Task Master integration (`call_mcp_tool tududi`) rather than ephemeral markdown files.
2. **No Superficial Symptom Patches**: Never resolve build or test errors by swallowing exceptions, deleting failing tests, or returning dummy fallback data. Always address root causes.
3. **Empirical Verification Mandate**: Never declare a task resolved without running build (`npm run build`) or unit test (`pytest`) verification commands and inspecting complete logs.
4. **Preserve System Architecture & Privacy**: AI agents must never exfiltrate user data, bypass air-gapped security boundaries, or introduce unauthorized network calls.

---

## 9. Vulnerability Disclosure & Responsible Security Reporting

Security vulnerabilities should be reported privately to prevent zero-day exploitation:

- **Private Reporting Email**: `savianalexander@pm.me`
- **Initial Response SLA**: Within 24 hours of receipt.
- **Triage & Patch SLA**: Security patches issued within 72 hours for critical/high severity vulnerabilities.
- **Public Disclosure**: Security advisories published after patches are verified and merged.

---

## 10. Governance & Maintainer Accountability

- **Transparent Decision Making**: Architectural decisions and breaking changes are documented in public RFCs and commit messages.
- **Audit Ledger Integrity**: All code modifications are validated against automated clean architecture tests (`scripts/architecture_cli.py`) and cryptographic SHA-256 audit ledgers (`scripts/update_test_ledger.py`).
- **Conflict Resolution**: Disagreements regarding implementation details are resolved by testing empirical benchmarks, SLA impact, and code simplicity (shortest working diff wins).

---

## 11. Attribution

This Code of Conduct is adapted from the [Contributor Covenant](https://www.contributor-covenant.org), version 2.1, available at https://www.contributor-covenant.org/version/2/1/code_of_conduct.html.
