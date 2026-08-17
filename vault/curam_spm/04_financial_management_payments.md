---
title: "IBM Cúram Financial Management, Benefit Issuance & Overpayment Recovery"
category: "Enterprise Financial Operations"
source: "IBM Cúram Financial Management Guide"
version: "8.0.x / 2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Curam", "FinancialManagement", "EBT", "PaymentIssuance", "Overpayment"]
---

# IBM Cúram Financial Management & Benefit Issuance

## 1. Financial Subsystem Architecture
The Cúram Financial module bridges statutory decision outcomes to real-world monetary disbursements and accounting ledgers.

```
+-----------------------------+
| CER Rule Determination      |
| Monthly Entitlement: $768.00|
+-----------------------------+
               │
               ▼
+-----------------------------+
| Financial Component (FC)    |
| Type: Payment | Sched: Monthly
+-----------------------------+
               │
               ▼
+-----------------------------+
| Financial Instruction (IL)  |
| Gross: $768 | Deduction: $0 |
+-----------------------------+
               │
               ▼
+-----------------------------+
| Delivery Mechanism          |
| EBT Card / Direct Deposit   |
+-----------------------------+
```

## 2. Core Financial Components (FC)
- **Payment Component**: Represents ongoing entitlement disbursed to the client (e.g. TANF Cash Grant, SNAP Monthly Allotment).
- **Liability Component**: Represents money owed back to the agency (e.g. Overpayments due to unreported income).
- **Billing Component**: Invoices generated for child care or health plan premiums.

## 3. Benefit Delivery Methods
- **Electronic Benefit Transfer (EBT)**: USDA SNAP and TANF food/cash card integration via ISO 8583 banking protocols.
- **Automated Clearing House (ACH / Direct Deposit)**: NACHA formatted payment files for direct bank accounts.
- **Third-Party Vendor Payments**: Housing voucher payments issued directly to private landlords under Section 8 HAP contracts.

## 4. Recoupment & Overpayment Recovery
When retroactive recalculation discovers past over-issuance:
1. An **Overpayment Case** is created.
2. Statutory maximum deduction limits (e.g. 10% or $10/month from ongoing SNAP allotment) are automatically enforced.
3. Repayment ledgers maintain full auditability for state and federal comptrollers.
