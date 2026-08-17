---
title: "NPC damage types"
url: "https://wiki.eveuniversity.org/NPC_damage_types"
pageid: 521
source: "EVE University Wiki"
categories: ["NPCs", "PvE"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# NPC damage types

There are four different **damage types** in EVE:
- Electromagnetic (EM)
- Kinetic
- Thermal
- Explosive

All weapons in EVE do at least one (often two) of these damage types, and every ship has different **resistances** against each. Understanding damage types helps you to survive longer and deal more damage to enemy ships:
- If you know that your enemy uses weapons which deal a particular damage type, you can fit modules to your ship to increase your resistance to that damage type, making your enemy's weapons less effective against you.
- Conversely, if you know that your enemy's ship has a low resistance to a particular damage type, you can use weapons which deal that specific damage type, making them more effective.
{{#css:
table.damage {
 font-size: 90%;
 text-align: center; 
}

table.damage tr th {
 background-color: var(--background-color-warning-subtle);
 padding: 0.2em 0.5em;
 white-space: nowrap; 
}

table.damage tr td {
 padding: 0.2em 0.5em; 
}
	
table.npc tr th:first-child,
table.damage tr td:first-child {
 text-align: left; 
}

}}

|  | Native resistance | Weapon damage |
| :--- | :--- | :--- |
| Shields]] | Armor]] | Lasers]] | Hybrids]] | Projectiles]] | Disintegrators]] | **Drones** | **Missiles** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 32px|link=|EM damage}}]] EM | - - | + + | Yes (60%) | Yes | Yes (Amarr) | Yes |  |
| 32px|link=|Thermal damage}}]] Thermal | - | + | Yes (40%) | Yes (40%) | Yes | Yes (60%) | Yes (Gallente) |
| 32px|link=|Kinetic damage}}]] Kinetic | + | - | Yes (60%) | Yes | Yes (Caldari) | Yes |  |
| 32px|link=|Explosive damage}}]] Explosive | + + | - - | Yes | Yes (40%) | Yes (Minmatar) | Yes |  |

Some points to note:
- "**Native resistance**" is a tech 1 ship's resistance to damage before any modules or rigs are fitted. For instance, without any modules or rigs, shields are most susceptible to EM damage and most resistant to explosive damage. However, keep in mind that it's possible (with the right modules) to compensate for a ship's weaknesses; and tech 2 ships follow their own patterns of native resistance.
- Thermal damage is not to be confused with heat damage, which is caused by **overheating** modules.
- **Energy turret**s (often called "lasers") do about 60% EM and 40% thermal damage. The exact proportions depend on the frequency crystals used.
- **Hybrid weapons** do about 60% kinetic and 40% thermal damage. The exact proportions depend on the ammunition type used.
- Each type of **projectile weapon** ammunition does two (sometimes three) different damage types (one of which is always kinetic).
- **Entropic Disintegrators** deal about 60% thermal and 40% explosive damage. The exact proportions depend on the plasma charge used.
- **Drones** from each of the four factions do one damage type each, but they have slightly different stats (for example, Caldari drones (kinetic) do less damage than Gallente drones (thermal), but are slightly faster).
- Each **missile** type comes in four variants, each doing one damage type. The variant have otherwise identical stats, although some missile-using ships have bonuses to one damage type (notably, many Caldari ships have a bonus to kinetic missile damage).
- The more "exotic" weapons in EVE (such as **smartbombs**, **bombs**, and **Doomsday** weapons) have variants for each damage type, which are generally otherwise equivalent.

1. # NPC damage breakdown
. You can see that he is weakest to explosive. Thus you would try to deal explosive damage. Because he deals explosive and kinetic, you would usually try fit resists against those. But in this case most try to avoid taking damage by orbiting close in an AB fit destroyer.]]
<onlyinclude>
Just like player ships, **NPC**s have different resistances for different damage types. However, NPCs tend to ignore the native resistance conventions of shields and armor, and instead have damage resistances which are specific to their faction. If you are **running missions** or **ratting**, it is helpful to know towards which damage the NPCs are weak and what damage they deal. This way you can can fit your ship accordingly and maximize your effectiveness against your chosen targets. You can see the resistances and damage types dealt in the attribute tab of an NPC if you open its info window. 

In general, all NPCs from a certain faction have similar damage profiles, making them much more predictable than player ships. Additionally, each faction only uses particular types of **electronic warfare**; this is also noted in the table below. Ship fitting tools like **PYFA** can simulate combat against rats of different factions, giving you even more fine-grained control over your fit. Please note that a few special NPCs don't follow the pattern of their faction.

{| class="wikitable damage npc"
! Faction
! Weaknesses
! Damage types dealt
! Electronic Warfare
|-
| **Angel Cartel**
| Explosive / Kinetic
| Explosive (62%) / Kinetic (22%)
| Target Painters
|-
| **Blood Raiders**
| EM / Thermal
| EM (50%) / Thermal (48%)
| Energy Neutralizers, Tracking Disruptors
|-
| **Guristas Pirates**
| Kinetic / Thermal
| Kinetic (79%) / Thermal (18%)
| ECM
|-
| **Guristas Pirates** (Homefronts)
| Kinetic / Thermal
| Kinetic (62.5%) / Thermal (37.5%)
| ECM
|-
| **Guristas Pirates** (**FOB**)
| Kinetic / EM
| Thermal (100%)
| ECM / Neut / Web / Scram
|-
| **Mordu's Legion**
| Kinetic / EM 
| Kinetic (70%) / Thermal (30%)
|
|-
| **Rogue Drones**
| EM/Thermal
| (varies) 
|
|-
| **Sansha's Nation**(missions / anomalies)
| EM / Thermal
| EM (53%) / Thermal (47%)
| Tracking Disruptors
|-
| **Serpentis**
| Kinetic / Thermal
| Thermal (55%) / Kinetic (45%)
| Sensor Dampeners
|-
| **CONCORD** 
| Kinetic / Thermal
| (Omni) 
| Kinetic (74%) / Thermal (26%)
|
|-
| **Khanid Kingdom**
| EM / Thermal
| Thermal / EM 
|
|-
| Mercenaries
| Kinetic / Thermal
| Kinetic / Thermal
|
|-
| **Sleepers**
| (Omni) 
| Thermal (60%) / Explosive (40%)
| (all except ECM) 
|-
| **Triglavian Collective**(invasions)
| Explosive / Thermal
| (Omni) 
</references>
</onlyinclude>

1. # External links
- [Damage Types](http://games.chruker.dk/eve_online/damage_types.php)
- [OGRank](http://www.ogrank.com/content/view/698/59/)
