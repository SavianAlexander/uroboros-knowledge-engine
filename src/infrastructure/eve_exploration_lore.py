"""
EVE Online Exploration Signatures, Sleeper Caches & Faction Lore Engine.

Exhaustive references for:
- Cosmic Signatures, Relic/Data Sites, Ghost Sites & Sleeper Caches (Limited, Standard, Superior)
- Major NPC Empires, Pirate Cartels, Ancient Precursors & Capsuleer Lore Compendium

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


def generate_exploration_lore_markdown() -> list:
    created_files = []

    # 1. EXPLORATION SIGNATURES & SLEEPER CACHES
    exp_dir = os.path.join(VAULT_EVE_DIR, "Exploration")
    os.makedirs(exp_dir, exist_ok=True)
    exp_file = os.path.join(exp_dir, "exploration_signatures_guide.md")
    exp_md = """# EVE Online: Cosmic Signatures, Relic/Data Sites & Sleeper Caches

Exploration scanning mechanics, hacking minigame virus optimization, and site risk-reward profiles.

---

## 🔍 Cosmic Signature Classifications
| Site Category | Difficulty / Scan Strength | Mini-game Mechanics | Top High-Value Loot |
| :--- | :--- | :--- | :--- |
| **Ruins / Relic Sites** | Easy to Hard (Null-sec / C1-C3) | Relic Analyzer (Coherence / Attack) | T2 Rig Blueprints, Enhanced Logic Components, Intact Armor Plates |
| **Data Sites** | Easy to Moderate | Data Analyzer (Decryption subroutines) | Faction Blueprints, Decryptors, Datacores |
| **Covert Research (Ghost Sites)**| Extreme (Explosion Timer: 90s) | Instant hack required, failure detonates | High-grade Ascendancy Implants, 'WET' BPCs |
| **Limited Sleeper Cache** | High (Frigates only) | Multi-room puzzle / Hacker & Sentry traps | Augmented Drone BPCs, 'Storyline' Modules |
| **Standard Sleeper Cache** | Very High (Cruiser / T3C) | Remote defense grid deactivation | High-Grade Snake/Slave Implants, 250M+ ISK |
| **Superior Sleeper Cache** | Maximum (T3C / Stratios) | High explosive shockwaves & spatial rifts | Polarized Weapon BPCs, Elite Cybernetics, 600M+ ISK |

---

## 💻 Hacking Module Benchmarks
- **T2 Relic Analyzer**: `60 Coherence` | `40 Virus Strength`
- **Zeugma / Frostline Integrated Analyzer**: `50 Coherence` | `40 Virus Strength` (Dual Data + Relic)
- **Blackglass Subspace Transmuter Rig**: **+20 Virus Strength to Data**, enables 1-hit firewall hacking.
"""
    with open(exp_file, "w", encoding="utf-8") as f:
        f.write(exp_md)
    created_files.append(exp_file)

    # 2. FACTION & PIRATE LORE COMPENDIUM
    lore_dir = os.path.join(VAULT_EVE_DIR, "Lore")
    os.makedirs(lore_dir, exist_ok=True)
    lore_file = os.path.join(lore_dir, "npc_factions_and_pirate_lore.md")
    lore_md = """# EVE Online: Major NPC Empires, Pirate Cartels & Ancient Lore Compendium

Canonical historical backgrounds, sovereign philosophies, and organizational structures of New Eden's major factions.

---

## 👑 The Four Major Empires
1. **Amarr Empire**: The oldest and largest empire in New Eden, ruled by the Empress and the Theology Council. Driven by the divine decree of "The Reclaiming". Primary weapons: *Energy Turrets, Heavy Armor Tanks*.
2. **Caldari State**: A hyper-capitalist corporatocracy governed by the Chief Executive Panel (CEP) representing the 8 Megacorporations (Kaalakiota, Sukuuvestaa, Nugoeihuvi, etc.). Primary weapons: *Missiles, Railguns, Heavy Shield Extenders*.
3. **Gallente Federation**: The only true democracy in New Eden, championing individual freedom, civil liberties, and multiculturalism. Primary weapons: *Autonomous Combat Drones, Blasters, Active Armor Repair*.
4. **Minmatar Republic**: A proud tribal federation composed of 7 tribes (Brutor, Sebiestor, Vherokior, Thukker, Krabal, Nefantar, Starkmanir). Born from slave rebellion against Amarr. Primary weapons: *Projectile Autocannons, Artillery, Speed & Agility*.

---

## ☠️ The Major Pirate Cartels
- **Blood Raider Covenant**: Led by Omir Sarikoo. Fanatical religious splinter faction of the Sani Sabik, practicing human blood harvesting.
- **Sansha's Nation**: Founded by Master Kuvakei. A cybernetically networked hive-mind society utilizing captured True Slaves.
- **Guristas Pirates**: Founded by former Caldari naval commanders 'The Rabbit' (Korako Kosakami) and 'Fatal'. Masters of drone swarms and missile strikes.
- **Angel Cartel**: Controlled by the Dominations in Curse and Heaven. The most organized and technologically advanced criminal syndicate.
- **Serpentis Corporation**: Founded by Salvador Sarpati. Deep pharmaceutical empire controlling the galaxy's booster and illegal drug cartels.

---

## 🌌 Ancient Precursors & Enigmas
- **The Jove Empire**: Hyper-advanced human civilization that succumbed to the Jovian Disease; creators of capsule technology.
- **Triglavian Collective**: Ancient bio-adaptive human sub-clades residing in Abyss/Pochven worshipping the Flow of Vyraj.
- **The Drifters / Sleepers**: Networked consciousness originating from the Second Jovian Empire guarding ancient Megastructures.
"""
    with open(lore_file, "w", encoding="utf-8") as f:
        f.write(lore_md)
    created_files.append(lore_file)

    return created_files
