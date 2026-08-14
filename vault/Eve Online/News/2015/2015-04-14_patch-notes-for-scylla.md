# Patch Notes For Scylla

- **Date**: 2015-04-14T10:01:53.000Z
- **Category**: patch-notes
- **Author**: CCP Falcon
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-scylla
- **Tags**: #patch-notes

## Overview
Patch notes for Scylla 1.5 For Release on Tuesday, April 14, 2015 FIXES: Localization: Fixed an issue which could cause the bilingual functionality popup window to become unresponsive. User Interface: Fixed an issue causing the fitting window to cause very low client FPS. &nbs

---

Patch notes for Scylla 1.5For Release on Tuesday, April 14, 2015


## **FIXES:**


**Localization:**


- Fixed an issue which could cause the bilingual functionality popup window to become unresponsive.


**User Interface:**


- Fixed an issue causing the fitting window to cause very low client FPS.


Patch notes for Scylla 1.4For Release on Wednesday, April 1, 2015


## **FEATURES & CHANGES :**


**Miscellaneous:**


- The "Load Charges" task in the Opportunity system has been temporarily disabled.


Patch notes for Scylla 1.3For Release on Tuesday, March 31, 2015


## **FEATURES & CHANGES :**


**User Interface**


- The Download on Demand resource loading indicator's autohide function has been turned off for now due to performance concerns. This means that the icon will persist in the bottom left corner of clients even if there is no loading ongoing.



## FIXES:



#### Gameplay:



- Opportunities: The 'Moving the Camera' opportunity has been fixed so that it no longer automatically completes upon first login.


**Localization:**


- An issue that caused the bilingual functionality popup to minimize to the Neoncom instead of getting closed has been fixed.
- The 'Do not show this again' check box in the bilingual functionality popup has been fixed.


**Modules:**


- The Cargo Scanner will now again receive results and deactivates correctly after using it on NPCs.


**Technical:**


- Download on Demand related FPS issues have been fixed.
- An issue that could cause frame rate drops during combat if the fitting window was open has been fixed.


**User Interface:**


- Inverted zoom is working in the old map system view now.
- Fixed issue causing Neocom menu to close inappropriately.
- Fixed issue causing two yellow stargates to sometimes show up in overview.
- Fixed an issue that could cause the Contracts window to fail to open.
- New map: Probing - Fixed results with low scan strength showing up black rather than red.
- New map: Probing - Fixed false positives sometimes not showing up.
- New map: Probing - Fixed signatures disappearing when resizing probe formation.
- New map: Fixed an issue causing some players' map to not load at all.
- New map: Improved probe formation resizing refresh rate.
- New map: Fixed beacons not showing up.
- New map: Probing - Fixed FPS issue when having many scan results.


Patch notes for Scylla 1.2For Release on Thursday, March 26, 2015


## FIXES:


**Technical:**


- Download-on-demand has been optimized, in particular the chance of stalls when looking at ships has been reduced.
- The chance of getting corrupt files into the resource cache has been reduced.


Patch notes for Scylla 1.1For Release on Wednesday, March 25, 2015


## FIXES:


**Missions & NPCs:**


- NPCs will again leave behind wrecks, even if there is no loot to be found within them.
- Drifter Battleship wrecks can be damaged.


Patch notes for Scylla 1.0For Release on Tuesday, March 24, 2015


## **FEATURES & CHANGES :**


**Gameplay:**


- Firing a bomb from a Bomb Launcher module will now trigger a 60 second Weapons timer.
- The default CSPA charge for newly created characters has been reduced from 2950 ISK to 0 ISK. For any existing characters that have their CSPA charge still at the default of 2950 ISK, the charge will also be changed to 0 ISK. Characters that have chosen to set their charge to any other value will be unaffected. All characters can still configure this setting as normal (via the Settings option in the Mail window).
- Fighters can no longer be assigned to other pilots, the ‘Delegate Control’ option has been removed from right click menus. (Updated on March 23, was originally: "Fighters can no longer be assigned to other pilots. The ‘Delegate Control’ option has been removed and replaced by ‘Assist’ and ‘Defend’, same as other drones.")
- The Opportunities New Player Experience has been updated. New opportunities have been added and existing opportunities have been updated. A new A/B testing framework will be rolled out as part of these changes. More information is available [here](//community.eveonline.com/news/dev-blogs/opportunities-abound-the-new-player-experience/).


The following opportunities have been added:


- Take a Look Around (camera)
- Navigating New Eden (routes, map, and autopilot)
- Market Forces (buying and selling on the market)
- We are not alone (chat)
- Fit for Purpose (Slots, rigs, and charges)
- Death of a Ship (losing a ship and how to acquire a new one)
- The following opportunities have been renamed:
- ‘Learning Skills’ is now ‘You Can Get Better!’
- ‘Use Station Services’ is now ‘Base Your Operations’


The following balance changes have been made to Strategic Cruiser defensive subsystems:

**Legion Defensive - Adaptive Augmenter**


- Signature Radius: 140 (-14)


**Legion Defensive - Augmented Plating**


- +7.5% Armor HP per level (previously +10%)
- Signature Radius: 154 (+7)


**Legion Defensive - Nanobot Injector**


- Armor HP: 3750 (+150)


**Legion Defensive - Warfare Processor**


- Signature Radius: 147 (+7)


**Loki Defensive - Adaptive Augmenter**


- Signature Radius: 125 (-5)


**Loki Defensive - Adaptive Shielding**


- Signature Radius: 130 (-13)


**Loki Defensive - Warfare Processor**


- Signature Radius: 143 (+13)


**Proteus Defensive - Adaptive Augmenter**


- Signature Radius: 160 (-16)


**Proteus Defensive - Augmented Plating**


- +7.5% Armor HP per level (previously +10%)
- Signature Radius: 176 (+8)


**Proteus Defensive - Nanobot Injector**


- Armor HP: 3650 (+150)


**Proteus Defensive - Warfare Processor**


- Signature Radius: 168 (+8)


**Tengu Defensive - Adaptive Shielding**


- Signature Radius: 150 (-15)


**Tengu Defensive - Supplemental Screening**


- +5% Shield HP and +3% Shield Recharge Speed per level (previously +10% Shield HP)
- Shield Capacity: 3550 (-200)
- Signature Radius: 165 (+7)


**Tengu Defensive - Warfare Processor**


- Signature Radius: 157 (+7)
- Optimal range of Bouncer sentry drones have been reduced by 14.3%. The same range has then been added to their falloff.
- Civilian Gatling Pulse Lasers and Civilian Gatling Autocannons have received slight buffs.
- The Ishtar has been slightly rebalanced. "10% bonus to Drone hit points and damage" becomes "10% bonus to Light, Medium, and Heavy Drone hit points and damage, 5% bonus to Sentry Drone hit points and damage".
- Rate of fire reduced by 7.5% for all Medium Rail Guns.
- Corp delivieries can now be sorted by quantity


**Graphics:**


- Updated many dungeon and worldobject assets to V3 shaders.
- Created a more stable bounding sphere algorithm that better supports animated ships.
- Adjusted the visual super nova effect of the 'Caroline Star'.


**Localization:**


- Added a popup window that appears when non-English clients are started, informing players of the bilingual functionality for important names in game. This window can be suppressed.
- All dungeon objects are now fully localized into German.


**Modules:**


- CONCORD has provided their initial analysis of the Lux Kontos.


**Missions & NPCs:**


- The [tragically deceased](//wiki.eveonline.com/en/wiki/Inferno_%28Chronicle%29) research agent Avagher Xarasier's position at Duvolle Labs has been replaced by the young and promising Rias Luisauir. Luisauir will be taking on all of Xarasier's previous responsibilities and any capsuleers who had previous dealings with Xarasier will find that their business can continue uninterrupted with Luisauir.


**Ships:**


- The new Victorieux Luxury Yacht has been released by the Intaki Syndicate, and will be awarded to all subscribed accounts on the server whose representatives win the [World's Collide PVP tournament](//community.eveonline.com/news/dev-blogs/fanfest-2015-worlds-collide/) at Fanfest.


**Technical:**

Download-on-Demand:  


- Small initial install.
- Resources are downloaded as the client needs them.
- Players can still opt to download the full set of resources.


**User Interface:**


- Added the ability to reverse the zoom direction of the scroll wheel and left+right mouse buttons. The setting can be found under Display & Graphics in the Esc menu.
- New Map: added support for probe scanning.
- New Map: added support for saved locations.
- New Map: added persisting camera position.
- New Map: added persisting search strings.
- New Map: added auto-collapse on search input.
- The look of the progress bar has been changed
- PI windows can now have their Storage columns resized
- Right-click menu now highlights previous selections when entering sub menus



## **FIXES :**


**Exploration:**


- A despawning issue with the Drone Horde combat site has been fixed.
- Extraneous objects within the Blood Raider Mainframe exploration site have been removed.
- A despawning issue with the Guristas Gas Processing combat site has been fixed.
- An issue with the Blood Hideaway combat site not despawning has been fixed.
- A despawning issue with the Haunted Yard combat site has been fixed.
- The single jump mass limit on wormholes connecting Thera and Low Security space has been increased to 1,000,000,000kg
- The site Silent Battleground had it's distribution adjusted.


**Gameplay:**


- Opportunities: fixed the "Done Already!" message appearing at inappropriate times.


**Graphics & Audio:**


- Restored textures to dungeon object ship wreckage.
- Corrected an issue making shadows from a pilot's cloaked ship visible to that pilot.
- Modified inactive client muting settings to include station interior effects.
- Added hangar and CQ view sound effects for T3 destroyer stance switch animations.
- Naglfar wrecks in various sites have had their textured fixed.
- Closing the ESC menu in fullscreen mode will no longer display a strange unexpected graphical effect


**Localization:**


- Various bug fixed and resolved terminology issues for all languages.


**Miscellaneous:**


- Various English grammatical errors in warning messages have been fixed.
- A text issue with the female 'Avenue' shirts has been fixed.
- A typo in the description of the Territorial Claim Unit has been fixed.
- A grammatical error in the description of the Stolen Passkey item has been fixed.
- A text error in description of the "Guillome Renard’s Sleeper Loot Stash" item has been fixed.
- A text error in the description of the Tempest Fleet Issue battleship has been fixed.
- A text error with the X-Instinct series of boosters has been fixed.
- Typo in Industry career path description has been fixed.
- Line breaks and text has been fixed in accepting Courier Contracts.


**Missions & NPCs:**


- Non-law enforcement NPCs will no longer be able to maintain target lock on capsuleers inside force fields.
- A typo with the Centus Black Op Assassins has been fixed.
- An issue with missing objectives has been fixed in the combat mission: Mordu's Folly 1 of 2.
- A text issue in the description of the combat mission Undue Attention (3 of 3) has been fixed.
- A text error in the description of the Anomic Team combat mission has been fixed.
- A text issue in the mission Pirate Aggression mission objectives has been fixed.
- An accessibility issue in the mission: The Big Sting has been fixed.
- A text error in the Advanced Operations Technology certificate has been fixed.
- A missing object from the Advanced Military tutorial mission 'Don't Look Back' site has been reintroduced.
- Inconsistent mission locations for the Minmatar Epic Arc have been fixed in the mission briefings.


**PvE:**


- The rewards for completing the final Trouble in Paradise combat site have been increased.
- An information pop up message has been added to the Average Frontier Deposit mining site.
- All enemy ships now have to be destroyed to activate the acceleration gates in the Guristas Hallucinogen Supply Waypoint combat site.
- The Serpentis Narcotics Storage Facility container no longer drops the Gas Cloud Harvester I module.
- Text issues with the Serpentis Port and Blood Port combat sites have been fixed.


**User Interface:**


- Fixed an issue with the fitting window stance buttons becoming out-of-date when switching directly between two T3 Destroyers in space whilst keeping the fitting window open.
- Fixed an issue where UI scaling could cause the fitting window to break.
- Fixed an issue where tool tips would display while dragging windows.
- Opportunities: the opportunities map window can no longer be stacked with other windows, as that was causing various issues.
- New Map: fixed landmarks not being right clickable.
- New Map: fixed panning.
- New Map: fixed location names not being drag+droppable from dropdown lists.
- New Map: fixed selected region not being properly detailed directly after opening map when using the 'Group By Region' filter.
- The traits window for the Rattlesnake Victory Edition will now correctly display the ship characteristics icons.
- Fixed the 'Search' button overlapping text fields in the 'Search for recipients' window.
- Fixed an error which could cause duplicate Neocoms to appear.
- Using saved fittings for tactical destroyers is no longer causing errors about missing items. It is also no longer possible to save fittings for tactical destroyers with no items fitted.
- Tactical destroyers no longer lose their hp stats from fleet watch lists at changing mode.
- Chat tabs no longer remove blinking on mouse over
- Industry window performance has been improved when changing job types with lots of blueprints
- Moving Neocom buttons around too fast will no longer screw up the button order
- Wallet blink for corp wallet has been turned off for those that no longer have access to it
- Mail window list and text sections are now correctly aligned
