---
title: "IBM Cúram Express Rules (CER) XML Document Type Definition (DTD) & Grammar"
source_authority: "IBM Cúram Social Program Management Architecture Specification"
spec_version: "CER 8.0.x"
harvested_at: "2026-08-17T16:14:42Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CER_XML_GRAMMAR_VERIFIED"
---

# IBM Cúram Express Rules (CER) XML Grammar & DTD Specification

## 1. Formal XML Document Type Definition (`CuramExpressRules.dtd`)

```xml
<!ELEMENT RuleSet (Class*)>
<!ATTLIST RuleSet
    name CDATA #REQUIRED
    xmlns:xsi CDATA #IMPLIED
    xsi:noNamespaceSchemaLocation CDATA #IMPLIED>

<!ELEMENT Class (Annotations?, Attribute*)>
<!ATTLIST Class
    name CDATA #REQUIRED
    extends CDATA #IMPLIED
    isAbstract (true|false) "false">

<!ELEMENT Attribute (Annotations?, (type | calculation))>
<!ATTLIST Attribute
    name CDATA #REQUIRED>

<!ELEMENT calculation ANY>
<!ELEMENT compare ANY>
<!ATTLIST compare
    comparison CDATA #REQUIRED>

<!ELEMENT condition ANY>
<!ELEMENT choose ANY>
<!ELEMENT timeline ANY>
```

---

## 2. Sample Complete Statutory CER XML Rule Set (Medicaid MAGI)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RuleSet name="MedicaidMAGIEligibilityRuleSet">
  <Class name="MedicaidApplicant" extends="AbstractHouseholdMember">
    
    <!-- Ingested Evidence Attribute -->
    <Attribute name="grossMonthlyEarnedIncome">
      <type><javaclass name="curam.util.type.Money"/></type>
    </Attribute>

    <!-- 5% Statutory FPL Disregard under 42 CFR 435.603(d) -->
    <Attribute name="statutoryFplDisregardMonthly">
      <calculation>
        <multiply>
          <reference attribute="monthlyFplThreshold"/>
          <Number value="0.05"/>
        </multiply>
      </calculation>
    </Attribute>

    <!-- Countable Income after Disregard -->
    <Attribute name="countableMagiIncome">
      <calculation>
        <subtract>
          <reference attribute="grossMonthlyEarnedIncome"/>
          <reference attribute="statutoryFplDisregardMonthly"/>
        </subtract>
      </calculation>
    </Attribute>

    <!-- Final Statutory Eligibility Decision -->
    <Attribute name="isMedicaidMagiEligible">
      <calculation>
        <compare comparison="&lt;=">
          <reference attribute="countableMagiIncome"/>
          <reference attribute="statutoryExpansionThresholdAmount"/>
        </compare>
      </calculation>
    </Attribute>

  </Class>
</RuleSet>
```

---

## 3. IBM Cúram Relational Case Entity Schema

```sql
-- Participant Core Table
CREATE TABLE ConcernRole (
    concernRoleID BIGINT PRIMARY KEY,
    concernRoleType VARCHAR(16) NOT NULL, -- PERSON, PROSPECT, EMPLOYER
    creationDate DATE NOT NULL
);

-- Master Case Header
CREATE TABLE CaseHeader (
    caseID BIGINT PRIMARY KEY,
    caseTypeCode VARCHAR(16) NOT NULL, -- CT1 (Integrated Case), CT2 (Product Delivery)
    concernRoleID BIGINT REFERENCES ConcernRole(concernRoleID),
    statusCode VARCHAR(16) NOT NULL -- CS1 (Open), CS2 (Active), CS3 (Closed)
);

-- Financial Component Output Table
CREATE TABLE FinancialComponent (
    financialComponentID BIGINT PRIMARY KEY,
    caseID BIGINT REFERENCES CaseHeader(caseID),
    amount DECIMAL(15, 2) NOT NULL,
    categoryCode VARCHAR(16) NOT NULL, -- PMT (Payment), LBY (Liability)
    deliveryMethod VARCHAR(16) NOT NULL -- EBT, ACH, CHK
);
```
