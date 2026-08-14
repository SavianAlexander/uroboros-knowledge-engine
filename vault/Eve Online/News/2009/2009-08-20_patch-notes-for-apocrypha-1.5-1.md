# Patch Notes for Apocrypha 1.5

- **Date**: 2009-08-20T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-apocrypha-1.5-1
- **Tags**: #patch-notes

## Overview
Patch notes for Apocrypha 1.5, released 20 August 2009.   Table of Contents FEATURES CHANGES FIXES POST-PATCH CHANGES FEATURES Ships Black Ops ships now have a dedicated fuel bay that can be used to store fuel for their covert cynosural generators and jump drives. The ba

---

**Patch notes for Apocrypha 1.5, released 20 August 2009.**

**Table of Contents**

[FEATURES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=191#features)[CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=191#changes)[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=191#fixes)[POST-PATCH CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=191#postpatchchanges)

**FEATURES**

**Ships**


- Black Ops ships now have a dedicated fuel bay that can be used to store fuel for their covert cynosural generators and jump drives. The bay can only hold ice; if you have fuel in both the fuel bay and the cargo hold it will be consumed from the fuel bay first.
- Carriers, Dreadnoughts, Motherships, Titans, Jump Freighters and the Rorqual now have special fuel bays accessible via the context menu of the ship. The fuel bays accept ice products such as isotopes or strontium. Jumping, or modules which use ice products such as siege modules, can be activated with fuel in this hold. Carriers, dreadnoughts, titans, and motherships class ships base cargo capacity is being lowered because of this change. The affected ships are: - Motherships: Nyx, Hel, Wyvern, Aeon
  - Carriers: Archon, Chimera, Thanatos, Nidhoggur
  - Dreadnoughts: Revelation, Phoenix, Moros, Naglfar
  - Titans: Leviathan, Erebus, Ragnarok, Avatar
  - Capital: Rorqual, Orca
  - Black Ops: Redeemer, Widow, Sin, Panther
  - Jump Freighters: Ark, Rhea, Anshar, Nomad
- The Orca and Rorqual now have a dedicated bay for storing ore. This bay can only contain unrefined and compressed ore.


**Rigs**


- All rigs and their blueprints now come in three sizes: small, medium and large. There are no changes in the rig bonuses, drawbacks or calibration requirements, only in the quantity of materials required to build them. Full details can be found at [My Rifter is equipped with the following rigs…](//www.eveonline.com/devblog.asp?a=blog&bid=670)
- Production times for rigs have been increased. Using junk to make state of the art equipment is not easy!


**Agents & Missions**


- Four new Epic Mission Arcs have been added, one for each of the four main Empire factions. These arcs will be of Level 4 mission difficulty and will be deeply rooted in the lore of New Eden. Here is a list of the agents giving out the first mission of the arcs: - Caldari: Aursa Kunivuri
  - Gallente: Roineron Aviviere
  - Amarr: Karde Romu
  - Minmatar: Arsten Takalo
- Players will not get a standing hit when they decline more than one Factional Warfare mission within a four hour interval, when they fail an accepted FW mission or when they let an accepted Factional Warfare mission expire.


**Factional Warfare**


- Killing player ships belonging to enemy militia now grants loyalty points for your own Factional Warfare militia. Please note: this only works for killing your militia direct opponent; a pilot in the Federal Defence Union will only receive loyalty points for destroying State Protectorate ships, not 24th Imperial Crusade assets. Please refer to [this Dev Blog](//www.eveonline.com/devblog.asp?a=blog&bid=671) for more details.
- In an effort to increase Factional Warfare rewards, all four Militias LP stores now have discounts on navy ship offers while proposing unique faction items to their pilots. Please refer to [this Dev Blog](//www.eveonline.com/devblog.asp?a=blog&bid=671) for more details.


**CHANGES**

**Need for Speed**


- When multiple players attacked another set of players in Empire space a notification about the aggression would be sent to everyone in the vicinity for each aggression. This contributed to what has been dubbed ‘Factional Warfare lag’. This has been fixed and should have a significant impact on reducing lag within Factional Warfare fleet fights.
- If ships were involved in deep collisions, where they intersected each other by a great amount sometimes desync between the server and client state would result. This has been reduced significantly. We will continue to work in this area in future patches.
- The efficiency when making any call to the Science & Industry system has been increased substantially, resulting in a much smoother performance and increased performance on the cluster.
- There is now less data in the offices and headquarters tabs in stations. Only the logo and the corporation name are displayed. Previously, the logo, corp name, URL, CEO and description were displayed. This has been done primarily for cluster performance reasons.
- The Directional Scanner can now only be activated once every 2 seconds. This has been done due to performance concerns and exploits.
- The market UI has now been streamlined in order to reduce calls to the server when looking up the average price of an item.
- Several other enhancements have been made to the cluster which will further increase performance.


**Tech III**


- The drop rate and quantity of the Neurovisual Input Matrix has been increased in Sleeper wrecks.


**Scanning & Probes**


- Updated probe range sphere graphics using a cleaner, more translucent pattern which remains visible at small scale. Moved away from green tint to blue.
- Added controlled delays to UI updates when state changes occurred in relation to probe scanning and/or probe control interaction. This allows refresh requests to be grouped, preventing multiple state changes in a very short time span which was spamming the client UI, causing multiple refreshes to graphics and severe performance hits.
- Removed helper axis-aligned grid lines that appeared when grabbing the scanner probe controls. This has notable performance benefits.
- Added thin blue circles that highlight where probe ranges intersect, giving a clear dynamic visual indication of overlap. Intersection lines fade out partially when probes are not moving.
- Added logarithmically-scaled range indicators inside a moving scanner probe control range sphere with a simple axis-aligned crosshair. The range indicators are only visible when grabbing the cube sides of the probe control which are aligned the same way. The range of the rings is always half the last ring starting from the probe range.
- Scanning with multiple probes would give just a single result dot when all probes got a hit rather than multiple dots. This has been fixed.
- Warpable results can now be bookmarked from the context menu.
- Warpable results can now be ignored from the context menu.


**Graphics**


- New graphics have been added for the capsule, warp tunnel effect, mining and ice mining graphic as well as energy vampire and warp scrambler effects.


**Miscellaneous**


- The shield and armor hit points for control bunkers in Factional Warfare have been increased by 50%.


**FIXES**

**Ships**


- The correct scan resolution will now be displayed on all Black Ops Battleships.
- Ammunition bonuses will now display correctly when ejecting and re-boarding a ship in space. Previously, bonuses would display incorrectly until the turret or missile bays were unloaded and reloaded. This was a display issue only.


**Modules**


- The Civilian Damage Control module will now correctly display a 30% resistance to thermal damage on a ship’s hull.
- A bug was introduced in Apocrypha 1.3 where the passive bonus of active hardeners was applied when the module was active. This has been fixed, and the passive bonus will no longer apply when armor or shield hardeners are active.


**Tech III**


- Malfunctioning Thruster sections will now correctly produce 10 run propulsion subsystem BPC's.
- The spawn container “Broken Sleeper Database” will no longer provide Minmatar Starship Engineering datacores and will now provide the correct propulsion subsystem datacore. No one wanted rusty datacores anyway.
- An issue regarding skill loss when a Tech III ship is destroyed has been fixed.


**Rigs**


- The description of the Core Defence Capacitor Safeguard II has been fixed and will now correctly state that it affects "... modules which require the Shield Operations skill."


**Starbases, Outposts & Stations**


- The “Equipment Assembly Array” model will now display correctly when anchored.


**Boosters & Implants**


- Crash Boosters will now have an effect on all types of missiles, both guided and unguided, resulting in a decreased factor of signature radius for all missile types.


**Agents & Missions**


- The mission “Royal Jelly” has had the proximity range to the habitation module fixed so that the mission can be completed successfully.
- The objective for the Epic Mission Arc “Data Retrieval” no longer requires you to destroy the Angel Forward Scout. You can simply collect the objective and return to your agent.
- The mission “The Navy Armada” will now display the Spaceshuttle wreck correctly.
- The name of the Level 2 mission “Seek and Destroy” now displays properly
- The Agent dialogue for “Cash Flow for Capsuleers (9 of 10)” has now been corrected and will no longer mention the perpetual motion device or any reference to the Guristas.
- The final mission on the Amarr branch of “Right to Rule” will now have the dungeon area location spread out to cover multiple systems. This prevents massive lag build up when multiple mission arcs are being done in one location
- The mission objective for the Epic Missions “Wildfire” and “Intaki Chase” will now appear correctly in the agent conversation and mission details window.
- The mission objective for “The Voting Trail (3 of 3)” will now show as complete when the Vengeful Officer has been destroyed.
- The mission “Their loss, our profit” will now have cargo containers spawn in the area in which an object was destroyed. Previously, the loot can would spawn beside the player’s ship, causing confusion.
- Mission descriptions for the Epic Mission Arc will now display correctly in the right-hand pane of the mission window as intended.
- A typographical error has been corrected in the mission briefing of “Seek and Destroy.”


**Exploration & Deadspace**


- The Guristas Troop Revigoration Camp will now display the link to the Guristas information rather than the Gallente Federation.
- All Angel cartel ships have been removed from the exploration site “Regional Blood Raider Data Mining Site.” All NPC's spawned will be Blood Raider vessels only.
- The Exploration site “Serpentis Annex’ now requires a Serpentis Gold Tag to activate the gate to the second stage.


**Graphics**


- Fixed minor graphic glitches on Level Of Detail of wrecks.
- The Gallente, Amarr and Serpentis control towers have had a graphical makeover and will now display the correct model, shade and textures. In addition, warping in and out to the tower when modules are being anchored will now display the model correctly.


**Sound & Audio**


- The sound issues experienced when the map was open have now been fixed and no further audio glitches will be heard.
- Sounds from the scanner, docking and in station ambient noise, warping and jumping through stargates have all been fixed and will now be heard correctly.
- F.O.F. Missiles will no longer persist in creating a sound effect when the target has been destroyed or when the missile bay has deactivated. Previously the launcher was just so happy to be firing that it would keep making noise until there was a session change.


**User Interface**


- Sorting items in the hangar will now display items of the same type (i.e. containers) correctly. Previously, the display would change order after sorting by name, then sorting by type, and sorting by name again.


**Localized Clients**


- A grammatical error has been corrected in the Science & Industry window for “Accept Quote” in the Russian client.
- The descriptions of the Snake, Crystal and Slave implant sets have been corrected in the Russian client.
- A grammatical error has been corrected in the market buy window in the Russian client.
- The market quickbar will now display all tabs correctly in the Russian client
- The assets list window has now been translated correctly in the Russian client.
- Multiple skill group names have been translated correctly in the Russian client.
- Several ship attribute have been translated correctly in the Russian client. The changes include “Drone Capacity,” “Capacitor,” “Max targeting Range” and “Warp Speed.”
- The skill queue option “Train after current queue” has been translated correctly in the German client.


**Miscellaneous**


- Player transfers to the Jovian system RU-97T will no longer cause players to become stuck. This will be welcome news for pilots participating in Alliance Tournament VII.
- Fixed problems with the Optional Client Update system


**POST-PATCH CHANGES**

Apocrypha 1.5.0-1 Server side change, released 21 August 2009


- This hotfix today was made to fix the new Caldari epic arc. The arc was disabled yesterday before we opened and was enabled today. All four arcs are now available.


Apocrypha 1.5.0-2 Server side change, released 24 August 2009


- The Minmatar Epic Arc “Playing All Their Cards” has been fixed. Players will now be able to complete the mission and accept the reward without worrying about how much space is available in their cargo hold.


Apocrypha 1.5.0-3 Server side change, released 25 August 2009


- Killmails are now correctly generated when all participants are Factional Warfare members.
- The base NPC sell price of the large rig blueprints was increased to be consistent with the small and medium rig blueprint prices
- The Medium Energy Burst Aerator I Blueprint is now correctly sold by various Amarr Science corps.
- The small and medium EW Drone range augmentor rigs were released accidentally. These have been removed and any rig or blueprint of this type was converted to a drone control range augmentor rig variant.
