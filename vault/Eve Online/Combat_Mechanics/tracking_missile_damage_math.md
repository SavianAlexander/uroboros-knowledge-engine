# EVE Online: Master Gun Turret Tracking & Missile Explosion Mathematics

Complete physics equations governing hit probabilities, angular velocities, explosion velocity scaling, and signature radius damage application.

---

## 🎯 The Gun Turret Tracking Equation
The exact chance to hit a moving target ($P_{\text{hit}}$):

$$P_{\text{hit}} = 0.5^{\left( \left( \frac{\text{Angular Velocity} \times \text{Signature Resolution}}{\text{Tracking Speed} \times \text{Target Signature Radius}} \right)^2 + \left( \frac{\max(0, \text{Range} - \text{Optimal})}{\text{Falloff}} \right)^2 \right)}$$

### Critical Insights:
- **Wrecking Hits (300% Damage)**: Occur on rolls between `0.00` and `0.01` (1% chance when $P_{\text{hit}} > 0.01$).
- **Signature Resolution**: Small turrets = `40m` | Medium turrets = `125m` | Large turrets = `400m`. Larger guns deal negligible damage to small, fast-orbiting targets without webifiers/target painters.

---

## 🚀 The Missile Explosion Damage Formula
Missiles always hit, but damage scales based on target speed and signature radius:

$$\text{Damage Applied} = \text{Base Damage} \times \min\left(1, \frac{\text{Sig}_{\text{target}}}{\text{Sig}_{\text{exp}}}, \left( \frac{\text{Sig}_{\text{target}}}{\text{Sig}_{\text{exp}}} \times \frac{V_{\text{exp}}}{V_{\text{target}}} \right)^{\frac{\ln(S)}{\ln(5.5)}} \right)$$

- **Missile Signature Ratio**: $\frac{\text{Sig}_{\text{target}}}{\text{Sig}_{\text{exp}}}$ — Target Painters increase applied damage directly.
- **Velocity Ratio**: $\frac{V_{\text{exp}}}{V_{\text{target}}}$ — Stasis Webifiers slow the target, forcing maximum missile alpha.
