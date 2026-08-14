# EVE Online: Official Dogma Engine & Module Stacking Penalty Calculus

The exact mathematical formulation utilized by the CCP Dogma game engine for diminishing returns on module stacking.

---

## 📐 The Dogma Stacking Penalty Equation
For the $n$-th module affecting the same statistic ($n \ge 1$):

$$S(n) = e^{-\frac{(n - 1)^2}{7.1289}} = e^{-\frac{(n - 1)^2}{2 \times (1.8879)^2}}$$

### 📊 Exact Efficiency Multipliers per Module:
| Module Rank ($n$) | Theoretical Formula | Exact Multiplier | Relative Effectiveness |
| :--- | :--- | :--- | :--- |
| **1st Module** | $S(1) = e^0$ | **1.000000** | **100.00%** |
| **2nd Module** | $S(2) = e^{-1/7.1289}$ | **0.869119** | **86.91%** |
| **3rd Module** | $S(3) = e^{-4/7.1289}$ | **0.571028** | **57.10%** |
| **4th Module** | $S(4) = e^{-9/7.1289}$ | **0.282956** | **28.30%** |
| **5th Module** | $S(5) = e^{-16/7.1289}$ | **0.105999** | **10.60%** |
| **6th Module** | $S(6) = e^{-25/7.1289}$ | **0.029991** | **3.00%** |
| **7th Module+**| $S(7) = e^{-36/7.1289}$ | **0.006408** | **< 0.64% (Hard Floor)**|

---

## 🛡️ Penalized vs Non-Penalized Modules
- **Penalized Modules**: Gyrostabilizers, Magnetic Field Stabilizers, Heat Sinks, Ballistic Control Systems, Magnetic/Shield/Armor Hardeners, Inertial Stabilizers, Overdrive Injectors, Tracking Enhancers.
- **Non-Penalized Modules**: Damage Control II, Reactive Armor Hardener, Reinforced Bulkheads, 1600mm Steel Plates, Large Shield Extenders, Ancillary Armor Repairers.
