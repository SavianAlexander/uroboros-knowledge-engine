---
title: "Defect Triage, Severity Classification & Root Cause Analysis (RCA)"
category: "Defect Lifecycle & Quality Governance"
source: "Enterprise QA Defect Triage & Triage Board Standard"
version: "2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Jira", "DefectTriage", "Severity", "RCA", "QualityAssurance"]
---

# Defect Triage & Severity Classification Lifecycle

## 1. Defect Severity vs. Priority
- **Severity**: The objective impact on system functionality, statutory calculations, and data integrity.
- **Priority**: The urgency with which the defect must be resolved by the engineering team.

---

## 2. Standard Defect Severity Tiers

| Severity Tier | Description | Production Go-Live Impact |
| :--- | :--- | :--- |
| **CRITICAL / BLOCKER** | System crash, data corruption, statutory miscalculation of benefit dollars, security vulnerability, or complete inability to process applications. | **BLOCKS GO-LIVE (0 Allowed)** |
| **MAJOR** | Important feature failure (e.g. PDF notice generation failure, batch payment delay) with no automated workaround. | Must have approved mitigation |
| **MINOR** | Non-critical functional defect with available manual workaround (e.g. incorrect sort order in caseworker inbox). | Allowed with scheduled patch |
| **TRIVIAL / COSMETIC** | Typo, styling misalignment, or cosmetic UI artifact. | Allowed |

---

## 3. Defect Lifecycle Workflow in Jira

```
[NEW] ──> [TRIAGED] ──> [IN DEVELOPMENT] ──> [RESOLVED / FIX COMMITTED]
                                                      │
                                                      ▼
[CLOSED / VERIFIED] <── [UAT RE-TESTED: PASS] <── [IN QA RE-TEST]
                                                      │
                                                      ▼ (FAIL)
                                                [RE-OPENED]
```
