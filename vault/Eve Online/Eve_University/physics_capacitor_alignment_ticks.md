# EVE University: Deep Physics — Alignment Server Ticks & Capacitor Calculus

Mathematical formulas governing ship physics, agility tick rounding, capacitor curves, and thermodynamics.

---

## ⏱️ Sub-warp Alignment & Server Tick Equations
The exact time to reach 75% max velocity in seconds ($t_{\text{align}}$):

$$t_{\text{align}} = \frac{-\ln(0.25) \times \text{Mass (kg)} \times \text{Inertia Modifier}}{1,000,000} \approx \frac{1.386294 \times \text{Mass} \times \text{Inertia}}{10^6}$$

### ⚡ Server Tick Rounding (1.0s Intervals):
$$\text{True Align Time} = \lceil t_{\text{align}} \rceil \text{ seconds}$$

- **Instawarp Rule (< 2.0s align)**: If $t_{\text{align}} < 2.00\text{s}$, the ship enters warp on tick 2, making it **impossible for enemy gunners to lock or point** (e.g. Stiletto, Ares, Prowler).

---

## 🔋 Capacitor Regeneration Physics & 25% Peak Calculus
Capacitor does not recharge linearly. The instantaneous recharge rate in GJ/second:

$$\frac{dC}{dt} = \frac{10 \times C_{\text{max}}}{T_{\text{recharge}}} \times \left( \sqrt{\frac{C}{C_{\text{max}}}} - \frac{C}{C_{\text{max}}} \right)$$

### 📈 The 25% Peak Recharge Rule:
$$\text{Peak Capacitor Recharge Rate} = 2.5 \times \frac{C_{\text{max}}}{T_{\text{recharge}}} \text{ GJ/second}$$

- **Critical Capacitor Threshold**: Peak energy generation occurs when the capacitor is at **25.0% capacity**. Below 25%, energy recovery drops off rapidly towards zero.

---

## 🌡️ Thermodynamics & Overheating Math
- **Overheating Buffs**: `+15% Turret Rate of Fire`, `+20% Shield Boost Amount`, `+20% Remote Rep`, `+10% MWD Velocity`.
- **Heat Dispersion**: Heat damage spreads to adjacent module slots (50% probability) and secondary slots (25% probability). Placing high-heat modules next to passive modules acts as a **heat sink buffer**.
