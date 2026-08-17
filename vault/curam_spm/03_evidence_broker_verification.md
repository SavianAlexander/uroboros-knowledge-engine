---
title: "IBM Cúram Evidence Management, Evidence Broker & Verification Framework"
category: "Enterprise Evidence Governance"
source: "IBM Cúram Evidence Management Guide"
version: "8.0.x / 2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Curam", "EvidenceManagement", "EvidenceBroker", "VerificationEngine", "Audit"]
---

# IBM Cúram Evidence Management & Verification Framework

## 1. Evidence Architecture in Cúram SPM
In Cúram SPM, **Evidence** represents verified facts about participants, relationships, and financial circumstances required to determine social program eligibility.

### 1.1 Evidence Structure & Metadata
Every evidence record contains:
- **Case Participant**: The individual to whom the evidence applies.
- **Evidence Type**: e.g., `PDC00001` (Earned Income), `PDC00002` (Shelter Expense), `PDC00003` (Medical Condition).
- **Effective Period**: Start Date and End Date (`YYYY-MM-DD`).
- **Status Lifecycle**: `In-Edit` $\rightarrow$ `Active` $\rightarrow$ `Superseded` $\rightarrow$ `Canceled`.
- **Change Reason**: e.g., `Initial Intake`, `Reported Change of Income`, `Annual Redetermination`.

---

## 2. The Evidence Broker Subsystem
The Evidence Broker enables automated, rules-governed sharing of evidence across multiple cases and agencies:
- **Bi-directional Sharing**: Updates made on an Integrated Case automatically cascade to child Product Delivery Cases (PDCs) and related person records.
- **Conflict Resolution**: When conflicting evidence is received (e.g. state wage clearinghouse reports $2,200/mo while citizen reported $1,600/mo), the Evidence Broker queues a **Verification Task** for caseworker adjudication.
- **Trusted External Ingestion**: Direct integration with federal interfaces (CMS Data Hub, SSA Title II/XVI, Equifax Work Number, IRS 1095).

---

## 3. The Cúram Verification Engine
The Verification Engine enforces statutory proof requirements before benefits can be disbursed:
1. **Verification Item**: The specific proof required (e.g. `Paystub (Last 30 Days)`, `Birth Certificate`, `Lease Agreement`).
2. **Verification Level**: Mandatory (blocks PDC activation) vs. Optional / Conditional.
3. **Due Date & Escalation**: Tracks statutory 10-day citizen response windows with automated reminders.
4. **Document Attachment**: Integrates with Enterprise Content Management (ECM) systems for digital document storage.
