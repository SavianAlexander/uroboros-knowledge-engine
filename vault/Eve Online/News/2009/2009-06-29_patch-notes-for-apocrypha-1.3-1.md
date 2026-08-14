# Patch Notes for Apocrypha 1.3

- **Date**: 2009-06-29T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-apocrypha-1.3-1
- **Tags**: #patch-notes

## Overview
Patch notes for Apocrypha 1.3, released 29, June, 2009\. Please note that Apocrypha 1.3.1, released 30, June, 2009 can be found under Post Patch Changes   Table of Contents FEATURES CHANGES FIXES POST PATCH CHANGES FEATURES Need for Speed The inventory service, which ke

---

**Patch notes for Apocrypha 1.3, released 29, June, 2009. Please note that Apocrypha 1.3.1, released 30, June, 2009 can be found under Post Patch Changes**

**Table of Contents**

[FEATURES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=190#features)[CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=190#changes)[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=190#fixes)[POST PATCH CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=190#postpatchchanges)

**FEATURES**

**Need for Speed**


- The inventory service, which keeps track of the ownership and location of everything in the game, has been changed to use the new database service backend to connect and communicate with the Tranquility database. This will yield noticably less network I/O and memory usage than the previous system. The performance of most inventory related operations will improve, but there may be cases where performance will degrade. We fully expect a good performance gain on the whole though. The in-memory inventory storage has had a new index added which will address "The Jita Problem“ where performance has been degrading over time as more items are primed in local storage. Maintaining an extra index induces some overhead, but frees the server from having to search through very large sets in highly populated systems. Degredation of searches over time is now a function of the player population at a given location and not a function of the number of items in a location as before. CCP Explorer provides full tech details in his dev blog [Encore: EVE Online 'Core'](//www.eveonline.com/devblog.asp?a=blog&bid=676)


**CHANGES**

**Tech 3**


- Several changes have been made to fix the cost of Tech 3 production: the volume of some gases required will be halved; the drop rate of the Neurovisual Input Matrix salvage item has been increased; and the material requirement for the power conduits has been switched from carbon-86 to Scandium Metallofullerene.
- Reverse Engineering will see several improvements. We are increasing the drop rate of Tech 3 datacores, increasing the runs on the blueprints from reverse engineering jobs and increasing the presence of radar sites in wormhole space.


**Modules**


- The Omnidirectional Tracking Link I has had its description changed and will now correctly state that it "Improves optimal range and tracking on all drones."
- Strip miners, ice harvesters, doomsdays, triage module, siege modules and other modules which previously used a CPU bonus on the ship to allow you to fit a special module now use a new “Can be Fitted To” attribute and no longer need the high base CPU to restrict the fitting of the module. The CPU on each of these types of modules has been adjusted to no longer require a 10,000 CPU base as a result of employing this new method.


**Weapons & Ammunition**


- The siege module explosion velocity penalty for Citadel Torpedoes has been changed from -92.5% to -60%.


**Drones**


- The drop rates for faction drone blueprints have been increased substantially. In addition, we have increased the material quantities needed in many containers for the parts required to make meta drones. The materials required to make faction drones and rogue drone component material volume have both been decreased.


**Skills**


- The pre-requisite skills for Capital Shield Operation have been changed. The new requirements for the training of this skill will be Shield Management V, Shield Operation V and Engineering V.


**Markets & Contracts**


- **Freeform contracts can no longer be created. This is due to griefing problems. You will still be able to view your completed freeform contracts for now but in an upcoming expansion older freeform contracts will be removed as well.**


**Starbases, Outposts and Stations**


- Multiple changes have been made to the anchoring and onlining of starbase modules and structures. All offensive starbase structure anchoring times have been reduced by 50% and all offensive starbase structure online times have also been reduced by 50%. Defensive starbase structures such as hardeners will have their anchoring, online and un-anchor times reduced by 50%. Finally, all starbase tower un-anchoring times have been reduced by 50%.


**Miscellaneous**


- The Basic Drone Control certificate will now require the skill Drones to be trained to Level 4.


**FIXES**

**Modules**


- All five variations of the Gas Harvester module have had the "Crystals Damage" attribute removed under Show Info. Since these modules do not use crystals, the attribute was redundant.
- Mousing over a module on the fitting screen will now always display the correct CPU and powergrid requirements when the target ship has a specific bonus to fitting. For example, hovering the mouse over a Covert Ops Cloaking Device II while in the fitting screen of a Covert Ops ship will display the proper CPU requirements. If you have Covert Ops trained to level V then it will display the CPU required as “0” rather than “10,000.”


**Tech 3**


- The Offensive Covert Reconfiguration System has had its description fixed and will no longer say that you can fit a Covert Cynosural Field Generator.
- The reverse engineering of the Intact Power Core ancient relic was incorrectly generating Electronics subsystem class BPC’s. This has now been rectified and the correct Engineering subsystem blueprints will be created as intended.


**Agents & Missions**


- A redundant empty room has been removed from the mission “Cash Flow for Capsuleers (4 of 10).”
- The mission “Cash Flow for Capsuleers (8 of 10)” has had the “objective completed” location fixed. Players will now be required to approach the destination as per the agent’s instruction. Previously, this mission would be marked as complete as soon as players warped into deadspace area.
- “Balancing the Books (3 of 10)” will now have the correct NPC, depending upon the faction you are running the mission for. Amarr variations will have a Blood Raider pirate, Caldari will have a Guristas pirate, Gallente will have a Serpentis pirate and Minmatar will have an Angel pirate.
- The NPC’s in the mission “Vitoc Vector - A Terrible Thing (4 of 4)” have been rebalanced. The overall number of enemies has been reduced but their difficulty has been increased.
- The missions “Delving into The Past (1 & 2 of 3)” now have their completion triggers fixed. The mission journal will now blink correctly when the mission objective has been looted from the container.
- The orbit range of the two rogue drones in the mission “Making Mountains out of Molehills (4 of 10)” has been reduced from 50 km to 5000 meters.
- The storyline mission dialogue for "The Numon Claim - Imperial Intervention (3 of 5)" will now correctly refer to the Amarrian Empress rather than Amarrian Emperor. Jamyl Sarum thought it more prudent to ask the agents to update their information rather than go through an unnecessary sex change.
- The mission “Drone Distribution” has had the name of some structures changed. In addition, players can also use a microwarpdrive in the mission area.
- Structures have been moved around in the deadspace areas for the missions “Angel Extravaganza” level 3, “Silence the Informant” level 3 and “Spies R Us (Serpentis version)” level 4.
- The mission “Spies R Us (Blood Raider version)” level 3 has had a missing trigger added. Additionally, the number of destroyers in this mission has been reduced.
- Grammatical errors have been fixed in the mission description for “Seek and Destroy.”
- A typographical error has been fixed in the pop up warning for the COSMOS mission "Contested Amarr Bastion of Blood."
- A grammatical error has been corrected in the name of the fighter group in the mission “The Big Sting (3 of 3).”
- A grammatical error has been corrected in the mission objective for “Lost Records.”


**Exploration & Deadspace**


- The exploration site "Blood Raider Naval Shipyard" will no longer throw an exception error in the final room.


**Science & Industry**


- The Reprocessing window will now refine large stacks of items much more quickly. The window has been adjusted to display a message that reprocessing is in progress and the speed has been increased up to 25 times faster. This fix will be released in a future patch


**Markets & Contracts**


- Many blueprints for COSMOS items have been added to the contracts database and can now be contracted normally.
- The Amarr Navy Heavy Capacitor Booster Blueprint is now published and can be searched in contracts.


**Graphics**


- Multiple NPC’s have had missing guns added to their ships. Now they look much cooler before you blow them up.


**User Interface**


- The starmap has been fixed and stars will no longer vanish when zooming in and out.
- The certificates for "Battleship Advanced Artillery Turrets - Elite" and "Battleship Advanced Beam Turrets - Elite" now display the correct description.
- A ship GUID icon has been added to the Show Info window for all Doomsday Devices.
- A grammatical error has been corrected in the error message displayed when attempting to overload Cruise Missile Launchers.
- We have cleaned up the double spaces and trailing of some names in groups and items. A search for said items will now yield the proper result.
- A grammatically incorrect attribute which was displayed in the Show Info of the Naglfar has been removed.
- A grammatical error has been corrected in the “Military-Damage Types (3 of 5)” tutorial.
- A grammatical error has been corrected in the World Map Control Panel.
- Several typographical errors have been corrected in the “Mining” tutorial.


**EVE Voice, Mail & Chat**


- It is now possible to join voice chat on newly created chat channels. The "Join Audio" button will now display correctly on all newly created player chat channels.
- Players can now join other player created channels normally without getting a message stating "You may own at most 10 mailing channels or mailing lists."


**Localized Clients**


- Several grammatical errors have been corrected in the Show Info window for all ships in the Russian client
- Several words which were displayed in English have been corrected in the German and Russian clients concerning player-owned structures.


**POST PATCH CHANGES**

**These fixes were added as Apocrypha 1.3.1 which was deployed during downtiime on 30, June, 2009.**

**Modules**


- Fixed an issue that causes focus scripts to not work correctly.


**Starbases, Outposts and Stations**


- Fixed an issue that was causing only one starbase gun to be controllable at a time.
