---
title: "Hacking"
url: "https://wiki.eveuniversity.org/Hacking"
pageid: 511
source: "EVE University Wiki"
categories: ["Exploration"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Hacking

- Hacking** is used to access Container structures in **relic and data sites**, **chemical labs** as well as mission given by Agents.

1. # Hacking

The goal of hacking is to **find and disable the Container’s System Core**. You do this by maneuvering a Virus through the board of nodes that represents the Container’s electronics.

Nodes are:
- if explored
- if adjacent to explored nodes
- gray if neither explored or adjacent to explored nodes

Clicking on a  node will reveal its contents: if the node is empty, it will turn  and allow you to further explore adjacent nodes.

If the new node is empty it will briefly display a number between 1 and 5. The number is the distance to the nearest node with a System Core, Utility Subsystem or Data Cache.

Number:
- 1 means an adjacent node is a System Core, Utility Subsystem or Data Cache
- 2, 3 and 4 mean the nearest System Core, Utility Subsystem or Data Cache is respectively 2, 3 and 4 nodes away
- 5 means you are 5 or more nodes away from the nearest System Core, Utility Subsystem or Data Cache

The numbers 1-5 don't tell you how distant you are from the nearest Defensive Subsystem.

Instead of being empty, a node may contain:
- a **System Core**
- a **Defensive Subsystem**
- a **Utility Subsystem**
- a **Data Cache**

  1. # System Core
  - Finding and disabling the System Core is the goal of hacking.**

| Difficulty
! scope="col" | System Core
! scope="col" | Firewall
! scope="col" | Anti-Virus 
! scope="col" | Resto. Node
! scope="col" | Suppressor |
| :--- |
| Very Easy |
| Easy |
| Medium |
| Hard |
| Hardest |

<references>
</references>

System Cores, Defensive Subsystems and your Virus have:
- **Coherence** () which is their health
- **Strength** () which is their attack power

When you click on the System Core or Defensive Subsystem your Virus will attack. Attacking is turn-based:
# your Virus attacks, lowering the System's Coherence by your Virus Strength; and then
# the System Core or Defensive Subsystem retaliates if it survived the attack.

When you reduce the System's Coherence to 0, it is disabled and removed from the board.

You fail a hack when:
- your Virus Coherence reaches 0
- the hacking window is closed for any reason, such as moving too far away from the Container structure or initiating warp during an active hack.

If you fail the hack:
- twice, a Data or Relic Site Container structure will be destroyed (with a few exceptions, such as the Storage Depots in Sleeper Caches)
- once, a Covert Research Facility Container structure will be destroyed and deal a large amount of explosive damage to all ships in range
- once, a Sleeper Cache will release a deadly toxic gas, activate turrets or put up other obstacle. Specific information can be found on the respective Sleeper Cache pages.
- once, any hackable container in the **Observatory Infiltration** site will activate lockdown
- once, the **AEGIS Encrypted Key Storage** will spawn a hostile response fleet.

  1. # Defensive Subsystems
  - Defensive Subsystems prevent you from exploring adjacent nodes until they are disabled.**

| - |  | **Firewalls** have high Coherence and low Strength. |
| :--- | :--- | :--- |
|  | **Anti-Virus** have low Coherence, but high Strength. |  |
|  | **Restoration Nodes** give 20 extra Coherence to a random Defensive Subsystem at the end of each turn (though never to the System Core). They are a high priority target. |  |
|  | **Virus Suppressors** lower your Virus Strength by 15. Your Virus Strength cannot go below 10. They are a high priority target. |  |

  1. # Utility Subsystems
  - Utility Subsystems** assist you in disabling the System Core and Defensive Subsystems.

When you click the Utility Subsystem it will be added to a free utility slot.

Activate the Utility Subsystem by clicking on it in your utility belt. They can also be activated by pressing the number keys "1", "2" etc. The number of utility belt slots depends on your Analyzer module.

| - |  | **Self Repairs** increase your Virus Coherence by 5-10 each turn for the three turns. Use it immediately as your Virus doesn't have a maximum Coherence value. Appears in all categories of hacking difficulty. |
| :--- | :--- | :--- |
|  | **Kernel Rots** reduce a System’s Coherence by 50%. Use it on high Coherence Systems. |  |
|  | **Polymorphic Shields** nullify the next two System attacks against your Virus. Use it before attacking high Strength Systems. |  |
|  | **Secondary Vectors** reduce a System’s Coherence by 20 each turn for three turns. Use it against a Suppressor Defensive Subsystem. |  |

  - Self Repairs** appears in all categories of hacking difficulty.

  - Kernel Rot** only appears in Very Easy and Easy hacks by chance from opening Data Caches, and naturally appears in Medium hacking difficulty and up.

  - Polymorphic Shield** appears in Medium hacking difficulty and up.

  - Secondary Vector** appears in Hard hacking difficulty and up.

  1. # Data Caches

| - |  | **Data Caches** can contain either a Defensive or Utility Subsystem. |
| :--- | :--- | :--- |

Data Caches have a 50-50 probability of containing a Defensive or a Utility Subsystem.

Open a Data Cache by clicking on it. Open them only as a last resort.

1. # Skills
- : Required skill for the use of Relic Analyzer modules. Gives +10 Virus Coherence per level.
  - Relic Analyzers require Archaeology, and are a fairly cheap mid-slot module used to interact with Container structures. A good amount of your income as an explorer will come from accessing these Container structures, so note this skill's importance!
  - Higher skill levels makes hacking Relic Site Container structures easier, with  allowing you to use the powerful Relic Analyzer II module. Explorers should considering training Archaeology to V, especially if they intend to hack Relic Sites in **NullSec** or **Wormholes**.
- : Required skill for the use of Data Analyzer modules. Gives +10 Virus Coherence per level.
  - *A la* Archaeology, Data Analyzers require Hacking, and open Container structures found in Data Sites, Chemical Labs and Ghost Sites.  has slightly higher requirements than Archaeology I, but make sure you get both skills, so that you can hack any sites you find.
  - Also like Archaeology, higher skill levels make hacking easier, and  will give you access to the Data Analyzer II module, which gives better bonuses, and is needed for Data Sites in NullSec or Wormholes.

1. # Ships and equipment

  1. # Ships
Hacking can be done in any ship that has mid slots for Data and/or Relic Analyzers. However, exploration ships have a role bonus for both Virus and scan Strength.

Each Empire's Tech 1 Exploration Frigate has a role bonus of +5 Virus Strength to both Data and Relic Analyzers. These ships also get an 7.5% (37.5% max) increase to scan strength per racial frigate level, which helps in scanning down Cosmic Signatures. The Navy Exploration frigate is a small upgrade with more defense and movement speed at the tradeoff of greater cost. 

- /
- /
- /
- /

Covert Operation ships are the direct upgrade from Tech 1 Exploration Frigates. They get a +10 bonus to Virus Strength, +10% (50% max) per level bonus to scanning, and can use Covert Ops Cloaking Device II.

- 
- 
- 
- 
- 

The **Sisters of EVE** faction ships all have a +10 bonus to Virus Strength, a 37.5% role bonus to scanning, and both the Astero and the Stratios can use a Covert Ops Cloaking Device II. They also get bonus to armor resists, energy turrets and drones making them capable combat crafts. They have lower skill requirements than Covert Operation ships, but they are more expensive than Covert Operation ships.

- Frigate.  (CPU is low, making it hard to fit an Expanded Probe Launcher.)
- Cruiser.
- Battleship. Role Bonus: 50% bonus to Core and Combat Scanner Probe strength. Cannot fit a Covert Ops Cloaking Device II.

  - Strategic cruisers** can be fitted with the **Covert Reconfiguration** subsystem that gives them 10% per level scan bonus, +10 Virus Strength, and the ability to use Covert Ops Cloaking Device II. Strategic cruisers are very expensive ships.

- 
- 
- 
- 
  - Society of Conscious Thought** special edition frigate is given away yearly for capsuleer day events, making the price variable.

- has a +10 bonus to virus strength, a 37.5% bonus to both Core Scanner Probe strength and deviation, and a +2 bonus to ship warp core strength and can use a Covert Ops Cloaking Device making it a very slippery exploration vessel.
- /  /  have a bonus to Core Scanner Probe strength but not virus strength.

  1. # Ship equipment
Data Analyzer or Relic Analyzer allow you to hack Data and Relic Sites. There is no additional high, mid or low slot equipment to make hacking easier.

Full list of normally used scanning equipment:

| - | link=|]] | Data]] and **Chemical Lab** sites found while exploring.

The T1 module has a base 40 Virus Coherence and 20 Strength, with the T2 Version has an additional +20 Virus Coherence (60 total) and +10 Virus Strength (30 total) |
| :--- | :--- | :--- |
| link=|]] | Relic]] Sites

The T1 module has a base 40 Virus Coherence and 20 Strength, with the T2 Version has an additional +20 Virus Coherence (60 total) and +10 Virus Strength (30 total) |  |
| link=|]] | Data and Relic]] sites. They are more expensive then their specialized counterparts, have lower Virus Coherence and Strength, and smaller utility belt slots.

Integrated Analyzers get bonus Coherence from both Archaeology and Hacking skills as well as rigs and implants. |  |
| link=|]] | **Memetic Algorithm Bank** rig increases the Virus Coherence of both Data and Integrated Analyzers. The T1 rig increases the Coherence by +10, and the T2 version increases it by +20. Due to Calibration size and ISK cost, it is more cost-effective to have two T1 rigs than one T2 rig. |  |
| link=|]] | **Emission Scope Sharpener** rig increases the Virus Coherence of both Relic and Integrated Analyzers. The T1 rig increases the Coherence by +10, and the T2 version increases it by +20. Due to Calibration size and ISK cost, it is more cost-effective to have two T1 rigs than one T2 rig. |  |

The slot 9 implants that improve Virus Coherence and Strength.

| - style="background-color: var(--background-color-warning-subtle);"
! Implant 
! Effect |
| :--- |
| Poteque 'Prospector' Archaeology AC-905 |
| Poteque 'Prospector' Hacking HC-905 |
| Neural Lace 'Blackglass' Net Intrusion 920-40 |

The slot 10 EY-1005 implant improves Virus Coherence.

| - style="background-color: var(--background-color-warning-subtle);"
! Implant 
! Effect |
| :--- |
| Poteque 'Prospector' Environmental Analysis EY-1005 |

1. # Tips and Tricks
- **Explore the board as much as possible before attacking a Defensive Subsystem.** You may just stumble onto the System Core early! Restoration Nodes and Virus Suppressors are the exception to this though, as they should be removed from the board as soon as possible.
- **Always pick up Utility Subsystems as soon as they are exposed.** If you keep exploring without snagging these, a Defensive Subsystem might pop up and cut off your access to them!
- **Be careful of where you are clicking.** It is quite common for one to blitz through a site and unintentionally discover the System Core or a Utility Subsystem, only to then click on another node to reveal a Defensive Subsystem, blocking off access to it. Rush only when you are certain that what you need is unlikely to spawn on that area of the grid.
- The utility subsystem 'Secondary Vector' can be used to clear Virus Suppressors and Antiviruses from the board without sustaining damage, as such it is advised to hold on to them unless there is no other option.
- **Always use a Self Repair as soon as you find it.** It increases your Virus Coherence, so there is no gain in waiting.
- **Don’t open Data Caches until you’ve fully explored all their adjacent nodes.** You don’t want your exploration to be cut off by an unexpected Defensive Subsystem!
  - Difficult hack's Data Caches might expose Restoration Nodes and Suppressors. **Leave opening Data Caches as a last resort.**
- On this note, if you are low on coherence and have already discovered the System Core, opening Data Caches is completely safe assuming:
  - 1. The Data Cache is **NOT** adjacent to the System Core, as revealing a Defensive Subsystem here will block off the System Core and almost certainly render the hack forfeit.
  - 2. The hack being attempted is **NOT** a red core (Hard) hack. In yellow (Medium) hacks and below, none of the Defensive Subsystems will directly affect your ability to destroy the System Core, as Restoration Nodes cannot heal the System Core. On a Hard hack, it can risk spawning Virus Suppressors, which will reduce your virus strength and possibly fail the hack. However, if one feels that the risk is worth it, by all means, go ahead.
- **Use the 1-5 numbers to guide your movement** around the board.  For example, if you're approaching an edge or corner of the grid, and the number 5 shows up, then trying to explore anything towards that corner/edge is not useful, because you know that there cannot be anything good within 5 nodes.  In general, you want to click in directions that make the numbers smaller. Because the numbers disappear as you move along, you need to remember where there were 5's, so you know which areas not to bother going back to later.
- **Use the Rule of Six**. This rule is slightly complicated, but can make your life when hacking much easier. The rule is that if you have a node that has six edges leading away from it ( a "complete" node with no missing nodes in the hexagon around it), then that node is guaranteed to 1) Have no Defensive Subsystems in it OR 2) be adjacent to the System Core. What that means in practice is that you can use these squares to move safely through the board, and any Defensive Subsystems you find tell you where the System Core is.  It is usually worthwhile to try to reach and use areas of the map with many of these "complete" nodes when hacking. You can find a video tutorial [here](https://www.youtube.com/watch?v=h5uQC74VvVQ).
- **Rule of 8, or "Before 8 it's Bait"**. The core is always placed at least 8 grid-spaces (including empty spaces) away from the starting point. If such placement is impossible, the core is placed randomly anywhere on the board.
