---
title: "Requirements Traceability Matrix (RTM) in Jira Xray & Zephyr"
category: "Enterprise QA Governance"
source: "IEEE 29119 & Jira RTM Standard"
version: "2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Jira", "RTM", "RequirementsTraceability", "Compliance", "SOC2", "Audit"]
---

# Requirements Traceability Matrix (RTM) Architecture

## 1. What is an RTM?
A Requirements Traceability Matrix (RTM) is an architectural framework that maps business, statutory, and regulatory requirements directly to corresponding software test cases, test executions, and discovered defects.

```
+------------------+       +------------------+       +------------------+       +------------------+
|   REQUIREMENT    | ----> |    TEST CASE     | ----> |  TEST EXECUTION  | ----> |      DEFECT      |
|  (e.g. REQ-SNAP) |       | (JIRA-TC-SNAP-01)|       | (PASS/FAIL Run)  |       |  (BUG-2026-01)   |
+------------------+       +------------------+       +------------------+       +------------------+
```

## 2. Why Traceability is Essential for State & SOC 2 Audits
1. **Zero Requirement Gaps**: Proves that 100% of statutory rules (e.g. 7 CFR 273 SNAP rules) have verified test coverage.
2. **Defect Impact Analysis**: When a test fails during UAT, the RTM immediately identifies which statutory requirement is violated.
3. **Change Impact / Blast Radius**: When policy changes (e.g. annual FPL poverty line updates), the RTM identifies the exact test suites that must be updated.

## 3. Jira Traceability Link Types
- `tests` / `is tested by`: Links a `Test` issue to a `Story` or `Requirement`.
- `relates to`: Bidirectional conceptual linkage.
- `blocks` / `is blocked by`: Identifies critical defects obstructing UAT sign-off.
