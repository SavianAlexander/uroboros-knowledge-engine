"""
EVE University (UniWiki) Core Curriculum, Deep Game Physics & Career Playbooks Engine.

Exhaustive references derived from EVE University knowledge archives:
- Fleet Academy Curriculum (Fleet 101, Tackle 101, Logistics 101, EWAR 101, FC Commands)
- Sub-warp Alignment Server Ticks & Agility Mathematical Physics
- Capacitor Regeneration Physics & 25% Peak Recharge Calculus
- Thermodynamics & Module Overheating Heat-Spreading Equations
- Directional Scanner (D-Scan 14.3 AU) & Combat Probing Reconnaissance
- High-End Career Guides: Highsec Incursion Fleets & J-Space Wormhole Living

Ponytail: Zero-dependency stdlib implementation (os, sys, json, time).
"""

import os
import sys
import json
import time

VAULT_EVE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "vault",
    "Eve Online"
)
UNI_DIR = os.path.join(VAULT_EVE_DIR, "Eve_University")


def generate_eve_university_markdown(output_dir: str = UNI_DIR) -> list:
    os.makedirs(output_dir, exist_ok=True)
    created_files = []

    # 1. FLEET CURRICULUM 101
    fleet_file = os.path.join(output_dir, "eve_uni_fleet_curriculum_101.md")
    fleet_md = r"""# EVE University: Master Fleet Academy Curriculum (Fleet 101 - 105)

Standardized operational protocols and command vernacular across New Eden capsuleer fleets.

---

## 🗣️ Standard Fleet Command Terminology
- **"Align To [Celestial/Gate]"**: Turn ship and accelerate towards target without entering warp.
- **"Hold on Gate" / "Hold Cloak"**: Do not break session-change gate cloak (60s timer) until FC calls position.
- **"Jump, Jump, Jump"**: Immediate authorization to jump through gate/wormhole.
- **"Anchor on [Pilot]"**: Keep at range (500m - 1,500m) on the designated anchor ship with propulsion module on.
- **"Primary is [Target], Secondary is [Target]"**: Lock and apply maximum DPS to primary target; pre-lock secondary.
- **"Check, Check"**: Request for absolute comms silence for critical tactical broadcast.

---

## 🎯 Tackle 101 & Fast Interception
1. **Slingshot Maneuver**: Double-click away in reverse to force an orbiting kiter in a straight line, then overheat MWD straight into them for scramble.
2. **Spiral Approach**: Approach a turret gunship at an angle ($\approx 45^\circ$) rather than a straight line to maintain high transversal and minimize incoming damage.
3. **Point vs Scram**:
   - **Warp Disruptor (Long Point)**: 20-30km range, 1-2 point strength. Prevents warp but target MWD stays active.
   - **Warp Scrambler (Short Scram)**: 8-12km range, 2-3 point strength. **Shuts down Microwarpdrives & Micro Jump Drives**.

---

## 🛡️ Logistics 101 (Cap-Chain Dynamics)
- **Capacitor Chain**: Ships like Basilisk / Guardian send remote cap to each other. 2 incoming transfers yield more energy than 2 outgoing transfers consume, achieving **infinite cap stability**.
- **Broadcast Priority**: Broadcast for Shield/Armor reps when buffer reaches **80%** (gives logistics 2-3 seconds to lock and apply reps before hull breach).
"""
    with open(fleet_file, "w", encoding="utf-8") as f:
        f.write(fleet_md)
    created_files.append(fleet_file)

    # 2. DEEP PHYSICS: ALIGNMENT TICKS & CAPACITOR PEAK
    phys_file = os.path.join(output_dir, "physics_capacitor_alignment_ticks.md")
    phys_md = """# EVE University: Deep Physics — Alignment Server Ticks & Capacitor Calculus

Mathematical formulas governing ship physics, agility tick rounding, capacitor curves, and thermodynamics.

---

## ⏱️ Sub-warp Alignment & Server Tick Equations
The exact time to reach 75% max velocity in seconds ($t_{\\text{align}}$):

$$t_{\\text{align}} = \\frac{-\\ln(0.25) \\times \\text{Mass (kg)} \\times \\text{Inertia Modifier}}{1,000,000} \\approx \\frac{1.386294 \\times \\text{Mass} \\times \\text{Inertia}}{10^6}$$

### ⚡ Server Tick Rounding (1.0s Intervals):
$$\\text{True Align Time} = \\lceil t_{\\text{align}} \\rceil \\text{ seconds}$$

- **Instawarp Rule (< 2.0s align)**: If $t_{\\text{align}} < 2.00\\text{s}$, the ship enters warp on tick 2, making it **impossible for enemy gunners to lock or point** (e.g. Stiletto, Ares, Prowler).

---

## 🔋 Capacitor Regeneration Physics & 25% Peak Calculus
Capacitor does not recharge linearly. The instantaneous recharge rate in GJ/second:

$$\\frac{dC}{dt} = \\frac{10 \\times C_{\\text{max}}}{T_{\\text{recharge}}} \\times \\left( \\sqrt{\\frac{C}{C_{\\text{max}}}} - \\frac{C}{C_{\\text{max}}} \\right)$$

### 📈 The 25% Peak Recharge Rule:
$$\\text{Peak Capacitor Recharge Rate} = 2.5 \\times \\frac{C_{\\text{max}}}{T_{\\text{recharge}}} \\text{ GJ/second}$$

- **Critical Capacitor Threshold**: Peak energy generation occurs when the capacitor is at **25.0% capacity**. Below 25%, energy recovery drops off rapidly towards zero.

---

## 🌡️ Thermodynamics & Overheating Math
- **Overheating Buffs**: `+15% Turret Rate of Fire`, `+20% Shield Boost Amount`, `+20% Remote Rep`, `+10% MWD Velocity`.
- **Heat Dispersion**: Heat damage spreads to adjacent module slots (50% probability) and secondary slots (25% probability). Placing high-heat modules next to passive modules acts as a **heat sink buffer**.
"""
    with open(phys_file, "w", encoding="utf-8") as f:
        f.write(phys_md)
    created_files.append(phys_file)

    # 3. D-SCAN & COMBAT RECON MASTERY
    dscan_file = os.path.join(output_dir, "dscan_combat_recon_mastery.md")
    dscan_md = """# EVE University: Directional Scanner (D-Scan) & Combat Probing Mastery

Reconnaissance techniques for hunting, safe travel, and situational awareness across New Eden.

---

## 📡 Directional Scanner Mechanics (14.3 AU)
- **Maximum Scan Range**: `14.3 AU` (`2,147,483,647 km`)
- **Scan Angles**: `360°` (Full sphere) $\\rightarrow$ `180°` $\\rightarrow$ `90°` $\\rightarrow$ `60°` $\\rightarrow$ `30°` $\\rightarrow$ `15°` $\\rightarrow$ `5°` (Pinpoint cone).

### 🎯 Pinpointing Targets without Probes:
1. Scan at `360°` at 14.3 AU to detect ship hulls on grid in system.
2. Reduce slider to `5 AU` and rotate camera around celestials (Anomalies, Gates, Citadels).
3. Narrow angle to `5°` and align camera directly through target celestial to verify if the ship is stationed on that specific warp beacon.

---

## 🎯 Combat Scanner Probing Protocol
- **Probe Formation**: Pinpoint Spread (8 Probes centered around signature).
- **Scan Reduction Steps**: `4.0 AU` $\\rightarrow$ `2.0 AU` $\\rightarrow$ `1.0 AU` $\\rightarrow$ `0.5 AU` (Achieving 100% lock in **4 scan pulses**).
- **Virtue Implants**: Reduce required scan steps by 50% for near-instant warp-in locks.
"""
    with open(dscan_file, "w", encoding="utf-8") as f:
        f.write(dscan_md)
    created_files.append(dscan_file)

    # 4. WORMHOLE LIVING & INCURSION CAREERS
    careers_file = os.path.join(output_dir, "wormhole_living_incursion_careers.md")
    careers_md = """# EVE University: Highsec Incursion Communities & Wormhole Living Guide

Playbooks for high-tier group PVE, community running, and sovereign J-Space infrastructure.

---

## ⚔️ High-Sec Incursion Fleets (HQ Sites)
- **Primary Communities**: *Warp To Me (WTM)*, *The Ditanian Fleet (TDF)*, *The Outcasts*.
- **Site Archetype**: 40-man Headquarters (HQ) Sites (*Kundalini Manifest, Nation Rebirth, True Sansha Nation Fleet Staging*).
- **Fleet Composition**: 3-4 Remote Shield Basilisk/Scimitar Logi + 30 Battleship Gunships/HACs (Nightmare, Vindicator, Machariel, Paladin).
- **Payout**: **31,500,000 ISK + 7,000 CONCORD LP per site** (~**200M – 300M ISK/hour**).

---

## 🌌 Wormhole (J-Space) Living Playbook
1. **Static Hole Rolling**: Using mass-heavy Battleships/Megathrons with **Higgs Anchor Rigs** and 500MN MWD (oversized mass) to deliberately collapse entrance wormholes and spawn fresh statics.
2. **Wormhole Mass States**:
   - **Stage 1 (Fresh)**: `> 50% Mass remaining`
   - **Stage 2 (Destab)**: `10% - 50% Mass remaining`
   - **Stage 3 (Critical)**: `< 10% Mass remaining (Do not jump heavy hulls!)`
"""
    with open(careers_file, "w", encoding="utf-8") as f:
        f.write(careers_md)
    created_files.append(careers_file)

    return created_files
