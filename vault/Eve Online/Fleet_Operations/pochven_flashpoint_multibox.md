# Pochven Observatory Flashpoint (OFP) Multi-Box Blueprint

The highest liquid ISK printing PvE engine in EVE Online (3.5 Billion ISK per site payout).

---

## 💰 Observatory Flashpoint (OFP) Metrics
- **Target Fleet Size**: **Exactly 15 Pilots** (Payout drops if > 15 pilots on grid).
- **Site Payout**: **3.5 Billion ISK Total** ($pprox$ **233.3 Million ISK per pilot** per site).
- **Site Clear Duration**: **12 – 15 Minutes**.
- **Net Hourly Yield**: **~850 Million to 1.1 Billion ISK/hr per pilot**.

---

## 🚀 15-Box Optimal Fleet Archetype
```mermaid
graph TD
    subgraph "15-Man Multi-Box OFP Fleet Composition"
        D1["👑 4x Paladin (Mega Pulse Laser II + Conflagration M)"]
        D2["💥 4x Kronos (Neutron Blaster Cannon II + Void M)"]
        D3["🎯 4x Vargur (800mm Repeating Cannon II + Hail M)"]
        Logi["🛡️ 3x Nestor (Spider-Tanking Remote Armor Reps + Cap Chain)"]

        D1 -->|Bastion Firepower| Boss["Triglavian Stellar Transmuter Boss"]
        D2 -->|Point-Blank DPS| Boss
        D3 -->|Web & Tracking| Boss
        Logi -->|Cross-Remote Reps| D1
        Logi -->|Cross-Remote Reps| D2
        Logi -->|Cross-Remote Reps| D3
    end
```
