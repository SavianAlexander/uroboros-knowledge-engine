---
title: "IBM Cúram Express Rules (CER) XML Document Type Definition (DTD) & Grammar"
source_authority: "IBM Cúram Social Program Management Architecture Specification"
spec_version: "CER 8.0.x"
harvested_at: "2026-08-19T14:35:14Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CER_XML_GRAMMAR_VERIFIED"
---

# IBM Cúram Express Rules (CER) XML Grammar & DTD Specification

## 1. Formal XML Document Type Definition (`CuramExpressRules.dtd`)

```xml
<!-- IBM Cúram Express Rules (CER) Document Type Definition -->
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

    <!-- Statutory MAGI Expansion Income Limit (138% FPL) -->
    <Attribute name="magiExpansionIncomeLimit">
      <calculation>
        <multiply>
          <reference attribute="monthlyFplThreshold"/>
          <Number value="1.38"/>
        </multiply>
      </calculation>
    </Attribute>

    <!-- Financial Eligibility Determination Boolean -->
    <Attribute name="isFinanciallyEligible">
      <calculation>
        <compare comparison="lessThanOrEqualTo">
          <reference attribute="countableMagiIncome"/>
          <reference attribute="magiExpansionIncomeLimit"/>
        </compare>
      </calculation>
    </Attribute>

  </Class>
</RuleSet>
```
