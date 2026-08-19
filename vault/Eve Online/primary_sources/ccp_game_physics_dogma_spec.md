---
title: "CCP Games Canonical Dogma Physics & Combat Mathematics Specification"
source_authority: "CCP Games Game Engine Mechanics & Dogma Subsystem"
harvested_at: "2026-08-19T14:35:14Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_DOGMA_PHYSICS_VERIFIED"
---

# CCP Games Canonical Dogma Physics & Combat Mathematics

## 1. Module Stacking Penalty Formula

When multiple modules or rigs affect the same dogma attribute, CCP applies a multiplicative stacking penalty function:

$$S(n) = e^{-(n-1)^2 / 7.1289}$$

### Exact Empirical Multiplier Values:
- **Module 1 (n=1)**: S(1) = 1.0000 (100.0% Effectiveness)
- **Module 2 (n=2)**: S(2) = e^(-1/7.1289) approx 0.8691 (86.91% Effectiveness)
- **Module 3 (n=3)**: S(3) = e^(-4/7.1289) approx 0.5710 (57.10% Effectiveness)
- **Module 4 (n=4)**: S(4) = e^(-9/7.1289) approx 0.2830 (28.30% Effectiveness)
- **Module 5 (n=5)**: S(5) = e^(-16/7.1289) approx 0.1060 (10.60% Effectiveness)
- **Module 6 (n=6)**: S(6) = e^(-25/7.1289) approx 0.0299 (2.99% Effectiveness)

---

## 2. Gun Turret Hit Chance & Tracking Equation

$$\text{HitChance} = 0.5^{\left( \left(\frac{\text{Angular Velocity} \times \text{Signature Resolution}}{\text{Tracking Speed} \times \text{Target Signature Radius}}\right)^2 + \left(\frac{\max(0, \text{Distance} - \text{Optimal Range})}{\text{Falloff}}\right)^2 \right)}$$

- **At Optimal Range with Zero Transversal**: Hit Chance = 1.0 (100%)
- **At Optimal + Falloff with Zero Transversal**: Hit Chance = 0.5 (50%)
- **At Optimal + 2x Falloff**: Hit Chance = 0.5^4 = 0.0625 (6.25%)
