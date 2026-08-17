---
title: "Tech 3 Production"
url: "https://wiki.eveuniversity.org/Tech_3_Production"
pageid: 113
source: "EVE University Wiki"
categories: ["Industry"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Tech 3 Production

1. # Introduction

Tech 3 ships - Strategic Cruisers and Tactical Destroyers - are made using materials obtained in **wormhole** space. As can be seen below there are four distinct manufacturing stages:
- React Fullerenes to form Hybrid Polymers
- Use Hybrid Polymers and Ancient Salvage to make Hybrid Tech Components
- Invent Tech 3 Hull and Subsystem BPC using Ancient Relics. This process is also sometimes called reverse engineering.
- Construct Tech 3 subsystems and hulls using the Hybrid Tech Components

The processes for manufacturing tactical destroyers and strategic cruisers differ only in the relic required for reverse-engineering, and in that tactical destroyers do not require Subsystems to be built. This page will otherwise discuss primarily strategic cruiser production.

1. # Naming Conventions

The naming convention of the gases used to manufacture Tech 3 items can be confusing. In the Regional Market window they are named "Fullerenes" (under "Manufacture and Research", "Gas Cloud Materials"). However the gases themselves are named "Fullerite" with a number, such as Fullerite-C28 (the most common) to Fullerite-C540 (only available in C5/C6 wormholes). When trying to make a filter in the inventory they are found under "Group", "Celestial", "Harvestable Cloud". Finally, there are items like "Methanofullerene" and "PPD Fullerene Fibers" which are actually reacted components ("Hybrid Polymers") made of fullerenes. In this wiki page, we will be using the market name "fullerene" to describe the gas material.

1. # Hybrid Polymer Reactions

This is the process by which the fullerene gases mined in wormhole space are transformed in Hybrid Polymer, which will themselves be transformed in Hybrid Tech Components (see below). The Polymer Reaction interface look like this:

  1. # Skills
The required skills are the same as for T2 (Hybrid) reactions:
- : 4% reduction of reaction time per skill level. Level 3 is needed for the Hybrid Polymer Reactions needed for T3 production.
- : One additional reaction slot per Level (from the one slot base allowance).
- : One additional reaction slot per level (for a maximum of 11 with both skills at 5).

  1. # Materials
- Polymer Reaction blueprints are seeded on the NPC market under *Reactions > Polymer Reactions*. As with other reactions these cannot be researched.
- Fullerenes are obtained by harvesting gas sites in w-space. See **Gas cloud harvesting#Fullerenes** for more details. Fullerenes are very bulky and shipping large quantities of these gases may become challenging, however they are treated as Ore for purposes of being carried by specialized cargo holds (such as via a **Miasmos**). Fullerenes can be compressed at a ratio of 10:1. This makes exporting fullerenes out of wormholes much easier, however decompression is imperfect and incurs a loss. See .
- Minerals are obtained from mining standard ores (either from Ores sites in w-space, or asteroid belts in k-space). Compared to Tech 2 manufacturing, very little minerals are actually required to manufacture Tech 3 ships and subsystems.
- Fuel blocks are also required. These can be manufactured from ice and PI commodities or purchased on the market.

  1. # Process
Polymer reactions are done in Refineries (Athanor and Tatara). The refinery needs a Standup Hybrid Reactor I service module online and can be rigged for material and time efficiency using T1 or T2 rigs. When looking for a suitable refinery, look in the Facility tab of the Industry window and mouse over facilities that show up in the Reactions column. You're looking for a facility that supports Hybrid Polymers:

Notes:
- The Standup Hybrid Reactor is not the same as the Standup Composite Reactor (which is used for producing T2 components and intermediates).
- In this screen capture, the facility has a bonus to production, but not to Hybrid Reactions.
- The System Cost Index will impact the job cost, and is calculated based on all reactions done in the system, not just on Hybrid reactions.

The process is the same as for other reactions:
- Choose Reaction formula
- Set number of runs
- Set input & output location
- Press Start
- After run time has passed, press deliver
- Repeat as necessary

After the reaction process the Hybrid polymer produced will typically have 40% or so of the feed materials volume, depending on the exact reaction and on the facility ME bonuses.

1. # Hybrid Tech Component Construction

These components are used to construct both the subsystems and the hulls. You can manufacture these in any citadel or station where construction is possible (where there is an online Standup Manufacturing Plant I).  The BPOs are available under *Blueprints > Manufacture & Research > Components > Subsystem Components* and may be researched & copied as normal. Normal facility bonuses apply. A rig (Advanced Component Manufacturing) can also be installed to speed up manufacturing or increase material efficiency.

  1. # Skills
Each Hybrid Tech Component BPO needs  trained at V and  trained to II and may require in addition one of the following skill
- II
- II
- II
- II
- II
- II
- II
- II

  1. # Materials
Construction of subsystem components is from two material sources:
- Ancient Salvage is obtained by salvaging **Sleeper** wrecks in w-space.
- Hybrid Polymers obtained from the reaction process as previously described.

1. # Invention of BPCs

This is the process by which T3 BPCs - for hulls and subsystems - are invented. This process is very similar to the process of T2 Invention. The Invention interface looks like this:

The initial object required is an ancient relic, retrieved from Relic sites in w-space. Ancient relics look very much like BPOs, except with a yellow background instead of a blue one. Unlike a BPO, however, they will be consumed during the Invention process.

There are six different types of ancient relics, each prefixed by a specific quality level (Intact, Malfunctioning or Wrecked, see below):

- Small Hull Section - used to invent a T3 destroyer BPC
- Hull Section - used to invent a T3 cruiser hull BPC
- Armor Nanobot - used to invent a Defensive Subsystem BPC
- Power Cores - used to invent a Core Subsystem BPC
- Thruster Sections - used to invent a Propulsion Subsystem BPC
- Weapon Subroutines - used to invent an Offensive Subsystem BPC

Each type of ancient relic comes in three different qualities, which determine the chances of success and the quality of the resulting BPC:
- Intact - highest chance of BPC invention (26% base chance of success, 20-run BPC)
- Malfunctioning - medium chance of BPC invention (21% base, 10-run BPC)
- Wrecked - lowest chance of BPC invention (14% base, 3-run BPC)

  1. # Skills
 is the basic skill required for every type of Ancient Relic.

Then each ancient relic needs its own two skills. The Subsystem Technology skills themselves each require a specific science skill at IV.
- Armor Nanobot -   &  (which has a prerequisite of Nanite Engineering IV)
- Hull Section -  &
- Power Cores -   & Core Subsystem Technology (which has a prerequisite of High Energy Physics IV)
- Small Hull Section -  &
- Thruster Sections -   &  (which has a prerequisite of Graviton Physics IV)
- Weapon Subroutines -  &  (which has a prerequisite of High Energy Physics IV)

  1. # Materials
- Ancient Relics are gathered from Sleeper Relic sites in w-space using an Relic Analyzer ( skill). They can also be found in the Derelict Talocan Battleship found in certain Sleeper Data sites (despite being found in a Data Site, this object also requires a Relic Analyzer). Be warned that these sites are also combat sites.
- Tech 3 Subsystem Datacores are obtained from Sleeper Data sites in w-space using a Data Analyzer ( skill) and are required for invention of the various subsystems. Be warned that these sites are also combat sites.
- Standard datacores are obtained from **Factional Warfare** LP stores, R & D agents, randomly from Data sites, or just the market and are required for both invention of the subsystems and of the T3 hulls.

  1. # Process
T3 invention is mostly identical to normal T2 **invention**. Datacores and decryptors (if used) are consumed whether the Invention is successful or not. As usual the chances of success and the number of runs of the invented BPC can be changed by using a decryptor. 

The T3 invention process is fast with a base time of only one hour. With good skills and citadel bonuses, the time can easily be reduced to 25 or 30 minutes. One major difference with T2 Invention, however, is that only one job run per science job slot can be submitted at a time. Given the low base chance of success of the process, especially with Malfunctioning or Wrecked ancient relics, this prevent a player from submitting 20 runs overnight and hoping that over the number of runs one or two will have succeeded. 

Most players will therefore want to have the required skills at least at III before attempting the invention process, and having them at IV will help to increase the chances of success. Many players doing T3 Invention will also use decryptors such as Attainment or Parity to increase the chances of success further.

1. # Subsystems and Hull Construction

This is the final part of the process where the BPC that were invented previously are used to manufacture the Tech 3 hulls and subsystems using the Hybrid Tech Components. The Production interface will look familiar:

  1. # Skills
Construction of Tech 3 subsystems and hulls are skill intensive. The skills required are as follow.

For Tactical Destroyers:
- to IV
- to V
- to V
- *<Racial>* Starship Engineering (5x) to V

For Strategic Cruisers
- to IV
- to V
- to V
- *<Racial>* Starship Engineering (5x) to V

For Subsystems
- Either Core, Defensive, Offensive or Propulsion Subsystem Technology at I, as appropriate
- to IV
- to IV
- to IV
- *<Racial>* Starship Engineering (5x) to IV
- to V

  1. # Materials
Tactical Destroyers, Strategic Cruisers and Subsystems are created using invented BPC and Hybrid Tech Components. In addition Tactical Destroyers and Strategic Cruiser require R.A.M.- Starship Tech, for which the BPO is sold by NPCs in k-space.

  1. # Process
Tech 3 subsystems and hulls can me manufactured in any Citadel or Engineering Complex with a Standup Manufacturing Plant I service module online. Rigs exist that can speed up the process or increase material efficiency. These are
- For Tactical Destroyer, Advanced Small Ship Manufacturing
- For Subsystems, Advanced Component Manufacturing (same rig as for manufacturing Hybrid Tech Components)
- For Strategic Cruisers, Advanced Medium Ship Manufacturing

A Tech I and Tech II version of these rigs exist. The usual skill, implants and Facility bonuses also apply.

The actual production process works like any T1 industry job:
- Choose Blueprint
- Set number of runs
- Choose input and output locations
- Press Start
- Wait until the run time has passed and press deliver
- Rinse and Repeat

1. # Final thoughts

As you are now in no doubt, T3 construction is one of the most complex manufacturing process in EVE. Most of the T3 production activity in EVE used to be carried out by wormhole-based corporations at their own structures in w-space, but a fair amount is now done by sov null based corporations. The skill requirements to manufacture Tech 3 ships are also high. Tech 3 ships are therefore expensive, with prices for a Strategic Cruiser hull and all four subsystems around the 250 - 300 M ISK mark (as of March 2022). With a good set-up, the production of Tech 3 ships and subsystems can be profitable, but this likely won't be the first thing the new Industrialist will try.
