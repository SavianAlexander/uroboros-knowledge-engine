---
title: "ISO/IEC/IEEE 29119-3: International Standard for Software Testing - Test Documentation"
source_authority: "ISO/IEC JTC 1/SC 7 Software and Systems Engineering"
standard_id: "ISO/IEC/IEEE 29119-3:2021"
harvested_at: "2026-08-17T17:48:00Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "ISO_IEEE_29119_VERIFIED"
---

# ISO/IEC/IEEE 29119-3 Test Documentation Data Models

## 1. Test Case Specification Structure (Clause 7.2)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ISO29119TestCaseSpecification",
  "type": "object",
  "required": [
    "testCaseIdentifier",
    "testCaseObjective",
    "preconditions",
    "inputData",
    "expectedResults",
    "statutoryRuleTraceability"
  ],
  "properties": {
    "testCaseIdentifier": { "type": "string", "pattern": "^[A-Z0-9_-]+$" },
    "testCaseObjective": { "type": "string" },
    "preconditions": { "type": "array", "items": { "type": "string" } },
    "inputData": { "type": "object" },
    "expectedResults": {
      "type": "object",
      "required": ["decisionStatus", "benefitAmount", "statutoryRuleReference"]
    },
    "statutoryRuleTraceability": { "type": "string" }
  }
}
```
