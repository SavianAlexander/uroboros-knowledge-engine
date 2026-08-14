# EVE Online: Dynamic System Cost Index (SCI) & Manufacturing Calculus

Formulation of industrial manufacturing job fees, duration scaling, and material efficiency.

---

## 💰 Dynamic System Cost Index (SCI) Formula
$$\text{SCI}_{\text{activity}} = \sqrt{\frac{\text{Gross System Production (28 Days)}}{\text{Universe Gross Production (28 Days)}}}$$

### Exact Job Installation Fee Equation:
$$\text{Job Fee} = \text{Estimated Item Value (EIV)} \times \text{SCI} \times \text{Facility Cost Multiplier} \times (1 + \text{Facility Tax})$$

---

## ⏱️ Industrial Job Duration Scaling
$$\text{Job Duration} = T_{\text{base}} \times (1 - \text{TE}_{\text{Blueprint}}) \times (1 - 0.04 \times \text{Industry Skill}) \times \text{Structure Time Rig Multiplier}$$

- **Material Efficiency (ME 10)**: Conserves **10.0% of raw minerals/components**.
- **Time Efficiency (TE 20)**: Reduces base production duration by **20.0%**.
