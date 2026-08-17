---
title: "Moon mining"
url: "https://wiki.eveuniversity.org/Moon_mining"
pageid: 16269
source: "EVE University Wiki"
categories: ["Mining", "Needing updates"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Moon mining

1. # Background and History
The Lifeblood expansion was released on October 24, 2017, and brought with it substantial changes to the process of moon mining.  Previously, moon mining was completed using **player-owned starbases**, but the Lifeblood expansion introduced a new class of **Upwell structures** called **refineries**, which—if anchored in 0.5 space or below near a moon mining beacon—can use a Standup Moon Drill to extract a chunk of the moon for mining.  As of the [Equinox](https://www.eveonline.com/news/view/equinox-expansion-notes) update, a **Metenox Moon Drill** can also be placed at a moon mining beacon, providing automated (if slower) moon mineral extraction.

1. # Moon Scanning
Moons may be scanned with survey probes along with a survey probe launcher.  

Moon scans return details on the average output of a moon, and allow would-be moon miners to understand what the value of the moon might be so that the best available moon can be selected.  An example of a moon scan result is shown below.

Moon scanning is different than probe scanning from exploration, in two critical ways. First, Survey probes are consumed when they are launched, and cannot be recalled to the ship. Second, the ship must be pointed directly at the target moon when the probe is launched. If the ship is not facing the moon when a survey probe is launched, the probe may 'miss' the moon and return no results. The probe is still consumed when this happens.

  1. # Equipment

  1. ## Survey Probes
There are three types of Survey probes. They differ in skill requirement, size, and the "maximum flight time" which is the measure used for how long it will take to return data. The data returned by each type of probe will always be the same, so the primary considerations are how many a ship can carry (if probing a system with lots of moons, or many systems) and how long it takes to get the results.

| Survey Probe Type | Skill Requirement | Volume | Flight Time |
| :--- | :--- | :--- | :--- |
| Quest Survey Probe I | Survey|III}},  | 5 | 1200s (20 minutes) |
| Discovery Survey Probe I | Survey|III}},  | 10 | 300s (5 minutes) |
| 24px]] | Survey|V}},  | 5 | 150s (2.5 minutes) |

There is no T2 Survey probe, although the Gaze Survey Probe is restricted to Omega-only.

  1. ## Survey Probe Launchers
The Survey Probe Launcher fits in a high slot, but does not require a turret or launcher hardpoint. This allows it to be used on a wide variety of hulls. Unlike the probes themselves, there is a T2 variant of the launcher, which grants a 10% reduction to the probe's scan time. Only one survey probe launcher of either variant can be fitted to a ship at a time.

  1. # Performing the Activity
Survey Probes must be launched directly at the target moon, from within 100,000km of it. This means you must physically align your ship to the moon, as the probe is launched in a straight line along your path of travel. Once in range and aligned, cycle the Survey Probe Launcher to launch a probe. It does not auto-repeat, but it will auto-reload if emptied and additional probes are available in the cargohold. 

Upon launching a probe, a new window will be displayed showing the remaining time for the probe to return its results. The ship must stay in-system and undocked until the results are sent back from the probe, and the results will appear in the bottom half of the same window. The window will keep these results until the user logs out of the game, even if they move to another system. Individual results can be cleared by right clicking on the moon name and selecting Delete.

The probe results window does not allow copying to clipboard via typical keyboard commands such as  + , however there is a "Copy to Clipboard" button which will copy the entire list of probe results into a tab-delimited format that can easily be pasted into another program:

The values listed in this export are the Ore name, the Quantity (as a percentage), the TypeID of the ore, and the ID's for the Solar System, Planet and Moon. Much of this data is redundant, but it makes for good error-checking if the results are to be run through a script or stored in a database. It is of note Quantity may not add up to 1.0, the highest of value moons can sometimes be as low as 80%.

The total quantity makes up 30,000 m3 of moon Product mined per hour - so a moon with 0.5 Quantity (or 50%) Bitumens will produce 15,000 m3 of Bitumens per hour to contribute to the final extraction, or to the Metenox output (it's worth bearing in mind Metenox drills have their own efficiency reduction to apply also).
 
Converted into a more legible table format:

| -
! Moon !!  Moon Product !! Quantity (%) !! Ore TypeID !! SolarSystemID !! PlanetID !! MoonID |
| :--- |
| Tarta IX - Moon 1 |
| Bitumens |
| Sylvite |
| Zeolites |
| Tarta IX - Moon 2 |
| Coesite |
| Zeolites |

There is no known limit to how many probes a player may have active at any given time, only a practical limit on how many one can launch while moving between moons to launch more, before the results start to return and clear their respective probes from the list. There is also no reason to launch additional probes at the same moon - the results are always accurate regardless of the probe type used, and will never change even after moon extractions have begun.

1. # Moon Ore Extraction
Once a moon has been identified as a good candidate, a refinery is anchored near the moon mining beacon and then the refinery must be equipped with a moon mining drill service module.  The moon mining drill can then be activated to extract a chunk of the moon over a period of 6 to 56 days, slowly pulling the chunk closer to the refinery.  The length of extraction is directly related to the amount which will be extracted, calculated with 30.000 m³ per hour of preparation.  After the extraction period has passed, the refinery owner has a period of time to detonate the moon ore chunk into a mineable asteroid field with moon-specific ores.  If the chunk is not detonated manually, it will automatically detonate after approximately three hours, modifiable with rigs.

Alternately, a **Metenox Moon Drill** can be anchored in Low-Sec, Null, or Wormhole space to automatically extract the moon minerals. This is a slower extraction rate than a properly run refinery + mining fleet.

1. # Moon Ore Mining
Once a moon chunk has been extracted using a Refinery, it exists as an asteroid field which contains special moon-specific ores.  After extraction, the mining is performed using the same mining equipment and processes used for asteroid **Mining**.  Mining crystals are available for each class of moon ore to improve efficiency of Tech 2 mining lasers, provided the player trains the appropriate moon ore reprocessing skill.

1. # Ore Types

  1. # Moon-specific Ore
In addition to the classic minerals that other ores provide, some materials required for T2 construction can only be found in moon ores. Like the normal asteroid ores, moon ores also have basic, improved, and excellent quality types. However, moon ore quality more strongly affects the reprocessed minerals received. The improved ores yield a 15% bonus, while the excellent ores provide a 100% bonus on minerals received through reprocessing. 

There are 5 classes of moon ore, as shown in the table below. All classes are available in low and null-sec systems, but High sec and Wormhole systems may only have R4 (Ubiquitous) ores.

| Ubiquitous | Common | Uncommon | Rare | Exceptional |
| :--- | :--- | :--- | :--- | :--- |
| R4 | R8 | R16 | R32 | R64 |
| High Sec | ✔ |  |  |  |
| Low Sec | ✔ | ✔ | ✔ | ✔ |
| Null Sec | ✔ | ✔ | ✔ | ✔ |
| Wormhole | ✔ |  |  |  |

Moon-specific ores are often of mixed quality, with the same moon pull containing both regular and improved quality of the same ore. However there is a chance that, at the time of detonating a moon chunk to create the asteroid field, that there will be a bright blue flash - this has come to be known as a "jackpot" and indicates that the moon ores for that particular extraction will ***all*** be of the excellent quality instead.

  1. # Moon Ore Refining
The following tables show the minerals and special materials present in ***1000*** of each moon ore. Values are for the basic ore. Any decimal values from the improved ores (+15%) are rounded up to the next whole number.

| 32px|link=]]  Ubiquitous (R4) Moon Ore Yield (per 1000) |
| :--- |
| Moon Ore | R4 Minerals | Normal Minerals |
| :--- | :--- | :--- |
| 32px|link=]] Pyerite | 32px|link=]] Mexallon |
| :--- | :--- |
| **Bitumens** |  65 Hydrocarbons | 6000 |
| **Coesite** |  65 Silicates | 2000 |
| **Sylvite** |  65 Evaporite Deposits | 4000 |
| **Zeolites** |  65 Atmospheric Gases | 8000 |

| 32px|link=]] Common (R8) Moon Ore Yield (per 1000) |
| :--- |
| Moon Ore | R8 Minerals |
| :--- | :--- |
| Cobaltite | 32px|link=]] 40 Cobalt |
| Euxenite | 32px|link=]] 40 Scandium |
| Scheelite | 32px|link=]] 40 Tungsten |
| Titanite | 32px|link=]] 40 Titanium |

| 32px|link=]] Uncommon (R16) Moon Ore Yield (per 1000) |
| :--- |
| Moon Ore | R16 Minerals | R4 Minerals |
| :--- | :--- | :--- |
| Chromite | 32px|link=]] 40 Chromium | 32px|link=]] 10 Hydrocarbons |
| Otavite | 32px|link=]] 40 Cadmium | 32px|link=]] 10 Atmospheric Gases |
| Sperrylite | 32px|link=]] 40 Platinum | 32px|link=]] 10 Evaporite Deposits |
| Vanadinite | 32px|link=]] 40 Vanadium | 32px|link=]] 10 Silicates |

| 32px|link=]] Rare (R32) Moon Ore Yield (per 1000) |
| :--- |
| Moon Ore | R32 Minerals | R8 Minerals | R4 Minerals |
| :--- | :--- | :--- | :--- |
| Carnotite | 32px|link=]] 50 Technetium | 32px|link=]] 10 Cobalt | 32px|link=]] 15 Atmospheric Gases |
| Cinnabar | 32px|link=]] 50 Mercury | 32px|link=]] 10 Tungsten | 32px|link=]] 15 Evaporite Deposits |
| Pollucite | 32px|link=]] 50 Caesium | 32px|link=]] 10 Scandium | 32px|link=]] 15 Hydrocarbons |
| Zircon | 32px|link=]] 50 Hafnium | 32px|link=]] 10 Titanium | 32px|link=]] 15 Silicates |

| 32px|link=]] Exceptional (R64) Moon Ore Yield (per 1000) |
| :--- |
| Moon Ore | R64 Minerals | R16 Minerals | R8 Minerals | R4 Minerals |
| :--- | :--- | :--- | :--- | :--- |
| Loparite | 32px|link=]] 22 Promethium | 32px|link=]] 10 Platinum | 32px|link=]] 20 Scandium | 32px|link=]] 20 Hydrocarbons |
| Monazite | 32px|link=]] 22 Neodymium | 32px|link=]] 10 Chromium | 32px|link=]] 20 Tungsten | 32px|link=]] 20 Evaporite Deposits |
| Xenotime | 32px|link=]] 22 Dysprosium | 32px|link=]] 10 Vanadium | 32px|link=]] 20 Cobalt | 32px|link=]] 20 Atmospheric Gases |
| Ytterbite | 32px|link=]] 22 Thulium | 32px|link=]] 10 Cadmium | 32px|link=]] 20 Titanium | 32px|link=]] 20 Silicates |

1. # External links
- EVE Help center: [Moon Mining](https://support.eveonline.com/hc/en-us/articles/115005404229-Moon-Mining), [Metenox Moon Drill](https://support.eveonline.com/hc/en-us/articles/14341380413212-Metenox-Moon-Drill)
- Dev blog: [The Goo must flow: Everything about Refineries and Moon mining](https://www.eveonline.com/news/view/the-goo-must-flow-everything-about-refineries-and-moon-mining)
