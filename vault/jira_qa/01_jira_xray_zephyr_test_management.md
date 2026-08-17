---
title: "Jira Xray & Zephyr Enterprise QA Test Management Standards"
category: "Enterprise QA & Test Engineering"
source: "Atlassian Jira QA & Xray/Zephyr Architecture Standard"
version: "2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Jira", "Xray", "Zephyr", "TestCaseManagement", "QA", "Traceability"]
---

# Jira Xray & Zephyr Enterprise QA Test Management

## 1. Executive QA Test Architecture Overview
In modern enterprise software engineering, test cases, test plans, test executions, and defects are managed natively within **Atlassian Jira** using industry-standard testing engines such as **Xray Test Management** and **Zephyr Enterprise/Squad**.

---

## 2. Core Issue Types in Jira QA

### 2.1 `Test` Issue (`issueType: "Test"`)
Represents a singular, repeatable test case specification:
- **Test Type**: Manual (Step-by-Step), Generic (Automated/Pytest), or Cucumber (Gherkin BDD: Given/When/Then).
- **Preconditions (`Precondition`)**: Conditions that must be satisfied before test execution begins.
- **Test Steps (`testSteps`)**: Ordered sequential actions containing:
  1. `Step #`: 1-indexed execution step.
  2. `Action`: User or caseworker interaction.
  3. `Data`: Exact input parameters, citizen evidence payload, or API request.
  4. `Expected Result`: Statutory or system expected outcome.

### 2.2 `Test Set` / `Test Suite`
A logical grouping of related test cases (e.g. `Medicaid MAGI Statutory Acceptance Suite`, `SNAP Deduction Boundary Suite`).

### 2.3 `Test Execution` (`issueType: "Test Execution"`)
An instance of running a test suite against a specific environment or build version:
- **Execution Status**: `PASS`, `FAIL`, `EXECUTING`, `BLOCKED`, `ABORTED`.
- **Actual Results**: Logs, timestamps, duration in ms, and screenshot artifacts.

### 2.4 `Test Plan`
High-level testing strategy tracking multiple test executions across major release milestones (e.g. `Release 2026.1 Enterprise Sign-Off`).

---

## 3. Standard JSON Schema for Jira Xray/Zephyr Test Cases

```json
{
  "issueType": "Test",
  "key": "JIRA-TC-MED-001",
  "summary": "Verify Medicaid MAGI Adult Expansion (<= 138% FPL)",
  "description": "Objective: Verify standard MAGI adult expansion rule under Title XIX",
  "priority": "High",
  "labels": ["Medicaid", "MAGI", "POSITIVE_ELIGIBLE"],
  "preconditions": [
    "Caseworker logged into Cúram SPM Intake",
    "State residency verified"
  ],
  "testData": {
    "applicant_name": "Marcus Vance",
    "household_size": 1,
    "earned_income_monthly": 1200.0
  },
  "testSteps": [
    {
      "stepNumber": 1,
      "action": "Enter Applicant Identity & Income Evidence",
      "data": "Household Size: 1, Earned Income: $1,200/mo",
      "expectedResult": "Evidence captured without validation errors"
    },
    {
      "stepNumber": 2,
      "action": "Execute CER Determination RuleSet",
      "data": "Trigger Medicaid MAGI Rules Engine",
      "expectedResult": "5% FPL disregard applied; Approved under 138% FPL limit"
    }
  ],
  "requirementLinks": ["REQ-MED-101"]
}
```
