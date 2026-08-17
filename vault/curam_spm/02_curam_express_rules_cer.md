---
title: "IBM Cúram Express Rules (CER) Engine Specification & RuleSet Architecture"
category: "Enterprise Rule Engine Standards"
source: "IBM Cúram Express Rules (CER) Developer & Architecture Guide"
version: "8.0.x / 2026 Edition"
harvested_at: "2026-08-17 14:59:00 UTC"
tags: ["Curam", "CER", "RuleEngine", "RuleSets", "DecisionTables", "MAGI", "SNAP"]
---

# IBM Cúram Express Rules (CER) Engine Architecture

## 1. Executive CER Overview
Cúram Express Rules (CER) is the declarative, object-oriented rule engine embedded within IBM Cúram Social Program Management. It enables social program policy analysts and technical architects to codify statutory federal, state, and local regulations into modular, maintainable XML/domain rule sets.

Unlike traditional procedural programming or legacy rule engines (such as classic Cúram Rules or Ilog JRules), CER operates on an **in-memory Directed Acyclic Graph (DAG) of dependency-tracked rule objects**, allowing automatic retroactive recalculation, dynamic timeline slicing, and explainable decision trees.

---

## 2. Fundamental CER Concepts & Terminology

### 2.1 Rule Set (`<RuleSet>`)
A named container for related rule classes. For example:
- `MedicaidMAGIRuleSet.xml`
- `SNAPEligibilityAndEntitlementRuleSet.xml`
- `TANFDeprivationAndCashGrantRuleSet.xml`

### 2.2 Rule Class (`<Class>`)
An object definition within a rule set specifying attributes, calculation expressions, and business logic. Rule classes can inherit from base classes (e.g. `AbstractHouseholdMember` $\rightarrow$ `MedicaidApplicant`).

### 2.3 Rule Attribute (`<Attribute>`)
A typed property on a rule class. CER attributes can be:
1. **Evidence-backed attributes**: Ingested directly from Dynamic Evidence (e.g. `earnedIncomeAmount`, `dateOfBirth`, `shelterCost`).
2. **Derived / Calculated attributes**: Computed via expressions (e.g. `countableMonthlyIncome`, `incomePercentOfFPL`, `isIncomeEligible`).

### 2.4 Rule Object (`RuleObject`)
An instance of a rule class instantiated in a rule session during eligibility evaluation.

### 2.5 Rule Session (`RuleSession`)
The execution context that holds all rule objects, resolves dependencies, caches intermediate calculations, and computes final eligibility decisions.

---

## 3. CER Decision Lifecycle & Execution Flow

```
+-------------------------------------------------------------------------+
| STEP 1: Case Evidence Extraction & Timeline Slicing                     |
|  - Participant data, income intervals, household composition            |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| STEP 2: Rule Object Graph Population                                    |
|  - Instantiates CER rule objects representing case entities             |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| STEP 3: Statutory Non-Financial Rule Evaluation                         |
|  - State residency verification                                         |
|  - Citizenship / Lawful presence check                                  |
|  - Categorical conditions (Child, Pregnancy, Disability, Deprivation)   |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| STEP 4: Financial Eligibility & Countable Income Determination          |
|  - Ingest empirical FPL guidelines and SMI tables                       |
|  - Execute statutory disregards (5% FPL disregard for MAGI)             |
|  - Apply earned income disregards (20% for SNAP, $90 + 30% for TANF)    |
|  - Calculate excess shelter & standard deductions                       |
+-------------------------------------------------------------------------+
                                     │
                                     ▼
+-------------------------------------------------------------------------+
| STEP 5: Decision Matrix & Entitlement Calculation                       |
|  - Decision Code: APPROVED | DENIED | INELIGIBLE                        |
|  - Monthly Benefit Entitlement ($ Allotment / $ Grant / HAP Subsidy)    |
|  - Generate Explainable Decision Tree & Audit Trace                     |
+-------------------------------------------------------------------------+
```

---

## 4. Key Statutory CER Expressions & Operators

CER provides declarative XML expressions for high-assurance mathematical and logical operations:

- `<compare>`: Value comparison (`<`, `<=`, `==`, `>=`, `>`).
- `<condition>`: Ternary if-then-else branching logic.
- `<sum>`, `<subtract>`, `<multiply>`, `<divide>`: Numeric arithmetic with exact decimal precision (`java.math.BigDecimal`).
- `<choose>`: Switch-case evaluation for multi-tier policy tables.
- `<timeline>`: Interval-based time-slicing for tracking changing income over benefit months.
- `<search>`: Querying rule objects across the session DAG.

---

## 5. Explainability & State Audit Compliance
Every decision produced by the CER engine is backed by a deterministic **Decision Tree Trace**. Caseworkers, supervisors, and state regulatory auditors can drill down into any historical decision to view:
- The exact evidence values in effect at the determination timestamp.
- The statutory policy version utilized.
- The step-by-step arithmetic deductions applied.
- The statutory reason codes justifying approval or denial.
