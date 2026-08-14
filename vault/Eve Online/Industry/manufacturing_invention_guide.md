# EVE Online: Advanced T2 Invention & Manufacturing Guide

Mathematical equations for T2 blueprint invention probabilities, decryptor modifiers, and facility job run costs.

---

## 🎲 The T2 Invention Formula
$$\text{Invention Chance} = \text{Base Chance} \times \left(1 + \frac{\text{Encryption Skill Level}}{40} + \frac{\text{Datacore 1 Level} + \text{Datacore 2 Level}}{30}\right) \times \text{Decryptor Mod}$$

### Base Chances by Hull Class:
- **Frigates / Destroyers**: `40.0% Base Chance`
- **Cruisers / Battlecruisers / Industrials**: `34.0% Base Chance`
- **Battleships**: `30.0% Base Chance`

---

## 🧮 Decryptor Modifiers Matrix
| Decryptor Type | Success Probability Mod | Max Runs Modifier | ME Modifier | TE Modifier | Optimal Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Accelerant** | `+20.0%` | `+1 Run` | `+2 ME` | `+10 TE` | T2 Cruisers & HACs |
| **Attainment** | `+80.0%` | `+4 Runs` | `-1 ME` | `-2 TE` | High-volume Ammo / Drones |
| **Augmentation** | `+60.0%` | `+9 Runs` | `-2 ME` | `+2 TE` | Mass Drone Production |
| **Parity** | `+50.0%` | `+3 Runs` | `+1 ME` | `-2 TE` | T2 Modules & Hulls |
| **Process** | `+10.0%` | `+0 Runs` | `+3 ME` | `+6 TE` | High-cost T2 Hulls |
| **Symmetry** | `+0.0%` | `+2 Runs` | `+1 ME` | `+8 TE` | Balanced Production |
