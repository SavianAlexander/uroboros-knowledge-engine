---
title: "IBM Cúram Social Program Management (SPM) Architecture & Case Lifecycle"
category: "Enterprise Social Program Architecture"
source: "IBM Cúram SPM Core Platform Reference Guide"
version: "8.0.x / 2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Curam", "SPM", "Architecture", "IntegratedCase", "PDC", "SocialPrograms"]
---

# IBM Cúram Social Program Management (SPM) Architecture

## 1. Executive Platform Overview
IBM Cúram Social Program Management (SPM) is the global standard enterprise software platform for health, human services, and social assistance administration. Designed specifically for government social security agencies and human services departments, Cúram SPM provides a complete end-to-end framework for citizen intake, multi-program eligibility determination, evidence management, benefit entitlement calculation, case lifecycle management, and financial issuance.

## 2. Core Case Management Hierarchy

```
+-------------------------------------------------------------------------+
|                        PARTICIPANT (Person / Prospect)                 |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
|                       INTEGRATED CASE (IC)                              |
|  - Shared Household Context                                             |
|  - Unified Citizen & Household Evidence (Income, Assets, Shelter)       |
|  - Cúram Express Rules (CER) Engine Evaluation                         |
+-------------------------------------------------------------------------+
          │                                     │
          ▼                                     ▼
+-----------------------------+       +-----------------------------+
| PRODUCT DELIVERY CASE (PDC) |       | PRODUCT DELIVERY CASE (PDC) |
| Program: Medicaid MAGI      |       | Program: SNAP Food Stamps   |
| Status: Active / Approved   |       | Status: Active / Approved   |
| Monthly Entitlement: $0.00  |       | Monthly Entitlement: $768.00|
+-----------------------------+       +-----------------------------+
```

### 2.1 The Participant Layer
- **Person**: An individual known to the agency whose identity, SSN, date of birth, and residency have been registered.
- **Prospect Person**: An individual whose identity is not yet fully verified (common during anonymous pre-screening).
- **Representative / Employer**: Corporate or organizational participants interacting with the case.

### 2.2 The Integrated Case (IC)
The Integrated Case serves as the single centralized hub for an entire family or household. Rather than forcing clients to submit separate applications for Medicaid, SNAP, TANF, and Child Care, all household evidence (identity, relationships, employment, unearned income, housing expenses, medical costs) is captured once at the Integrated Case level.

### 2.3 Product Delivery Cases (PDC)
When eligibility is established by the Cúram Express Rules (CER) engine, the system automatically instantiates one or more Product Delivery Cases (PDCs) under the parent Integrated Case:
- **Medical Assistance PDC**: Delivers Medicaid / CHIP health coverage cards and plan enrollment.
- **Food Assistance PDC**: Generates monthly Electronic Benefit Transfer (EBT) food allotments.
- **Cash Assistance PDC**: Manages direct deposit or check disbursements for TANF assistance.
- **Child Care PDC**: Authorizes vendor child care subsidies and tracks family copayment tiers.

## 3. Key Subsystems in Cúram SPM

### 3.1 Citizen Self-Service Portal & Universal Intake
Enables citizens to apply online, upload documentation, report changes in circumstance, and check benefit schedules. Applications are automatically validated and routed into caseworker work queues.

### 3.2 Dynamic Evidence Framework
Provides configurable metadata-driven evidence schemas without requiring Java code recompilation. Evidence versions are temporal, tracking effective date spans (e.g. `2026-01-01` to `Open-Ended`) and full audit histories.

### 3.3 Evidence Broker
Automatically synchronizes evidence across multiple integrated cases, external health insurance marketplaces (HHS CMS Hub), and child support enforcement systems.

### 3.4 Cúram Express Rules (CER) Engine
The high-performance declarative business rules engine that executes statutory policy matrices, calculates financial eligibility, and determines benefit entitlement amounts.

### 3.5 Financial & Payment Issuance Module
Calculates financial components, gross and net benefit entitlements, executes mandatory deductions or overpayment recoveries, and generates payment instruction batches for EBT, Automated Clearing House (ACH), or paper warrants.
