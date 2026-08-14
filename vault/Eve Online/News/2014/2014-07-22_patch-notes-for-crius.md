# Patch notes for Crius

- **Date**: 2014-07-22T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP Falcon
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-crius
- **Tags**: #patch-notes

## Overview
Patch notes for Crius 1.10 Released on Friday, August 15th, 2014 FEATURES & CHANGES: Miscellaneous: Made some changes to the tournament banning UI making it clearer when presenting the results of the ban phase.     Patch notes for Crius 1.9 Released on Wednesday, August

---

Patch notes for Crius 1.10Released on Friday, August 15th, 2014


## FEATURES & CHANGES:


**Miscellaneous:**


- Made some changes to the tournament banning UI making it clearer when presenting the results of the ban phase.


Patch notes for Crius 1.9Released on Wednesday, August 13th, 2014


## FIXES:


**Industry**


- Industry will no longer accept un-packaged ships as part of the material requirements for a job.
- Fixed the blueprint material requirements for building some tech 2 exploration frigates and transports.
- Fixed the blueprint material requirements for mobile warp disruptors and 125mm auto cannons.


Patch notes for Crius 1.8Released on Thursday, August 7th, 2014


## FEATURES & CHANGES:


**Industry**


- Added the ability to pay the job costs from either the personal or corporation wallet when installing jobs.
- Blueprint browser can now filter blueprints by groups using a dropdown or in the search box ie "ship" or "battlecruiser".



## FIXES:


**Gameplay**


- Cases where the hacking game window doesn't closing upon a successful hack has been fixed.


**Industry**


- Fixes cost, time and material calculations not updating after jump cloning with implants.
- Active and past jobs now correctly display as blueprint copies in the job browser.
- Raised the throttle limit on swapping between blueprints in the industry window.
- Fixed the calculation of material requirements when the material is an assembled ship.
- Active jobs now show the correct output ME / TE / runs based on selected decryptors Improved the performance of the blueprint browser when installing multiple jobs in quick succession.
- Impounded blueprints will no longer display in the blueprint browser.
- Fixed an issue with locked blueprints in secure containers displaying location twice in the location selector.
- Fixed a missing label on the jobs browser for the reverted state.
- Reimbursing incorrect costs for ME and TE Research jobs installed between 22.07.2014 11:00 and 23.07.2014 11:00.
- Minor style change to the activity icons on the industry window.
- Removing the blueprint from the industry window no longer leaves the 3D preview showing.


**User Interface**


- Fixed an issue where a number of items were missing their estimated price.
- Switching subsystems for Tech 3 ships in the 3D preview will no longer re-animate the camera.



## THIRD PARTY DEVELOPERS:


**EVE API**


- Fixed an error caused by FoxFour failing to understand copy and paste causing longitude and latitude for the PlanetaryPins endpoint to be identical.
- Added CORS header to the API for those of you looking to do more JavaScript client shenanigans.


**STATIC DATA EXPORT**


- Added missing market groups to the Static Data Export.


Patch notes for Crius 1.7Released on Friday, August 1st, 2014


## FIXES:


**User Interface**


- The Start button in the Industry window will no longer display red incorrectly, even if you could submit the job.


Patch notes for Crius 1.6Released on Thursday July 31st, 2014


## FEATURES & CHANGES:


**Industry**


- Added a 3D preview of ships and turrets to the industry window when manufacturing.
- T2 types should no longer require T1 materials (minerals and components) as part of their build requirements, with the exception of Capital Jump Drive components in Black Ops and Jump Freighters.
- Material quantities in T2 items (and other items which are built from other buildable items but reprocess down into base materials) should be corrected, resulting in the correct outputs from reprocessing. This should not change build requirements.
- Max production limits for blueprints have been revised to more accurately round to 1 significant figure.
- Tweaked blueprint data for perpetual motion units.
- Algos blueprint stats corrected to be in line with other destroyers.



## FIXES:


**Gameplay**


- An issue with the Ejected Sleeper Databank loot container has been fixed.
- An issue where some player's Drone Avionics skill was lowered has been fixed.


**Industry**


- Fixed Tech II blueprints that still contained Tech I components for maufacturing.
- Fixed Tech III blueprint requirements.
- Numerous other adjustments to blueprint build requirements and times.
- Fixed an issue where some outpost upgrades were applying their time / material efficiency bonuses twice.
- Paused jobs can now be cancelled without onlining the facility.


**User Interface**


- The station guest list and counter now updates when characters dock and undock.


Patch notes for Crius 1.5Released on Tuesday July 29th, 2014


## FEATURES & CHANGES:


**Industry**


- Advanced Industry skills changed to a 3% reduction in job time per skill level for all industry activities.
- Added an installer filter to the jobs tab on the industry window.



## FIXES:


**Industry**


- Rounding issues when calculating material quantities have been fixed.
- Fixed the calculation of product volume when delivering industry jobs, and volume restrictions now only apply to containers.
- Removed the reprocessing option for Harvestable Clouds.
- Some reverse engineering jobs were giving the same output subsystem, this is no longer the case.
- The industry window now remembers which tab was selected.
- The manufacturing tooltip in the facilities tab shows now the correct values for facilities with a bonus (such as an upgraded Outpost).


Patch notes for Crius 1.4Released on Monday July 28th, 2014


## FIXES:


**Exploration**


- Wormhole C391 has had its mass per jump corrected.
- K-space to C6 wormholes have calmed down a little and are now appearing at a more relaxed rate.


**Gameplay**


- The following Team Specialties now affect the correct products: Starbase Weapons, Starbase Defense, Starbase Processing, Starbase Production, Starbase Storage.


**Localization**


- The skill description for “advanced industry” is now correct in German.
- All ore, mineral and ice descriptions are now formatted correctly in German.


**Market**


- The bubble plank stabilizers have been fixed and the various EVE Markets should now properly work without breaking.


**User Interface**


- Teams that were selected during the Invention process will no longer be locked in with no way to remove them.
- The reprocessing window will now update correctly if items are added after a previous reprocess.


Patch notes for Crius 1.3Released on Friday July 25th, 2014


## FIXES:


**Science & Industry**


- Fixed a number of industry jobs that were failing to deliver.



## THIRD PARTY DEVELOPERS:


**EVE API**


- **/industry/facilities/** - The solar system, region, owner and type of facilities will now only contain the id
- **/industry/teams/{teamID}/** - Added - name
    - activity
  - You can now also access teams that are for auction this way
- **/industry/teams/ industry/teams/auction/** - The cache time has been reduced to 10 minutes


Patch notes for Crius 1.2Released on Thursday, July 24th, 2014


## FEATURES & CHANGES:


**Exploration**


- Component Assembly Facilities built by renegade Thukker Tribe members can now be seen anchored near the Guristas Research and Trade Hubs in low security space. It's rumored that these structures make use of advanced construction technology that was previously unknown outside the Thukker engineering community.


**Science & Industry**


- The Orca has had the Team specialization reclassified as Large Class (it was originally Medium Class).



## FIXES:


**Gameplay**


- The Ancient Tomb Dig Site container in the mission 'Recovery' can now be hacked with a Civilian Relic Analyzer.
- The Radio Telescope container in the mission 'Encounter at Station 464' can now be hacked with a Civilian Relic Analyzer.


**Science & Industry**


- Industry tab in ore Show Info will no longer display blank
- Facility drop down filter is now sorted by distance.
- The base price of the item when viewing an activity in a facility that does not support it will no longer be displayed, instead a dash will be shown.
- System cost bars are scaled properly.
- Blueprints and materials in secure containers with no password set can now be used in industry jobs.
- Fixed issues with the blueprint and output products going into the wrong containers when delivering jobs.
- The blueprint and job list in the industry UI will now update correctly as jobs are installed / delivered.
- Pre-Crius Reverse Engineering jobs can now be delivered.
- Applying the Police Pursuit cosmetic skin to the Federation Navy Comet is now exempt from all installation costs like the other ship skins.


**Skills**


- In the Kronos release the required skill for Drone Link Augmenters was changed from Combat Drone Operation to Drone Avionics. This was done without ensuring that players who fulfilled the skill requirements of those modules would still do so after the change. In this patch we are bumping up the level of Drone Avionics for all players to the same level that they had Combat Drone Operation when we deployed Kronos. Players who have trained Drone Avionics in the meantime will be given unallocated skillpoints instead up to the amount that their skill would have been adjusted.


**Structures & Deployables**


- Corporate Hangar Arrays cargohold has been increased from 1,400,000 m3 to 3,000,000 m3
- Ammunition Assembly Array cargohold has been increased from 150,000 m3 to 1,000,000 m3
- Component Assembly Array cargohold has been increased from 1,000,000 m3 to 1,500,000 m3
- Drone Assembly Array cargohold has been increased from 150,000 m3 to 1,000,000 m3
- Equipment Assembly Array cargohold has been increased from 500,000 m3 to 1,000,000 m3
- Rapid Equipment Assembly Array cargohold has been increased from 500,000 m3 to 1,000,000 m3


**User Interface**


- The Facility Location filter in the Teams section of the Industry window will now correctly filter by facility if it has been changed.


Patch notes for Crius 1.1Released on Wednesday, July 23rd, 2014


## FIXES:


**Audio**


- Audible clicks in booster sounds have been fixed.


**Gameplay**


- An [exploit](//community.eveonline.com/news/news-channels/eve-online-news/drone-damage-exploit-notification/) where abandoned drones maintained bonuses from previous owners has been fixed


**Industry**


- Copy and research jobs that have no material requirements no longer need access to the first division hangar.
- Jobs in progress are now removed from the jobs tab when the POS structure, where the job was installed at, got destroyed.
- Setting facility tax in a POS now takes immediate effect.
- The calculation of research job costs has been fixed.
- The Rapid Equipment Assembly Array works now with 5% material efficiency penalty which was previously missing.
- The invention times on mining crystals and the Perpetual Motion Unit have been fixed.


**User Interface**


- When viewing teams while located in wormhole space, we now show them as unreachable instead of using the maximum integer value.
- Some items that were not able to be reprocessed (such as deployables) can now be reprocessed without issue.
- Blueprint show info now correctly reflects the current ME and TE levels.


Patch notes for Crius 1.0Released on Tuesday, July 22nd, 2014


## FEATURES & CHANGES :


**Asteroids, ices and minerals**


- All minerals, ice products gained by reprocessing ores and ices have been increased by 38.1% to compensate for the reprocessing changes
- Alchemy material amounts have been increased by 81% to compensate for the reprocessing changes
- Units of ore / ice needed to reprocess have been unified to 100 for all ores and ices
- Mexallon has been added to Prime Arkonor, Crimson Arkonor and Arkonor
- Pyerite quantity gained by reprocessing Triclinic Bistot, Monoclinic Bistot and Bistot has been increased
- Nocxium quantity gained by reprocessing Crystalline Crokite, Sharp Crokite and Crokite has been increased
- All mineral, ice products show info descriptions now mention which ores and ices they are reprocessed from
- All ore and ice descriptions now explain in which solar system security status they may be found
- The volume of all Isotopes has been reduced to 0.1m3


 Exact numbers below (figures on the "[Reprocess all the things Dev Blog](//community.eveonline.com/news/dev-blogs/reprocess-all-the-things)" are out of date):


- 100 units of Prime Arkonor now yield 7596 Tritanium, 1406 Mexallon, 253 Megacyte, 127 Zydrine
- 100 units of Crimson Arkonor now yield 7251 Tritanium, 1342 Mexallon, 242 Megacyte, 121 Zydrine
- 100 units of Arkonor now yield 6905 Tritanium, 1278 Mexallon, 230 Megacyte, 115 Zydrine
- 100 units of Bistot now yield 16572 Pyerite, 118 Megacyte, 236 Zydrine
- 100 units of Triclinic Bistot now yield 17402 Pyerite, 124 Megacyte, 248 Zydrine
- 100 units of Monoclinic Bistot now yield 18230 Pyerite, 130 Megacyte, 259 Zydrine
- 100 units of Crokite now yield 20992 Tritanium, 275 Nocxium, 367 Zydrine
- 100 units of Sharp Crokite now yield 22041 Tritanium, 290 Nocxium, 385 Zydrine
- 100 units of Crystalline Crokite now yield 23091 Tritanium, 304 Nocxium, 403 Zydrine
- 100 units of Dark Ochre now yield 8804 Tritanium, 173 Nocxium, 87 Zydrine
- 100 units of Onyx Ochre now yield 9245 Tritanium, 182 Nocxium, 91 Zydrine
- 100 units of Obsidian Ochre now yield 9685 Tritanium, 190 Nocxium, 95 Zydrine
- 100 units of Iridescent Gneiss now yield 1342 Tritanium, 1342 Mexallon, 254 Isogen, 63 Zydrine
- 100 units of Prismatic Gneiss now yield 1406 Tritanium, 1406 Mexallon, 266 Isogen, 65 Zydrine
- 100 units of Gneiss now yield 1278 Tritanium, 1278 Mexallon, 242 Isogen, 60 Zydrine
- 100 units of Vitric Hedbergite now yield 85 Pyerite, 206 Isogen, 103 Nocxium, 10 Zydrine
- 100 units of Glazed Hedbergite now yield 89 Pyerite, 216 Isogen, 108 Nocxium, 10 Zydrine
- 100 units of Hedbergite now yield 81 Pyerite, 196 Isogen, 98 Nocxium, 9 Zydrine
- 100 units of Vivid Hemorphite now yield 189 Tritanium, 76 Pyerite, 18 Mexallon, 62 Isogen, 123 Nocxium, 9 Zydrine
- 100 units of Radiant Hemorphite now yield 198 Tritanium, 79 Pyerite, 19 Mexallon, 65 Isogen, 129 Nocxium, 9 Zydrine
- 100 units of Hemorphite now yield 180 Tritanium, 72 Pyerite, 17 Mexallon, 59 Isogen, 118 Nocxium, 8 Zydrine
- 100 units of Pure Jaspet now yield 76 Tritanium, 127 Pyerite, 151 Mexallon, 76 Nocxium, 3 Zydrine
- 100 units of Pristine Jaspet now yield 79 Tritanium, 133 Pyerite, 158 Mexallon, 79 Nocxium, 3 Zydrine
- 100 units of Jaspet now yield 72 Tritanium, 121 Pyerite, 144 Mexallon, 72 Nocxium, 3 Zydrine
- 100 units of Luminous Kernite now yield 140 Tritanium, 281 Mexallon, 140 Isogen
- 100 units of Fiery Kernite now yield 147 Tritanium, 294 Mexallon, 147 Isogen
- 100 units of Kernite now yield 134 Tritanium, 267 Mexallon, 134 Isogen
- 100 units of Mercoxit now yield 293 Morphite
- 100 units of Magma Mercoxit now yield 308 Morphite
- 100 units of Vitreous Mercoxit now yield 323 Morphite
- 100 units of Silvery Omber now yield 89 Tritanium, 36 Pyerite, 89 Isogen
- 100 units of Omber now yield 85 Tritanium, 34 Pyerite, 85 Isogen
- 100 units of Golden Omber now yield 94 Tritanium, 38 Pyerite, 94 Isogen
- 100 units of Azure Plagioclase now yield 112 Tritanium, 224 Pyerite, 112 Mexallon
- 100 units of Rich Plagioclase now yield 117 Tritanium, 234 Pyerite, 117 Mexallon
- 100 units of Plagioclase now yield 107 Tritanium, 213 Pyerite, 107 Mexallon
- 100 units of Pyroxeres now yield 351 Tritanium, 25 Pyerite, 50 Mexallon, 5 Nocxium
- 100 units of Solid Pyroxeres now yield 368 Tritanium, 26 Pyerite, 53 Mexallon, 5 Nocxium
- 100 units of Viscous Pyroxeres now yield 385 Tritanium, 27 Pyerite, 55 Mexallon, 5 Nocxium
- 100 units of Scordite now yield 346 Tritanium, 173 Pyerite
- 100 units of Condensed Scordite now yield 363 Tritanium, 182 Pyerite
- 100 units of Massive Scordite now yield 380 Tritanium, 190 Pyerite
- 100 units of Spodumain now yield 39221 Tritanium, 4972 Pyerite, 78 Megacyte
- 100 units of Bright Spodumain now yield 41182 Tritanium, 5221 Pyerite, 82 Megacyte
- 100 units of Gleaming Spodumain now yield 43143 Tritanium, 5469 Pyerite, 86 Megacyte
- 100 units of Veldspar now yield 415 Tritanium
- 100 units of Concentrated Veldspar now yield 436 Tritanium
- 100 units of Dense Veldspar now yield 457 Tritanium
- 1 unit of Clear Icicle now yields 69 Heavy Water, 35 Liquid Ozone, 414 Helium Isotopes and 1 Strontium Clathrates
- 1 unit of Enriched Clear Icicle now yields 104 Heavy Water, 55 Liquid Ozone, 483 Helium Isotopes and 1 Strontium Clathrates
- 1 unit of White Glaze now yields 69 Heavy Water, 35 Liquid Ozone, 414 Nitrogen Isotopes and 1 Strontium Clathrates
- 1 unit of Pristine White Glaze now yields 69 Heavy Water, 35 Liquid Ozone, 483 Nitrogen Isotopes and 1 Strontium Clathrates
- 1 unit of Blue Ice now yields 69 Heavy Water, 35 Liquid Ozone, 414 Oxygen Isotopes and 1 Strontium Clathrates
- 1 unit of Thick Blue Ice now yields 104 Heavy Water, 55 Liquid Ozone, 483 Oxygen Isotopes and 1 Strontium Clathrates
- 1 unit of Glacial Mass now yields 69 Heavy Water, 35 Liquid Ozone, 414 Hydrogen Isotopes and 1 Strontium Clathrates
- 1 unit of Smooth Glacial Mass now yields 104 Heavy Water, 55 Liquid Ozone, 483 Hydrogen Isotopes and 1 Strontium Clathrates
- 1 unit of Glare Crust now yields 1381 Heavy Water, 691 Liquid Ozone, 35 Strontium Clathrates
- 1 unit of Dark Glitter now yields 691 Heavy Water, 1381 Liquid Ozone, 69 Strontium Clathrates
- 1 unit of Gelidus now yields 345 Heavy Water, 691 Liquid Ozone, 104 Strontium Clathrates
- 1 unit of Krystallos now yields 173 Heavy Water, 691 Liquid Ozone, 173 Strontium Clathrates
- 1 unit of Unrefined Caesarium Cadmine now yields 164 Cadnium, 36 Caesarium Cadmide
- 1 unit of Unrefined Crystallite Alloy now yields 164 Cobalt, 36 Crystallite Alloy
- 1 unit of Unrefined Dysporite now yields 73 Dysporite, 173 Mercury
- 1 unit of Unrefined Fernite Alloy now yields 36 Fernite Alloy, 164 Scandium
- 1 unit of Unrefined Ferrofluid now yields 73 Ferrofluid, 173 Hafnium
- 1 unit of Unrefined Fluxed Condenstates now yields 73 Fluexed Condensates
- 1 unit of Unrefined Hexites now yields 36 Hexite
- 1 unit of Unrefined Hyperflurite now yields 73 Hyperflurite, 173 Vanadium
- 1 unit of Unrefined Neo Mercurite now yields 173 Mercury, 73 Neo Mercurite
- 1 unit of Unrefined Platinum Technite now yields 36 Platinum Technite, 164 Platinum
- 1 unit of Unrefined Promethium Mercurite now yields 173 Mercury, 73 Promethium Mercurite
- 1 unit of Unrefined Prometium now yields 173 Cadmium, 73 Prometium
- 1 unit of Unrefined Rolled tungsten Alloy now yields 36 Rolled Tungsten Alloy, 164 Tungsten
- 1 unit of Unrefined Solerium now yields 164 Chromium, 36 Solerium
- 1 unit of Unrefined Thulium Hafnite now yields 173 Hafnium, 73 Thulium Hafnite
- 1 unit of Unrefined Titanium Chromide now yields 36 Titanium Chromide, 164 Titanium
- 1 unit of Unrefined Vanadium Hafnite now yields 36 Vanadium Hafnite, 164 Vanadium


**Compressed ore and ice**


- Ore and ice may now be compressed directly inside the Starbase Compression Array or Rorqual (in industrial mode) by right-clicking them and selecting "compress"
- Compressed ore and ice mechanics have been changed. They now give the same quantities as non-compressed ore and ice variants, but have reduced volume (please refer to the non-compressed ore and ice above for mineral outputs)


Exact numbers (figures on the "[Reprocess all the things Dev Blog](//community.eveonline.com/news/dev-blogs/reprocess-all-the-things)" are out of date):


- 1 unit of Compressed Arkonor, Compressed Crimson Arkonor and Compressed Prime Arkonor now has a volume of 3.08m3
- 1 unit of Compressed Bistot, Compressed Monoclinic Bistot and Compressed Triclinic Bistot now has a volume of 6.11m3
- 1 unit of Compressed Crokite, Compressed Crystalline Crokite and Compressed Sharp Crokite now has a volume 7.81m3
- 1 unit of Compressed Dark Ochre, Compressed Obsidian Ochre and Compressed Onyx Ochre now has a volume of 3.27m3
- 1 unit of Compressed Gneiss, Compressed Iridescent Gneiss and Compressed Prismatic Gneiss now has a volume of 1.03m3
- 1 unit of Compressed Hedbergite, Compressed Vitric Hedbergite and Compressed Glazed Hedbergite now has a volume of 0.14m3
- 1 unit of Compressed Hemorphite, Compressed Radiant Hemorphite and Compressed Vivid Hemorphite now has a volume of 0.16m3
- 1 unit of Compressed Jaspet, Compressed Pristine Jaspet and Compressed Pure Jaspet now has a volume of 0.15m3
- 1 unit of Compressed Kernite, Compressed Fiery Kernite and Compressed Luminous Kernite now has a volume of 0.19m3
- 1 unit of Compressed Mercoxit, Compressed Magma Mercoxit and Compressed Vitreous Mercoxit now has a volume of 0.1m3
- 1 unit of Compressed Omber, Compressed Golden Omber and Compressed Silvery Omber now has a volume of 0.07m3
- 1 unit of Compressed Plagioclase, Compressed Rich Plagioclase and Compressed Azure Plagioclase now has a volume of 0.15m3
- 1 unit of Compressed Pyroxeres, Compressed Solid Pyroxeres and Compressed Viscous Pyroxeres now has a volume of 0.16m3
- 1 unit of Compressed Scordite, Compressed Massive Scordite and Compressed Condensed Scordite now has a volume of 0.19m3
- 1 unit of Compressed Spodumain, Compressed Gleaming Spodumain and Compressed Bright Spodumain now has a volume of 16m3
- 1 unit of Compressed Veldspar, Compressed Concentrated Veldspar and Compressed Dense Veldspar now has a volume of 0.15m3
- Compressed ice volumes have not been changed


**Exploration**


- Added a mysterious new beacon in the Metropolis region...


**Factional Warfare**


- Factional Warfare upgrades no longer give extra station slots and instead reduce NPC price on all industry activities by 10% per solar system upgrade level
- The damage and tracking of Factional Warfare Complex NPCs has been reduced significantly.


**Market**


- Icons have been added to all market groups in an effort to improve visibility
- The "Manufacture & Research" market group has been re-organized. It is now split into three with Components, Materials and Research Equipment folders


**Reprocessing**


- The reprocessing formula has been changed:Most of instances referring to “refining” (station service, star map and numerous miscellaneous entries) have been changed to “reprocessing”The formula change means the highest ore and ice reprocessing rate has been decreased from 100% to 72.4% at a 50% NPC station (counting a 4% reprocessing implant) - From Station Equipment + 0.375 x (1 + Refining skill x 0.02) x (1 + Refining Efficiency skill x 0.04) x (1 + Ore Processing skill x 0.05) x (1 + Reprocessing Implant)
  - To Station Equipment x (1 + Refining skill x 0.03) x (1 + Refining Efficiency skill x 0.02) x (1 + Ore Processing skill x 0.02) x (1 + Reprocessing Implant)


**Industry**


- Material Efficiency calculations are now applied to the whole jobs, not individual runs. This means manufacturing a large batch of items will still give some reduction on Assembly Arrays instead of being simply negated. - We will be rounding up to the next significant digit, which means that 14.4 Tritanium required to manufacture 10x cheap-quality holoreels will actually be rounded to 15.
  - Whole and single items will not be affected by this calculation. This is most relevant for Tech I items required for the manufacturing of Tech II variants. For example, building 10 Paladins will not require 9 Apocalypse if you have a 10% ME.
- All instances of "Productivity Level" have been renamed into Time Efficiency
- All instances of "Research Productivity" have been renamed into Time Efficiency Research
- All instances of "Material Level" have been changed to Material Efficiency
- All instances of "Material Research" have been renamed into Material Efficiency Research
- Research has been overhauled via the following changes: - Wastage Factor has been removed from the game. To compensate for that, all build costs have been increased by 11.11%
  - Blueprint research has been changed to a 10 level system. Each Material Efficiency level (ME) reduces blueprint required materials by 1%, and each Time Efficiency level (TE) reduces blueprint manufacturing time by 2%
  - It is no longer possible to research beyond ME 10 and / or TE 20 on any blueprint
  - Blueprints have been sorted into ranks, with higher ranks having longer research and manufacturing times
  - Copy times on all blueprints have been adjusted to require 80% of the manufacturing time
  - All blueprint manufacturing times have been changed to be a function of the new blueprint rank (see above, the "[Research the Future](//community.eveonline.com/news/dev-blogs/researching-the-future/)" Dev Blog and [this forum thread](//forums.eveonline.com/default.aspx?g=posts&t=351172&find=unread) for details)
  - The number of maximum runs for Tech I non-component items has been adjusted to have approximately 2 days of build time
  - The number of maximum runs of component blueprints has been adjusted to have approximately one week of build time
  - Blueprints for building special edition ships and ship skins will always have a job cost of 0
  - The Amarr, Caldari, Gallente and Minmatar Hybrid Tech Decryptors needed for Reverse Engineering have been renamed Amarr, Caldari, Gallente and Minmatar Subsystems Data Interfaces. Their respective icons have been changed as well
  - The R.A.M.- Hybrid Technology item needed for Reverse Engineering has been renamed R.Db.- Hybrid Technology. Its icon has been changed as well
- First set of changes to Invention include: - Invention now removes one run from the input blueprint copy instead of consuming it entirely
  - Invention no longer returns negative Material Efficiency or Time Efficiency Tech II blueprint copies. Output blueprint copies now have 0 or positive ME and TE values
  - Invention time on blueprints now approximately equals manufacturing time on the Tech II product item, divided by two, minus Tech I copy time for one run of the source item - Example: a Megathron blueprint invention time now approximately equals half the manufacturing time of the Kronos minus one run copy time of the Megathron blueprint
  - Decryptor TE bonuses have been doubled to take into account the research changes
- The damage per run mechanic has been removed from the game. This mainly affects R.A.M. and R.Db items - R.A.M. and R.Db requirements have been multiplied by 100 on all jobs that required them (mainly Tech II manufacturing and research)
  - All R.A.M. and R.Db blueprints now produce 100 more items for the same amount of materials
  - R.A.M. and R.Db volume has been divided by 100
  - Please refer to the "[Building Better Worlds](//community.eveonline.com/news/dev-blogs/building-better-worlds/)" Dev Blog for more details
- Extra Materials have been removed from the game. This mainly affects Tech I and Tech II manufacturing and research - All Extra Materials have been moved as regular Materials instead
- Most Tech I materials have been removed from Tech II blueprints - More precisely, minerals that are not morphite and components that are not Advanced Components or Advanced Capital Components have been removed
  - This does not apply to Tech I items required for Tech II manufacturing, those are staying and still have exceptions to the Material Efficiency and skill bonuses so that, for example:In some cases blueprint requirements have been modified to make sure price is not fluctuating too much - A Paladin should never require require 2 Apocalypses to build
    - Large shield Extender II should never require 0.75 Large Shield Extender I to build
- Manufacturing, Material Efficiency, Time Efficiency, Copy, Invention and Reverse Engineering slots have been removed from the game - Limitation on industry jobs is now based on facility pricing, which is calculated from the solar system facilities, team costs and other variables. For more information please refer to "[The Price of Change](//community.eveonline.com/news/dev-blogs/the-price-of-change/)" dev blog
  - Many blueprints with inconsistent values have been unified, please refer to "[Researching, the Future](//community.eveonline.com/news/dev-blogs/researching-the-future/)" Dev Blog for more details
- Production and research teams are now available - Teams can be viewed and manipulated from the Teams tab in the Industry window
  - The default view displays teams available for use
- Each team has a type, name, location, specialties, salary and retirement timeAny job in a given system can opt to pay any team's salary cost in order to use that team with that job, without restrictionAny job using a team gains the specialties bonuses listed for that team, either to job length (as indicated by an hourglass) or job material cost (as indicated by a diamond). Only specialties which include the specific blueprint type being used (see above) are applied - The type is one of Manufacturing, ME Research, TE Research, Copying
  - The name contains their corporate affiliation and a callsign encoding what type of team they are and their core specialty
  - Their location is a star system within New Eden, which includes Sleeper-infested wormhole space
  - Each team has a core specialty, which is one of Structure, Components, Consumables, Ships, Equipment or Mobile, and then various other specialties which give enhanced bonuses. For a list of specialties and what they apply to, please refer to the "[Teams and the Revamp of Industry in EVE Online](//community.eveonline.com/news/dev-blogs/teams-and-the-revamp-of-industry-in-eve-online/)" dev blog
  - Salary is a cost modifier on job install cost, between 2% and 18%
  - Retirement time indicates when the team will retire, and no longer be usable
- Selecting a blueprint and job type will automatically filter teams which give a bonus to that particular job, highlighting the particular specializations that apply; these can be filtered down by location
- Starting a job with a given team does not affect that team's availability for other jobs
- Clicking the "Team Chartering" option at the bottom of the Teams tab switches the tab to Chartering view
- Here you can see all teams that are available for chartering, a process which allows you to bid for these teams to move to a particular system
- The information display is much the same as for the default view in appearance and functionality, but with two visible changes: - "Retirement" is replaced with "auction ends", which tells you when the auction ends, which is seven days after it begun
  - There is an additional "auction" column, which lists the current bid price and allows you to submit a bid of your own
- You can click the "Bid" button to enter a system name and bid amount you wish to make, placing the bid into escrow; systems further away have a higher minimum bid price, to cover the team's cost of relocationOn submitting a bid, you are notified of the transaction via mailAll bids for a given team to move to a given system are pooled, with the system having the largest total pool winning the auction when the auction ends
- You must hit ENTER for at least 3 characters of the solar system you want to relocate a team to
- When the auction ends, the ISK from all losing bids is returned from escrow, and the team moves to the winning system, where it becomes available for use for 28 days
- Everyone who has bid on an auction is notified of the results when the auction ends
- New teams become available for chartering on a regular basis, randomly generated from all the possible combinations and locations (note that teams are never created in wormhole systems, although they may be chartered to move there)
- Teams whose auctions expire with no successful bids leave the game
- Teams who are available for use but are unused (no active jobs) for a 48-hour period will cease to be available and put themselves up for chartering for seven days


**Outposts**


- All player-made outposts now have a 50% reprocessing facility by default, while the Minmatar outpost starts at 52%
- Amarr, Caldari and Gallente outposts may be upgraded with refinery improvement platforms to 52%, 54% and 57% reprocessing efficiency to ores and ices (not applicable to other items)
- Minmatar outposts may be upgraded with refinery improvement platforms to 54%, 57% and 60% reprocessing efficiency to ores and ices (not applicable to other items)
- Improvement platforms that added manufacturing slots instead increase Material Efficiency by 1%. This may be cumulated
- Improvement platforms that added research slots (ME, TE, copy, invention) now reduce research costs by 10%. This may be cumulated on a multiplicative manner
- Assembly line settings for industry jobs have been added to outposts. They are available under the "Station Management" window for outposts owner, and have similar options to Customs Offices. They allow players to filter access and set taxes based on corporation standings


**Structures & Deployables**


- It is no longer possible to remotely use a blueprint in a Starbase structure. Blueprints are now required to be in the same Starbase structure that the job input / output materials are in - Please note it is still possible to remotely start a blueprint, as long as the blueprint and materials remain in the same location
- Control Towers anchoring mechanics have been changed
- Faction standings are no longer required to anchor Control Tower in high-security space (they still require charters however)
- 0.8 and above solar systems are now eligible for Control Tower anchoring (except for a few restricted solar systems, like Jita)
- Newly created corporations now need to wait 7 days before being allowed to anchor Control Towers
- Starbase Reprocessing Arrays have been overhauledThe Reprocessing Array may be anchored anywhere, requires 750 CPU, 150,000 powergrid, has 52% base reprocessing efficiency and 200,000m3 cargoholdThe Intensive Reprocessing Array may be anchored in 0.4 or lower, requires 1,000 CPU, 200,000 powergrid, 54% base reprocessing efficiency and 200,000m3 cargohold - They now reprocess instantly, may have different types of ore and ice in their cargo and take reprocessing skills into account (ships and modules are not allowed however)
  - Materials are reprocessed directly by right-clicking them in the structure cargohold – this is no longer done by right-clicking the structure itself
- A Compression Array has been introduced - This structure compresses ore and ice instantly by right-clicking them in its cargohold
  - It may be anchored anywhere, requires 500 CPU, 100,000 powergrid and has a 2,000,000m3 cargohold
- Mobile Laboratories have been overhauled - Mobile Laboratory has been renamed Research Laboratory
  - Advanced Mobile Laboratory has been renamed Design Laboratory
  - Hyasyoda Mobile Laboratory has been renamed Hyasyoda Laboratory
  - Research Laboratories now have a 0.7 Material Efficiency and Time Efficiency time multiplier
  - Design Laboratories now have a 0.6 copying time multiplier, and a 0.5 invention time multiplier
  - Hyasyoda Laboratories now have a 0.65 Material Efficiency and Time Efficiency time multiplier
- Assembly Arrays have been overhauled - All assembly arrays now have a 2% material reduction to manufactured products (except for the Drug laboratory, Subsystem System Array, Rapid Equipment Assembly Array and Supercapital Assembly Array). Assembly Arrays will keep their 25% time reduction
  - Advanced Assembly arrays no longer 10% have material waste. They now all have 2% material reduction like their regular counterparts
  - Rapid Equipment Array material waste now is 5% instead of 20%
  - X-Large Assembly Array has been renamed Capital Ship Assembly Array
  - Capital Assembly Array has been renamed Supercapital Ship Assembly Array
  - Corporate Hangar Arrays cargohold has been increased from 1,400,000 m3 to 3,000,000 m3
  - Ammunition Assembly Array cargohold has been increased from 150,000 m3 to 1,000,000 m3
  - Component Assembly Array cargohold has been increased from 1,000,000 m3 to 1,500,000 m3
  - Drone Assembly Array cargohold has been increased from 150,000 m3 to 1,000,000 m3
  - Equipment Assembly Array cargohold has been increased from 500,000 m3 to 1,000,000 m3
  - Rapid Equipment Assembly Array cargohold has been increased from 500,000 m3 to 1,000,000 m3
  - It is now possible to build Starbase structures in the Equipment Assembly Array and Rapid Equipment Assembly Array
- A Thukker Component Assembly Array has been introduced - This structure is meant to give an edge to capital ship manufacturing in low-security space
  - It may only be anchored within solar systems whose security status is between 0.1 and 0.4 (included), requires 150 CPU, 50,000 powergrid and has a 1,000,000m3 cargohold
  - It gives a 25% reduction in manufacturing time and 10% reduction in required materials
  - Can only build Capital Construction Components and Advanced Capital Construction Components
  - Thukker Component Assembly Array blueprints will occasionally drop from a particular rare deadspace structure
- The ozone fuel use of Jump Bridge starbase structures has been increased by 50%.
- The capacity of Jump Bridge starbase structures has been increased by 100%.


**Ships and Modules**


- The isotope fuel requirements of Capital Jump Drives, Jump Portal Generators and Doomsday Devices have been increased by 50%


**Skills**


- Starbase Defense Management now requires Anchoring trained at 4 instead of 5
- Supply Chain Management and Scientific Networking skills have been overhauledThe Material Efficiency skill is being renamed Advanced Industry, and now reduces manufacturing time by 1% per levelThe Refining skill has been renamed Reprocessing. This skill bonus has been increased from 2% to 3% per level - They now provide a 5 jump remote control range, up to a maximum of 25 solar systems for level 5
  - Region is no longer a limit to remotely start a job on such a manner
  - It is no longer necessary to have those two skills trained to level 1 in order to remote use a blueprint in the same solar system
- The Refining Efficiency skill has been renamed Reprocessing Efficiency. This skill bonus has been decreased from 4% to 2% per level. This skill now requires the Reprocessing skill to level 4 instead of 5 to train
- Arkonor Processing, Bistot Processing, Crokite Processing, Dark Ochre Processing, Gneiss Processing, Hedbergite Processing, Hemorphite Processing, Ice Processing, Jaspet Processing, Kernite Processing, Mercoxit Processing, Omber Processing, Plagioclase Processing, Pyroxeres Processing, Scordite Processing, Spodumain Processing, Veldspar Processing skill bonuses have been decreased from 5% to 2% per level
- All the skills listed above now only apply when reprocessing ores, ices and their compressed variations
- Scrapmetal Reprocessing now applies its bonus when reprocessing any item that is not an ore, ice or compressed variations.  This skill bonus has been decreased from 5% to 2% per level


**User Interface**


- The insurance list has now been split in to own ships and corp ships for those with relevant roles
- A "no label" label has been added in contacts lists so you can more easily find unlabeled contacts
- Flag exempt from fleet warp option has been added for those who don‘t want to take fleet warp. An icon is displayed next to the names of those in the fleet list so you‘ll know why those people didn‘t warp with the fleet
- You no longer need skills to fit modules and rigs. You will not, however, be able to online modules you don‘t have skills for
- The Reprocessing station service has been overhauled - for more details, please refer to the "[Reprocess all the things](//community.eveonline.com/news/dev-blogs/reprocess-all-the-things)" blog
- The "Science & Industry" service has been overhauled - for more details, please refer to the "[Industry UI](//community.eveonline.com/news/dev-blogs/industry-ui/)" blog
- The Show Info window for blueprints has been significantly improved and now filters activities more accurately
- Items now have an industry tab. It lists the blueprint the item is manufactured from, as well as materials given when reprocessing it, if applicable
- The "Planets" tab has been removed from the "Science and Industry" window and moved into its own window named "Planetary Colonies", located under the "business" section of the Neocom
- The Assembly Line settings have been removed from the Starbase Science and Industry window since it is no longer possible to remote use blueprints
- Ancient Relic icons have been changed to indicate they are similar to blueprints and can be used to start Reverse Engineering jobs
- Picking logic for brackets improved (less greedy)
- Bracket lists are now ‘sticky’ and remain until another bracket is moused over or the mouse is clicked
- Bracket list now shows entities on list with names in full
- Bracket list can display in either a bounded bracket list mode (box with background on list and wrapped lines) or a compact list mode (background only for icons and text lines floating with no wrap
- Compact bracket list mode can be toggled separately for both brackets gathered to the edges and brackets displayed in their correct positions in space via the General Settings -> Inflight panel of the Escape Menu
- Scrolling has been removed from bounded bracket list and the lists caps at 15 in both modes
- Bracket text now has a shadow to improve readability in bright background situations


**New Player Experience**


- The industry career path has been overhauled to reflect the changes made to industry. This includes:Basic tutorial text under Eve Help for Industry (Manufacturing, Mining and Reprocessing) have been updated - The Making Mountains of Molehills career arc
  - The Balancing The Books career arc


**Character migration**


- Compressed ore and ice blueprints have been removed and reimbursed to NPC order price
- Jobs installed or active during Crius deployment are dealt in the following mannerExisting Tech II blueprint copies are converted into the new Material Efficiency and Time Efficiency scale; all T2 BPCs will have 6 added to both ME and TE, and then converted as per the next patchnote - Jobs that were installed before the patch still use the old pricing and time until delivered
  - Blueprints that are using Starbases remotely will be delivered to the station they were installed into, not the Starbase. This is a one-time only move, blueprints inserted after Crius will need to be moved to Starbases
- Player blueprints are to be converted into the new Material Efficiency and Time Efficiency system based on the information at the end of the "[Researching, the Future](//community.eveonline.com/news/dev-blogs/researching-the-future/)" Dev Blog.
- For ME, ME0 blueprints become ME0%
- ME1 becomes ME5%
- ME2 becomes ME7%
- ME3 and ME4 become ME8%
- ME5 through ME9 become ME9%
- ME10 and above becomes ME10%
- For TE, PE0 becomes TE0%
- PE1 becomes TE10%
- PE2 becomes TE14%
- PE3 and PE4 become TE16%
- PE5 through PE9 become TE18%
- PE10 and above become TE20%
- This affects market orders, whose umber will be multiplied by 100 and price divided by the same amount to keep a balanced ratio
- Prices cannot go lower than 0.01 ISK per unit
- All stockpiles of R.A.M. and R.Db will be multiplied by 100 to fit the new system



## FIXES:


**Gameplay**


- Fixed an edge case with COSMOS containers not refilling correctly.
- Multiple text issues have been fixed.
- Multiple mission issues have been fixed.
- An issue where the hacking window appeared blank has been fixed.
- Sentry drones are now included in the list of affected drones for all drone specialization skills.
- Skill requirement for Civilian Hobgoblins lowered to Drones level 1.
- Fixed an issue preventing applied targeted effects from showing their names in the buff bar.
- Hardwiring implants that had outdated names have had their names changed to match the skills they refer to
- Zainou 'beancounter' refining implants have been renamed Zainou 'beancounter' reprocessing implants to be more consistent with the rest of the Crius industry changes
- C6 wormholes now have more formalized connections to K-space; the balance here has not changed, but they now have their own identifiers and distribution data
- K-space will now very occasionally distribute wormholes to C6 W-space


**Localization**

DE


- The German translation of the audio settings is now displayed correctly.
- Updated terminology for industry related activities: “reverse engineering” is now consistently translated as “Nachkonstruktion”, “reprocess” and “refine” are now both consistently translated as “aufbereiten”, “reprocessing” and “refining” are now both consistently translated as “Aufbereitung”.
- Various language fixes.


RU


- The consistency issues in the "People & Places" window are now resolved.
- The skill description of "Hacking and Archaeology" is now displayed correctly.
- New and updated terminology for industry and blueprint related activities.
- Various languages fixes.


**PvE**


- Expedition Frigates can now properly enter the acceleration gates in the Nation Mining Colony Incursion site.


**Technical**


- In-client patching system phased out. Game client no longer tries to use the legacy patch system and popups, players are rather directed to use the launcher to update their client.
- Probe scanning will now refresh correctly if the scanner window is open during a session change


**User Interface**


- Fixed an issue causing the in-space bracket list to persist between jumps.
- In-space bracket list icons now correctly display state changes.
- Fixed an issue with Advanced Military Stasis Webifiers tutorial where one of the steps would in rare cases display blank
- Changed rig size spelling from "Xlarge" to "X-Large" in ship show info description.
- Factional Warfare rules of engagements no longer incorrectly mention that the Loyalty Point Store offer costs are reduced with higher levels of faction control.
- Fixed the Rorqual bonuses to properly link to the Capital Shield Emission Systems window
- The message when you have assigned a label to a contact is now back.
- The guests station list count will now update when guests dock and undock.
- The search pop-up for assailable corporations/alliances will now respond to further search queries.
- The display names for Starbase security status has been corrected to include word level
- The message in local chat for the Encounter Surveilance System is now spelled correctly
- The weapon disruption icon text in the ISIS no longer refers to missile launchers
- The text in the war notification has been updated to note that it affects corporations both joining and leaving an alliance immediately



## THIRD PARTY DEVELOPERS:


**EVE API**


- Added corp/Facilities - Returns a list of all outpost and POS industrial facilities your corporation owns.
  - Cache time is 1 hour
- Added corp/IndustryJobsHistory - Returns a list of running or completed jobs for your corporation
  - A maximum of 10k rows or 90 days
  - Cache time is 6 hours
- Added char/IndustryJobsHistory - Returns a list of running or completed jobs for your character
  - A maximum of 10k rows or 90 days
  - Cache time is 6 hours
- Updated corp/IndustryJobs - Returns a list of running jobs for your corporatio
  - A maximum of 10k rows
  - Cache time is 15 minutes
- dated char/IndustryJobsFixed cache timers on the corp/Medals and api/ApiCalls endpoints - Returns a list of running jobs for your character
  - A maximum of 10k rows or 90 days
  - Cache time is 15 minutes


**Public Crest**


- Fixed a defect with alliance creator ID being the alliance executor ID instead of alliance creator ID as it clearly should be.
- Fixed a defect with all pages of a wars killmails returning the same data. Go killboards, parse those killmails!
- Exposed the CREST root ( [//public-crest.eveonline.com/](//public-crest.eveonline.com/) ) to public CREST.
- Added the MarketTypePriceCollection resource under market/prices/ - This returns a list of all items that have either an average market price or an adjusted price and what those values are.
  - Average price is the same as what you see when you select an item in your inventory.
  - Adjusted price is what the industry formulas use.
- Added the IndustryFacilityCollection resource under industry/facilities/ - This returns a list of all public facilities within New Eden.
  - You will still have to go to the SDE in order to figure out what activities are allowed at the facility and what the bonuses are.
- Added the SpecialityCollection resource under industry/specialities/ - Lists all specialities that can be associated with teams and what groups those specialties modify.
- Added the Speciality resource under industry/specialities// - Returns details on a single specified specialty.
- Added the TeamCollection resource under industry/teams - Returns a list of all active teams in the known universe of New Eden. This does not include WH space.
- Added the Team resource under industry/teams// - Returns details of a single specified team.
- Added IndustrySystemCollection resource under industry/systems/ - Lists the cost index for installing jobs in all the systems of the known universe. This does not include WH space.


**Static Data Export**


- Removed table invBlueprintTypes
- Removed table ramTypeRequirements
- Removed table ramAssemblyLines
- Added YAML file blueprints.yaml
- Jovian bloodlines should no longer cause issues


Tables which are existing, have been modified and will still be relevant to industry are:


- Column baseCostMultiplier added to ramAssemblyLineTypes
- Column costMultiplier added to ramAssemblyLineTypeDetailPerCategory
- Column costMultiplier added to ramAssemblyLineTypeDetailPerGroup
