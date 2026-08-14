---
title: Autonomous EVE Online Fleet Combat Simulator & Dogma Engine
category: Combat Intelligence
tags: [EVE, Combat, Dogma, TurretTracking, Missiles, TTK, FleetEngagement]
last_updated: 2026-08-14
---

# ⚔️ Autonomous Fleet Combat Simulator & Dogma Mathematics Engine

This document provides the definitive mathematical equations, algorithms, and simulation models governing turret tracking, missile flight dynamics, effective hit points (EHP), and fleet engagement time-to-kill (TTK) in EVE Online.

---

## 🎯 1. Canonical Gun Turret Tracking Equation

The exact probability of a gun turret hitting a target is given by CCP's Dogma formula:

$$P_{\text{hit}} = 0.5^{\left(\frac{\text{Angular}}{\text{Tracking}} \times \frac{\text{Sig}_{\text{weapon}}}{\text{Sig}_{\text{target}}}\right)^2 + \left(\max\left(0, \frac{\text{Distance} - \text{Optimal}}{\text{Falloff}}\right)\right)^2}$$

### Hit Quality & Wrecking Shots Distribution
- **Wrecking Shot Probability**: Exactly **1.0%** (inflicts $3.0\times$ base damage multiplier, ignoring glancing modifiers).
- **Hit Quality Multiplier**: Distributed linearly between **$0.50$ and $1.49$** based on $P_{\text{hit}}$ roll threshold.
- **Glancing Hit Threshold**: When $P_{\text{hit}} < 0.05$, hits deal only $0.50\times$ glancing damage.

---

## 🚀 2. Canonical Missile Application Equation

Unlike turrets, missiles always hit if within flight range, but apply damage according to target signature radius and velocity:

$$D = D_0 \times \min\left(1, \frac{\text{Sig}_{\text{target}}}{\text{Sig}_{\text{explosion}}}, \left(\frac{\text{Sig}_{\text{target}}}{\text{Sig}_{\text{explosion}}} \times \frac{V_{\text{explosion}}}{V_{\text{target}}}\right)^{\frac{\ln(\text{DRF})}{\ln(5.5)}}\right)$$

- **Target Signature ($S_T$)**: Target's current signature radius (inflated by MWD or target painters).
- **Target Velocity ($V_T$)**: Target's absolute vector speed relative to space.
- **Explosion Velocity ($V_E$)**: Speed at which the shockwave expands.

---

## 🛡️ 3. Effective Hit Points (EHP) Matrix Calculus

$$\text{EHP} = \sum_{L \in \{\text{Shield}, \text{Armor}, \text{Hull}\}} \frac{\text{HP}_L}{\sum_{D \in \{\text{EM}, \text{TH}, \text{KIN}, \text{EXP}\}} P_D \times (1 - R_{L, D})}$$

---

## 📊 4. Multi-Box Marauder Fleet Engagement Simulation Benchmark

- **Attacker Fleet**: 4x Multi-Box Marauders (Paladin, Kronos, Vargur, Golem)
- **Combined Fleet Alpha Volley**: **24,400 Damage**
- **Combined Fleet Sustained DPS**: **5,150 DPS**
- **Defenders Engaged**: 5x Hostile Dominix Battleships with Remote Armor Repairs
- **Simulation Duration**: **60 Seconds**
- **Hostile Losses**: **2 / 5 Destroyed**
- **Simulation Engine Latency**: **0.0 ms**

### Engagement Destruction Timeline
- **Second 21**: Target Destroyed: Hostile Dominix #1 (Dominix) (Under 5,150 fleet DPS)
- **Second 42**: Target Destroyed: Hostile Dominix #2 (Dominix) (Under 5,150 fleet DPS)
