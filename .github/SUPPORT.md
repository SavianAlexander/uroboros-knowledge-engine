# Support Guidelines & Help Resources

Thank you for using **Uroboros Knowledge Database Engine (Neuro Alexander)**! Below are the recommended channels and workflows for getting support, asking questions, and resolving technical issues.

---

## 1. Documentation & Self-Help Resources

Before opening a support request, please consult our documentation suite:

* **[Master Readme](README.md)**: Exhaustive 33-section reference covering system features, mathematical formulas, DDL schemas, REST API specs, and troubleshooting matrix.
* **[Troubleshooting Matrix](README.md#25-troubleshooting-matrix--diagnostic-workflows)**: Solutions for common issues like `WinError 32` file locks, Ollama connection errors, and Starlette warnings.
* **[Architecture Blueprint](ARCHITECTURE.md)**: Deep technical breakdown of clean architecture layers, ingestion pipelines, and retrieval algorithms.
* **[Security Policy](SECURITY.md)**: Air-gapped guarantees, zero-cloud execution rules, and vulnerability reporting.

---

## 2. Recommended Support Channels

| Question Type / Issue | Recommended Channel | SLA Response Time |
| :--- | :--- | :--- |
| **Bug Reports** | [GitHub Issues (Bug Report)](.github/ISSUE_TEMPLATE/bug_report.md) | **< 24 Hours** |
| **Feature Proposals** | [GitHub Issues (Feature Request)](.github/ISSUE_TEMPLATE/feature_request.md) | **< 48 Hours** |
| **Security Vulnerabilities** | Email to Maintainer (`savianalexander@pm.me`) | **< 24 Hours** (Confidential) |
| **General Q&A & Usage** | [GitHub Discussions](https://github.com/SavianAlexander/uroboros-knowledge-engine/discussions) | Community-driven |

---

## 3. Submitting Effective Support Requests

To help us resolve your issue quickly, please ensure your support request includes:

1. **Exact Reproduction Steps**: Clear command line syntax or API request payload.
2. **Empirical Logs**: Un-truncated error stack trace or log output from `pytest.log` or FastAPI stdout.
3. **Environment Specs**: Operating System, Python version (`3.12+`), FastAPI version, and hardware profile (RAM/VRAM).
