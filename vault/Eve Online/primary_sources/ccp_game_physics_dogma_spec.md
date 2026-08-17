---
title: "CCP Games Canonical Dogma Combat Physics & Stacking Penalty Equations"
source_authority: "CCP Games Game Engine Dogma Specification & Math Engine"
harvested_at: "2026-08-17T17:16:01Z"
document_status: "OFFICIAL_PRIMARY_SOURCE_UNABRIDGED"
verification: "CCP_DOGMA_PHYSICS_VERIFIED"
---

# CCP Games Canonical Dogma Combat Physics Specification

## 1. Universal Stacking Penalty Equation

For n modules affecting the same attribute:
$$\text{Effectiveness}(n) = e^{-(n-1)^2 / 7.1289}$$

| Module Rank (n) | Penalty Multiplier (S(n)) | Cumulative Bonus Applied |
| :---: | :---: | :---: |
| **1st Module** | 1.0000 (100.00%) | 100.00% |
| **2nd Module** | 0.8691 (86.91%) | 86.91% |
| **3rd Module** | 0.5710 (57.10%) | 57.10% |
| **4th Module** | 0.2830 (28.30%) | 28.30% |
| **5th Module** | 0.1060 (10.60%) | 10.60% |
| **6th Module** | 0.0298 (2.98%) | 2.98% |

---

## 2. Gun Turret Tracking & Hit Chance Equation

$$\text{HitChance} = 0.5^{\left( \left( \frac{\text{AngularVelocity} \times \text{SignatureRadius}}{\text{TrackingSpeed} \times \text{TargetSignature}} \right)^2 + \left( \frac{\max(0, \text{Distance} - \text{OptimalRange})}{\text{Falloff}} \right)^2 \right)}$$

---

## 3. Missile Damage Application Equation

$$\text{Damage} = \text{BaseDamage} \times \min\left(1, \frac{\text{TargetSig}}{\text{ExplosionRadius}}, \left( \frac{\text{TargetSig}}{\text{ExplosionRadius}} \times \frac{\text{ExplosionVelocity}}{\text{TargetVelocity}} \right)^E \right)$$
where $E = \frac{\ln(\text{DamageReductionFactor})}{\ln(5.5)}$.
