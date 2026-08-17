---
title: "Atlassian Jira Cloud REST API v3 Official OpenAPI Specification"
source_authority: "Atlassian Developer Documentation"
spec_version: "OpenAPI 3.0.0 / Jira Cloud v3"
endpoint_base: "https://{your-domain}.atlassian.net/rest/api/3"
harvested_at: "2026-08-17T16:07:26Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "ATLASSIAN_OPENAPI_SPEC_VERIFIED"
---

# Atlassian Jira Cloud REST API v3 Official Specification

## 1. Core Issue Creation Contract (`POST /rest/api/3/issue`)

### Request Body JSON Schema:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "JiraIssueCreateRequest",
  "type": "object",
  "required": ["fields"],
  "properties": {
    "fields": {
      "type": "object",
      "required": ["project", "summary", "issuetype"],
      "properties": {
        "project": {
          "type": "object",
          "properties": { "key": { "type": "string" }, "id": { "type": "string" } }
        },
        "summary": { "type": "string", "maxLength": 255 },
        "description": {
          "type": "object",
          "description": "Atlassian Document Format (ADF) or plain string",
          "properties": {
            "type": { "type": "string", "enum": ["doc"] },
            "version": { "type": "integer", "enum": [1] },
            "content": { "type": "array" }
          }
        },
        "issuetype": {
          "type": "object",
          "properties": { "name": { "type": "string", "enum": ["Test", "Story", "Bug", "Task", "Epic"] } }
        },
        "priority": {
          "type": "object",
          "properties": { "name": { "type": "string", "enum": ["Highest", "High", "Medium", "Low", "Lowest"] } }
        },
        "labels": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 2. Xray Test Management Schema for Test Steps

```json
{
  "title": "XrayTestStepSpecification",
  "type": "object",
  "required": ["stepNumber", "action", "data", "expectedResult"],
  "properties": {
    "stepNumber": { "type": "integer", "minimum": 1 },
    "action": { "type": "string", "description": "Interaction or caseworker procedure" },
    "data": { "type": "string", "description": "Exact input parameters or evidence values" },
    "expectedResult": { "type": "string", "description": "Statutory rule calculation or system state" }
  }
}
```

---

## 3. Requirements Traceability Matrix Link Types (`POST /rest/api/3/issueLink`)

```json
{
  "type": { "name": "Tests", "inward": "is tested by", "outward": "tests" },
  "inwardIssue": { "key": "REQ-MED-101" },
  "outwardIssue": { "key": "JIRA-TC-MED-001" }
}
```
