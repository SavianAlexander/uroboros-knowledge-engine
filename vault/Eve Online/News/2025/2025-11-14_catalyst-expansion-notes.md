# Catalyst: Expansion Notes

- **Date**: 2025-11-14T15:55:00.000Z
- **Category**: patch-notes
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/catalyst-expansion-notes
- **Tags**: #patch-notes

## Overview
The expansion notes for the upcoming Catalyst expansion are now available.

---

Greetings expansion enthusiasts!

The Catalyst expansion is arriving next week at **11:00 UTC 18 November! **We are delivering the patch notes early so you can absorb everything that's coming next Tuesday. We invite you to join the player discussion about the content of this release on the [EVE Online Discord](https://www.eveonline.com/discord) and the [EVE Online Forums](https://forums.eveonline.com/t/eve-online-catalyst-expansion-notes/500795).


### Expansion Notes 23.02 - EVE Online: Catalyst



## **Map Improvements**



### **New 2D Map**


A brand-new 2D map is now available! You can access it through the 2D toggle button in the bottom-right corner of the map window.

The 2D map comes with two distinct visual modes depending on your zoom level:


- **Heatmap view** when zoomed out, for an overview of the universe data.
- **Tube/Subway-style map** when zoomed in, for a clearer look at systems and connections.


You can also decide how much data to display: use the **eye-shaped toggle** above the 2D button to switch between always-visible data or focusing only around your cursor area.


### **Improved Data Visualisation**


We’ve improved how data is displayed on both the 2D and 3D maps.
The new visualisation now aligns more closely with **player expectations**, drawing inspiration from the classic map’s behaviour. Filters now use **logarithmic scaling,** which makes it easier to distinguish increments in lower-end values, even when big outliers appear on the map.

A **legend** has been added to help interpret the data shown on the map.
By interacting with the **tuning icon** on the legend, you can open the new **filter editing panel**, where you can:


- Adjust the **data range** displayed.
- Switch between **logarithmic** and **linear** scaling.
- Customise the **colours** used for visualisation.


Your changes will be saved per filter, allowing you to tailor how data appears and focus on what’s most relevant to your needs.


### **Jump Range Visualisation**


Pilots flying ships equipped with jump drives can now toggle the **jump range** display on or off on both the 3D and 2D map via the **jump icon** in the bottom-right corner.

In the 2D view, reachable systems are highlighted, and in the tube/subway map mode, reachable nodes change their shape from circles to diamonds.
Hovering over a system provides information about **jump range**, **fuel consumption** and **fatigue** incurred after the jump.


### **New Filters**


We’ve expanded the range of filters available on both 2D and 3D maps!
Under the new **Mining** category, you can now choose from:


- **Ore Anomalies** - displayed as pins, showing nearby anomalies within a 5-jump range.
- **Ore Distribution** - showing where ore belts are located across New Eden.
- **Specific Ores** - highlighting systems where particular ores can be found.


This is also where we’re introducing a new **information sidebar** that appears alongside the map. It provides extra context about the selected filter, helping you explore ore data and learn more about the resources you’re seeing.


### **Quality of Life Improvements**


The following quality of life improvements have been added:


- Pilots can now search for **landmarks** directly in the map’s search field.
- **Directional arrows** have been added to the 2D map to make **regional connections** clearer and easier to identify.



## **Mining UI/UX Improvements**



### Integrated Mining Surveyor with Overlay Toggle


All ORE mining ships and all basic empire corvettes now come equipped with a built-in Mining Surveyor, providing immediate access to in-space resource data without requiring a separate module.

The Mining Surveyor introduces a dynamic overlay, displaying colour-coded visual indicators of asteroid value directly in space. The overlay can be **toggled ON or OFF** via the scanner button on the HUD.


- **Turning Overlay ON:** By clicking the Scan button, your ship performs a mining scan and displays colour-coded visual overlays on nearby asteroids. These overlays highlight relative value tiers and estimated ISK to give players an immediate, at-a-glance view of the most profitable targets in range. - Clicking the scan button again will re-scan your surroundings.
- **Turn Overlay OFF:** Player can also right-click the scan button to disable the overlay. All the current scan data will be retained within the survey scan result window until player re-scan.



### **Mining Survey Chipset Module**


The Mining Survey Chipset is a passive mid-slot module that enhances the mining surveyor with detailed information on the number of units of ore available in nearby asteroids. It also provides bonuses to mining critical success chance and mining critical success bonus yield, as well as a reduction in mining residue chance.


- Only one mining survey chipset module can be fit at a time.
- The mining survey chipset is available in Basic, Tech 1, Compact, and Tech 2 versions.
- Existing survey scanner modules have been converted into mining survey chipset modules.


Mining Surveyors can be upgraded with a **Mining Survey Chipset** to reveal additional information, such as a total value and remaining quantity.

ORE Industrial Command ships can provide upgraded Mining Surveyor functionality fleet-wide through any **Mining Foreman Burst**, granting members access to the same enhanced survey data provided by the Mining Survey Chipset module.


### **Cargo Hold Capacity Indicator**


While the mining surveyor overlay is active, a new icon will display the current capacity of your mining hold in the space scene behind your ship to make this information accessible at a glance.


### **Faster Mining Cycles**


Mining lasers and strip miners now will have 4x faster cycles, and gas cloud harvesters will have 2x faster cycles, making mining operations more responsive. The yield per cycle, capacitor usage, and mining crystal volatility damage has been adjusted proportionally to maintain the same overall mining yield over time.


### **Mining Crits**


Mining lasers, strip miners, and ice harvesters can now experience critical successes, granting bonus yield without reducing the remaining ore in the asteroids. The chance of a critical success starts at 1% and the bonus yield from a critical success starts at 200% of the standard yield of that cycle, with both values able to be increased through skills, modules, and mining foreman bursts. Critical success notification will appear on-screen with added audio and visual cues to inform players when a crit occurs.


### **New Mining Critical Success Skills**


Two new skills have been added to benefit the mining critical success system:


- Mining Precision is a new rank 2 skill that provides a 10% bonus to mining laser and ice harvester critical success chance per skill level.
- Mining Exploitation is a new rank 6 skill that provides a 5% bonus to mining laser and ice harvester critical success bonus yield per skill level.



### **Changes to Mining Cycle Rounding**


The rounding system used for mining yields has been adjusted so that the amount of ore you receive over time while mining will more closely match the estimated values of your modules. Previously, any remainder of less than one whole unit of ore that was left over after the ore unit volume was divided into the mining cycle yield volume would be rounded down and lost. Now we have implemented a system of stochastic rounding so that each cycle will have a chance of receiving one additional unit of ore, so that over time your overall yield will tend towards the yield that would be expected from your module attributes and bonuses.


### **One-key Compression Shortcut**


A bindable hotkey can be assigned to compress all ore, ice, and gas in your ship at once when you have access to compression in space through a mining foreman ship in fleet.


### **Mining Laser Efficiency Mining Foreman Burst Charge**


A new Mining Laser Efficiency charge for the mining foreman burst module has been added.

This new charge provides a base bonus of +50% mining critical success chance and -15% mining residue chance to fleetmates within range. These bonuses scale with pilot skills, ship bonuses, and mindlinks just like other mining foreman bursts.

All of the mining foreman burst charges provide enhanced mining surveyor functionality to all affected fleet members that are piloting ships with an integrated mining surveyor, allowing them to track the remaining number of units of ore in nearby asteroids.


### **New Introductory Message When Entering Asteroid Fields**


When warping into asteroid belts and mining anomalies, a new introductory message will appear in the bottom third of the screen that lets players know the name of the location they just arrived at, as well as an estimate of how depleted or fresh the asteroid field is. This should be especially helpful to players in high-traffic space to indicate at a glance whether a field is mostly picked clean by other players or not.


## **Phased Asteroid Field**



- Phased Fields are high-value mining sites featuring unique mechanics. They spawn randomly in low and null-security space, and must initially be discovered using probe scanning. They contain a valuable new ore - Prismaticite, which can be mined from Phased Asteroids within the site and which requires the use of industrial command ships to mine efficiently.
- In addition to the incredibly valuable Prismaticite, there are also several high-value asteroids of superior grades present which can be mined at any time as normal.
- These sites contain a hyperspace fracture which will slowly move across space, breaching any Phased Asteroids along its path. - Once breached, Phased Asteroids are phased-out and can be mined for prismaticite at 10% efficiency immediately. - After deploying a Mobile Phase Anchor and connecting it to industrial command ships, the asteroid will phase-in and can then be mined at 100% efficiency.
    - This persists until it phases-out over time or the fracture moves away, collasping the asteroid.
- Mobile Phase Anchors require 100 energy to phase-in the Phased Asteroids. Rorquals provide 100, Orcas 50, and Porpoises 35. - Mobile Phase Anchor Blueprints are available for 140 million ISK in the following locations: Ytiri, Propel Dynamics, Eifyr & Co., Freedom Extension, Zoar & Sons, Ducia Foundry, Impetus, Chemal Tech, Mordu's Legion, ORE, and Intaki Bank Stations.
- Once the fracture has moved halfway across the site, a beacon is spawned revealing the site. Once revealed, the site’s location is visible to everyone in the solar system, and it also becomes visible on the Star Map.
- Prismaticite is resource-rich, but it is also the first in a new type of ore called Erratic. When Prismaticite is reprocessed, each reprocessing batch will randomly become 1 of the 8 possible mineral types and provide a variable quantity of that mineral.
- Capsuleers can control the mineral output of Prismaticite by running Unrefined Mineral Reactions. These reactions require Compressed Prismaticite and Atmospheric Gases. - Reactions for the Unrefined Minerals can be purchased from most Upwell Consortium member corporations for 50 million ISK.
  - Unrefined Mineral Reactions require Standup Composite Reactor.
  - Unrefined Minerals can be reprocessed into their respective Minerals with variable output quantity.



## **Mining Content**



- Revamped the ‘Asteroid Belt Remnants' site found in all starter systems and career agent systems. It has instead been replaced by an empire managed asteroid belt instead with enhanced visuals and NPCs. - Number of sites reduced from 3 to 1 to make it more likely for new players to meet each other in the sites.
  - New site uses an acceleration gate which only lets the standard Venture and empire corvettes inside (Impairor, Ibis, Velator and Reaper).
  - Veldspar size in the site increased by 10-12x.
- Kernite and Omber anomalies will now spawn rarely in all high security space between 0.5 and 0.8 security rating as they once did before the resource distribution update.
- Kernite and Omber anomalies have had a full visual pass.
- Kernite and Omber anomalies will have a slightly higher chance to spawn in high security space within 3 jumps of Empire Militia FW War HQ systems.
- Kernite and Omber anomalies have a very small chance to get an escalation to a brand new highsec exclusive mining escalation, the shrouded asteroid belt.
- Hidden Omber Deposits which need to be probed down with scanner probes will also appear rarely between 0.5 and 0.8 security rating systems. This site contains some +15% Platinoid Omber and a higher chance to get the mining escalation.
- Highsec mining anomalies such as the Kernite and Omber sites, Rare Border sites, Ice Belts and the new managed asteroid belts will now spawn a beacon into space on the overview when a player first warps to them (like FW sites) to give better visibility to newer players and showcase mining activity in highsec. These beacons have been added to the default mining overview. - We have not added these beacons to anomalies in lowsec/nullsec/w-space for now since miners in these areas of space might want to hide their activity.
  - The hidden omber site (found with scanner probes) and the highsec mining escalation do not spawn a beacon when warped to as players may want to keep the location to themselves.
- Added a system wide buff effect into Empire Miltia FW War HQ systems that grants a 10% mining speed bonus.
- NPC mining ships will now spawn much more frequently in their factions respective FW War HQ systems.
- Veldspar Deposits will now spawn in Empire Militia FW War HQ systems. - The War HQ systems are where the shipcasters are located for each empire militia and are listed below. - Amarr - Mehatoor
    - Caldari - Onnamon
    - Gallente - Intaki
    - Minmatar - Amo



> We are adding back the Omber and Kernite anomalies that were taken away from High Security space when the Resource Distribution update took place 5 years ago. Specifically, we are only adding back the Kernite and Omber anomalies (and not the ones containing Jaspet or Hemorphite) to keep Nocxium a more low-sec focused mineral. We want to bring back a source of Omber and Kernite to highsec so that players are able to mine it for level 3 and level 4 storyline trade missions that require it, and also add more valuable sites that are slightly less predictable than the rare border sites which spawn in the same locations. Additionally, we are adding a highsec escalation as a rare jackpot for highsec miners.To help encourage mining in FW empire war HQ systems (and help encourage them to become market/trade hubs and good places for producers to buy minerals from and stock ships, which they can then sell to FW players) we are weighting the chance of the Kernite and Omber anomalies to have a higher chance of spawning in and around the War HQ systems. We’re also adding a small mining boost effect in these systems and then adding in a Veldspar Deposit as a more reliable source of highsec minerals in the War HQ systems, as Amo and Mehatoor specifically only had 4 asteroid belts, and Intaki had special asteroid belts that only respawned infrequently which made it hard to get consistant mining going there.



- Improved the visuals of lowsec Asteroid Belts.
- Lowsec mining anomalies can no longer spawn multiple copies of the same site in the same solar system. For example, 2x Small Gneiss Deposits can no longer share the same system. This means they will be more spread out and more widely available and won’t congregate as much in a single system.
- Rare Border Sites that could spawn in 0.5 high security systems that border lowsec, nullsec that borders lowsec and Blue A0 sites which could spawn in systems with blue A0 suns in wormhole space and nullsec can no longer spawn multiple copies of the same site in the same solar system.
- Adjusted the Medium Jaspet Deposit and renamed to Average Jaspet Deposit to match the naming scheme of similar anomalies. It no longer spawns in every lowsec system, and will now instead appear uncommonly throughout lowsec. Increased the size of the asteroids, increased the amount of asteroids by approximately 4x and added +5% and +10% Jaspet variations so that the site should at least feel more rewarding.
- Doubled the chance of the small variation of mining deposits from appearing in lowsec.
- Removed rogue drone NPCs from lowsec small anomalies, so that they are a bit easier to ninja mine with ventures/prospects etc. The standard asteroid belt NPCs can still show up at the anomalies.
- Added new variations of the small mining deposits as ‘hidden’ versions that need to be discovered with scanner probes. These variations have higher quality ore and a much higher chance to get the new lowsec mining escalation. We’re adding just the small ones for now to see how players respond to them in low security space, we’re hoping the extra safety of needing to discover the site first and higher quality ore make them attractive to miners and will lead to more mining ships in space overall in lowsec.
- All lowsec anomalies now have a small chance to escalate to a new exclusive lowsec escalation, the Veiled Asteroid Field.
- The Veiled Asteroid Field has a similar amount of minerals found in the Large Crokite, Dark Ochre and Gneiss anomalies, but they are condensed into far fewer asteroids at higher tiers. It has the added advantage of other players needing to combat probe you to find the site.



### **Mining Missions**



- All mining missions have had an enhanced visual pass.
- All Level 1 and Level 2 mining missions have had their ISK and LP Payouts increased by 50%.
- We’ve made sure to do a QoL pass on many of the sites too, making sure the mission asteroids are usually within 20km of the warp in point for the mission so the mission ore can always be found with the on board scanner and players don’t have to move far away to be able to mine the ore, now that everything has been replaced with non-interactable objects to the mission ore should always be at the top of the overview if you sort by range closest to you.



### **Mining Mutaplasmids**



- New Mutaplasmids have been added that can mutate: - Mining Lasers
  - Strip Miners
  - Ice Mining Lasers
  - Ice Harvesters
  - Gas Cloud Scoops
  - Gas Cloud Harvesters
  - Mining Drones
  - Ice Harvesting Drones



> These new mining module Mutaplasmids can be found in Abyssal Deadspace, while the mining drone mutaplasmids are potential rewards from CONCORD Rogue Analysis Beacon sites.



## **New Ships**


Catalyst introduces 4 new mining ships along with the Sisters of EVE Expedition Command Ship the Odysseus!


### **ORE Mining Destroyer - Pioneer**



- Pioneer Skill Bonuses: - **Mining Destroyer: (per skill level)** - 10% bonus to **Mining **yield
    - 20% bonus to **Mining **range
    - 5% reduction in **Gas Cloud Scoop** duration
  - **Role Bonus:** - 50% bonus to **Mining **yield
    - 25% reduction in **Gas Cloud Scoop **duration
- Blueprint Originals for the Pioneer can be purchased from Outer Ring Excavations (ORE) stations in Outer Ring.
- Alpha Clones are able to train the new Mining Destroyer skill to level 2.



### **ORE Command Destroyer - Outrider**



- Outrider Skill Bonuses: - **Mining Destroyer:** - 15% bonus to **Mining **yield
    - 10% bonus to **Drone **hitpoints and damage
    - 6% bonus to all shield resistances
  - **Command Destroyer:** - 5% reduction in Micro Jump Field Generator spool up time
    - 2% bonus to Shield Command and Mining Foreman Burst effect strength and duration
  - **Role Bonus:** - 95% reduction in powergrid requirements for **Command Bursts**
    - 50% reduction in Microwarpdrive signature radius penalty
    - 50% reduction in reactivation delay for Defender Launcher
    - Can fit Micro Jump Field Generators
    - Can fit one Command Burst module
    - 75% bonus to tractor beam range
    - 30% bonus to Tractor Beam velocity
- Blueprint Copies of the Outrider can be obtained by performing Invention jobs on blueprint copies of the Pioneer.



### **ORE Navy Mining Frigate - Venture Consortium Issue**



- Venture Consortium Issue Skill Bonuses: - **Mining Frigate: (per skill level)** - 5% bonus to **Mining **yield
    - 5% reduction in **Gas Cloud Scoop** duration
    - 10% bonus to **Shield Booster** amount
  - **Role Bonus:** - 100% bonus to Mining and **Gas Cloud Scoop **yield
    - 2+ bonus to ship warp core strength
    - 50% reduction in **Industrial Cynosural Field Generator** liquid ozone consumption
    - 50% bonus to **Mining **critical hit chance
    - 10+ bonus to **Salvage Drone** salvage chance
- Blueprint Copies for the Venture Consortium Issue can be obtained from Upwell Consortium member corporations LP stores for the price of 10 million ISK and 10,000 Loyalty Points. - This includes Chemal Tech, Ducia Foundry, Eifyr and Co, Freedom Extension, Impetus, Intaki Bank, Mordus Legion, Propel Dynamics, Ytiri and Zoar and Sons corporations.
  - ORE offers a 60% discount in their LP store, at a price of 4 million ISK and 4,000 Loyalty Points.



### **ORE Navy Mining Destroyer - Pioneer Consortium Issue**



- Pioneer Consortium Issue Skill Bonuses: - **Mining Destroyer: (per skill level)** - 10% bonus to **Mining **yield
    - 20% bonus to **Mining **range
    - 10% bonus to **Shield Booster** amount
    - 5% reduction in Gas Cloud Scoop duration
  - **Role Bonus:** - 50% bonus to **Mining **yield
    - 50% bonus to **Mining **critical hit chance
    - 25% reduction in **Gas Cloud Scoop **duration
    - 10+ bonus to **Salvage Drone** salvage chance
- Blueprint Copies for the Pioneer Consortium Issue can be obtained from Upwell Consortium member corporations LP stores for the price of 30 million ISK and 30,000 Loyalty Points. - This includes Chemal Tech, Ducia Foundry, Eifyr and Co, Freedom Extension, Impetus, Intaki Bank, Mordus Legion, Propel Dynamics, Ytiri and Zoar and Sons corporations.
  - ORE offers a 60% discount in their LP store, at a price of 12 million ISK and 12,000 Loyalty Points.



### **SOE Expedition Command Ship - Odysseus**



- **Odysseus **Skill Bonuses: - **Amarr Battlecruiser: (per skill level)** - 4% bonus to **Armor Resistances**
  - **Gallente Battlecruiser: (per skill level)** - 10% bonus to **Light, Medium and Heavy Drone **damage
  - **Expedition Command Ships: (per skill level)** - 50% bonus to Data Analyzer and Relic Analyzer optimal range
    - 5% reduction in gas cloud scoop duration
    - 3% bonus to the strength and duration of **exploration command bursts**
    - 1% bonus to the strength and duration of **armor command bursts**
  - **Role Bonus:** - 100% bonus to the duration of **Expedition Command Bursts**
    - 50% bonus to the range of **command burst** modules
    - 50% bonus to **Medium Energy Turret** Optimal Range
    - 50% Reduction in CPU cost of **Gas Cloud Scoops**
    - 37.5% bonus to **Scan Probe Strength**
    - 10+ bonus to **Relic **and **Data analyzers**
    - Can fit **Covert Ops Cloaking Device**
    - Can fit two **command burst **modules
    - **Cloaking **reactivation delay reduced to 15 seconds
    - Can fit **Zero-Point Mass Entangler**
    - This ship can recieve bonus effects depending on the environment.
- Blueprint Copies for the Odysseus can be obtained from the Servant Sisters of EVE faction member corporations for the price of 250,000 LP and 250,000,000 ISK. - This includes The Sanctuary, Food Relief and the Sisters of EVE corporations.



## **Modules**



- Added new Expedition Command Burst modules, these modules can be activated to give you and nearby fleet members bonuses to hacking, scanning and salvaging.
- These modules can be loaded with 1 of 3 charges. - **Expedition Strength Charge** - improves scanning strength and virus coherence of all analyzer modules.
  - **Expedition Pinpointing Charge** - improves scanning scan deviation and cycle time of salvager modules.
  - **Expedition Reach Charge** - Improves the range of Analyzer modules, Salvager modules and directional scanner range.
- Blueprints of the Expedition Command Burst modules and charges can be found in Servant Sisters of EVE member corporation stations for sale.
- A faction variation of the Expedition Command burst can be found in the Servant Sisters of EVE member corporation LP stores.
- An expedition command mindlink can be found in CONCORD LP stores and purchased for 20 million ISK and 20,000 LP.
- The sisters expedition command mindlink, which combines the effects of the Armor and Expedition mindlink, can be purchased from Servant Sisters of EVE member corporations for 100,000,000 ISK and 100,000 LP.
- Added a new Integrated Sensor Array - Carrier only module. More about that below.



## **Carriers**



- Decreased build costs by approximately 30%.
- Decreased build times by 10%.



> The cost of Carrier construction has been brought down significantly. The reduction represents around 1 billion ISK per hull at time of writing. At this new price point, these ships will be somewhere between a Marauder and a Dreadnought. This allows a player to make a more meaningful choice when selecting their ship.



- Carriers can now have an additional Support Fighter squad active: - Increased the Support Fighter Squad limit to 2 (from 1).
  - Increased the total number of Fighter Squad Tubes to 4 (from 3).
- Added new Support Fighter effectiveness bonuses: - Archon: +2% bonus (per level) to Cenobite Support Fighter neutralization strength.
  - Chimera: +2% bonus (per level) to Scarab Support Fighter ECM strength.
  - Thanatos: +2% bonus (per level) to Siren Support Fighter afterburner speed bonus.
  - Nidhoggur: +2% bonus (per level) to Dromi Support Fighter stasis webification strength.
- Increased Fighter Bay Capacities: - Archon: 60,000 → 65,000 m3.
  - Chimera: 55,000 → 60,000 m3.
  - Thanatos: 70,000 → 75,000 m3.
  - Nidhoggur: 65,000  → 70,000 m3.



> These changes aim to strengthen the Carrier’s long range EWAR niche. A Carrier pilot can now field an additional Support Fighter, giving them additional utility with no loss of DPS. They will also have the option to field 2 Support and 2 Light Fighters at the same time if the need arises.Support Fighters themselves are now more powerful when used by a Carrier. Each faction will be able to make the most out of their respective Support Fighters, with an up-to 10% bonus to effectiveness.



- Increased Ship Maintenance Bays to 2,000,000 m3 (from 1,000,000 m3).



> Part of the expectation of a Carrier is the ability to move a large number of ships. As such, the SMB of all Carriers has been doubled. This brings these ships to the same ballpark as a Bowhead.



- Decreased max target ranges: - Archon: 3,950 → 315 km.
  - Chimera: 4,620 → 350 km.
  - Thanatos: 3,670 → 300 km.
  - Nidhoggur: 3,760 → 305 km.
- Added a max target range cap of 750 km.
- Can fit the new Integrated Sensor Array: - Functionally identical to Networked Sensor Arrays, other than the following: - Multiplies max target range by 12.
    - Removes the max target range cap.
    - Has a 2-minute duration.
    - Adds a -30% bonus to repair module duration and capacitor use.
    - Does not disable MJD or MJFG.
    - No increase in EWAR capacitor costs.
    - Uses the visual effect of a Triage module.
    - Cannot be fit to Supercarriers.
    - Note: You can still receive remote repairs when this is active, just like the NSA.
  - Build costs and blueprint availability are the same as those of Networked Sensor Arrays.
  - Networked Sensor Array can be traded in for Integrated Sensor Arrays at all LP stores.



> The above changes aim to tackle “skynetting” Carriers. Carriers will no longer be able to engage at their previous extreme ranges without an active Integrated Sensor Array. While this module is active, the Carrier will be unable to warp, dock, or tether. This provides counterplay for those attacking into Carriers within tether range of a structure.The Integrated Sensor Array is a much more powerful variant of the Networked Sensor Array. The MJD and MJFG restrictions are not present on this variant, allowing the ships more mobility. Active tanking is also buffed when using the Integrated Sensor Array. Lastly, the EWAR capacitor cost increases of the Networked Sensor Array are not present to allow more flexibility in fitting.Note that Carriers will still be able to fit a Networked Sensor Array until early next year. After this time, the Networked Sensor Array will be made exclusive to Supercarriers.



### **Support Fighters:**



- Increased Scarab Support Fighter ECM strengths: - Scarab I to 2.4 (from 1.6).
  - Navy Scarab to 2.7 (from 1.95).
  - Scarab II to 3.0 (from 2.3).
- Increase Cenobite Support Fighter Energy Neutralizer amounts: - Cenobite I to 70 GJ (from 60 GJ).
  - Navy Cenobite to 80 GJ (from 70 GJ).
  - Cenobite II to 90 GJ (from 80 GJ).



> The Scarab and Cenobite are the least popular Support Fighters by a noticable margin. Increasing their effectiveness helps make the bonuses found on the Archon and Chimera feel impactful. Having more viable options for a Carrier also gives them better flexibility.



### **Supercarriers:**



- All Supercarriers can now Conduit jump with the same mechanics as a Carrier: - Can jump with a maximum of 30 other capsuleers.
  - All sub-capital combat ships are eligible to be jumped.



> The addition of a Conduit jump to Supercarriers gives them extra utility and some nice QoL when flying in a smaller fleet.



### **Force Auxiliaries**



- Increased the Fuel Bay of all Force Auxiliary ships to 6,000 m3.



> Force Auxilary ships are often more fuel hungry than other ships with the same sized bay. Increasing the Fuel Bays for these ships should make the experience of flying them more enjoyable.



## **Balancing**



- **Molok** - Blueprint Copy added to the Blood Raider LP store at 165 billion ISK and 165 million LP.
- **Chemosh** - Blueprint Copy added to the Blood Raider LP store at 15 billion ISK and 15 million LP.
- **Dagon** - Blueprint Copy added to the Blood Raider LP store at 15 billion ISK and 15 million LP.
- **Loggerhead** - Blueprint Copy ISK and LP cost reduced from 25 billion ISK and 25 million LP to 15 billion ISK and 15 million LP.



> We’re adding the Blood Raider capital ships to the Blood Raider LP store, as we are unhappy with the state of NPC Sotiyos and to get parity with the other pirate factions. We are adding them at a slightly higher cost (+10% of the others) to carefully monitor them, and we’ll slowly adjust them down when we’re satisfied, although we know that this is likely too high of a cost, and the other pirate dreadnoughts are likely still too expensive as well.Additionally. we are reducing the cost of the Loggerhead at the same time to match the Dagon at 15 billion ISK and 15 million LP. We want to monitor pirate FAX being more available before reducing them to the dreadnought values, since they may be overpowered in some niche areas of space such as wormholes if they are easier to replace and more available.



- **Cenotaph** - Breacher Pod M Damage Duration reduced from 50s to 40s. (From 75s to 60s with max skills).
  - Breacher Pod M Maximum Damage reduced from 800 to 600 (from 1000 DPS to 750 DPS with max skills).
  - This is a large reduction to the total amount of damage done per breacher pod, especially against larger ships, with max skills this is a reduction from 75,000 to 45,000 maximum damage per pod.
- **Tholos** - Breacher Pod S Damage Duration reduced from 50s to 40s. (From 75s to 60s with max skills).
  - Breacher Pod S Maximum Damage increased from 160 to 200 (from 200 to 250 DPS with max skills).
  - This maintains the total amount of damage done per breacher pod against large ships, at 15,000 damage per pod.



> The Cenotaph is still too strong despite our attempts to add more counterplay to it in the Legion Major Update. We are reducing the maximum damage duration of pods with max skills from 75 seconds to 60 seconds, and lowering the maximum potential flat damage output that the breacher pod outputs. This comes close to halfing the total damage per pod (a 40% reduction overall). Which we think will still leave it in a very strong place against high resistance targets, but reduce the overall pressure it provides when spreading multiple pods over multiple ships at once.We are also adjusting the Tholos a little for consistency, so that all breacher pods now last 60 seconds with max skills. We are lowering the total damage duration of the pod but then compensating it by increasing the flat damage, keeping the damage per pod the same as now. This will see it increase from 200 to 250 DPS against larger targets it is focusing a few pods on, but it will see a small reduction of damage if spreading multiple pods over smaller targets.



- **Stratios** - Added 50% Medium Energy Turret damage role bonus.
  - Reduced Number of Turrets from 4 to 3.



> Even though the Stratios was bonused for Medium Energy Turrets, they were frequently ignored for other weapons or energy neutralizers and felt weak despite the bonus. We’re giving it a large 50% damage role bonus, but then taking away a turret. This should make the lasers feel better to use with most stratios fits since you can fit 3 bonused lasers alongside a cloak and a probe launcher at the same time, and it also reduces the fitting and capacitor costs needed for full gun fits, while providing a small boost in damage as now the 3 turrets will outdamage the old Stratios with 4 turrets fitted.



- **Mamba** - Guristas NET Resonators required to build the Mamba reduced from 40 to 30.
- **Mekubal** - Angel NET Resonators required to build the Mekubal reduced from 40 to 30.
- **Venture** - The Venture Blueprint no longer requires Isogen to be able to manufacture a Venture.
- **Porpoise** - Medium Industrial Core I - Shield Booster cycle time bonus improved from 10% to 20%.
    - Shield Booster amount bonus improved from 10% to 20%.
  - Medium Industrial Core II - Shield Booster cycle time bonus improved from 10% to 20%.
    - Shield Booster amount bonus improved from 15% to 25%.
- **Orca** - Large Industrial Core I - Shield Booster cycle time bonus improved from 30% to 40%.
    - Shield Booster amount bonus improved from 20% to 40%.
  - Large Industrial Core II - Shield Booster cycle time bonus improved from 30% to 40%.
    - Shield Booster amount bonus improved from 30% to 50%.



> Giving a small boost to the active tanking capabilities of the Porpoise and the Orca while they are using the industrial core modules.



## **PLEX Transaction Logs**


New PLEX Transaction Logs are now available through the Wallet. There are 2 tabs available Overview and Transactions.


- The Overview tab shows a Pie Chart of either Income or Expenses.
- The Transactions tab will show the latest 2000 entries.
- Description of transaction includes which Character interacted with PLEX balance.
- Entries can be sorted by date, ascending or descending.
- Transactions can be copied to clipboard in CSV format for easy pasting in your workbook software of choice.



## **Epic Arc**



- A New Epic Arc — Fractured Legacy — has been added! - Consisting of three mining-focused missions, this new Epic Arc is meant for new and returning players. - The Arc showcases Catalyst features, including a gorgeous Phased Field!
  - The latest Epic Arc in nearly 16 years, it is short and experimental compared to its predecessors. - It is estimated to be completable in the length of a normal session.
  - Earn novel rewards, such as the new ORE Mining Destroyer, the Pioneer! - Other rewards include other new expansion goodies, such as modules and BPCs.
  - To get started on this ORE Epic Arc, go to the AIR Laboratories station in Kisogo VII and speak to Elias Peltonnen.



### **Air Opportunities - Freelance Jobs Visibility Update**


We’ve updated Freelance Job tab in Air Opportunities to only display jobs that the current character is eligible to participate in.


### **Factional Warfare:**



- New NPCs have been added to most FW Complex sites: - NPCs of both the occupying and attacking factions will be present.
  - NPCs will fight based on factional allegiances and can contest sites.
  - Some NPCs may be fitted with warp disruption.
  - NPCs can still drop tags, but at a lower rate given their increased presence.
  - Scout, Small, Medium, and Large Complex sites have all been updated.



> These changes borrow strongly from the mechanics found in Pirate Insurgency sites. Capsuleers will always be able to take part in a small scale skirmish when entering a complex.Having NPCs of both factions present will also mean a capsuleer will want to be fit for combat even when defending. Keeping track of pointing NPCs will also be necessary if a player wants to be ready to a quick getaway.



### **Pirate Strongholds:**



- The rewards for destroying a Pirate Strongholds (sometimes referred to as Pirate FOBs) have been rebalanced: - A 10-pilot fleet will now be optimal for the maximum payout.
  - Up to 1 billion ISK can be earned per Stronghold.
- Roaming NPCs spawned by the Pirate Stronghold will no longer attack player structures.



> The rewards for Pirate Strongholds did not fit the expected risk/reward within low-sec. There has also been some demand for 10-pilot content within these systems. The FOBs have been rebalanced to provide rewarding content for medium scale low-sec pilots. Note that the drops from the FOB have been unchanged.The roaming Pirate NPCs have been causing frustration for those who have structures within those systems. This was especially true with Metanox Moon Drills, where their frequent brief attacks meant constant upkeep. As such, these NPCs will no longer shoot at structures. However, they may still visit them looking for other targets!



---


We're excited to see what you do with the updates coming in the Catalyst expansion, and we'd love for you to get involved with the discussion on the [EVE Online Discord](https://www.eveonline.com/discord) and the [EVE Online Forums](https://forums.eveonline.com/t/eve-online-catalyst-expansion-notes/500795).

o7
