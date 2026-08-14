# Patch notes for May 2016 release

- **Date**: 2016-06-21T10:11:26.000Z
- **Category**: patch-notes
- **Author**: CCP Phantom
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-may-2016-release
- **Tags**: #patch-notes

## Overview
Patch notes for May 2016  Release 1.6 Published on Tuesday, June 21st, 2016 Features & Changes User Interface: Clicking on a web link in the client now opens your desktops default browser. This includes a warning dialog that warns you about leaving the EVE Online client. Defect F

---

Patch notes for May 2016  Release 1.6Published on Tuesday, June 21st, 2016


## Features & Changes



#### User Interface:



- Clicking on a web link in the client now opens your desktops default browser. This includes a warning dialog that warns you about leaving the EVE Online client.



## Defect Fixes



#### Gameplay:



- New Eden has been made a better place by fixing a potential exploit.



## Third Party Developers



#### CREST API:



- Fixed a caching issue that caused the /corporations//structures/ resource to begin returning errors an hour after it was first accessed each day by each user.
- Added a /corporations// resource that contains a link to the corporation structures resource, so it can be discovered.
- Changed the /corporation//structures/ resource to /corporations//structures/ - More info is available in this [dev blog](//developers.eveonline.com/blog/article/improvements-to-corporation-structures-crest-endpoint).
- Fixed an issue with killmails that included someone in factional warfare.
- Fixed an issue with the navigation, show contract, and show market details CREST resources.



---


Patch notes for May 2016  Release 1.5Published on Tuesday, June 14th, 2016


## Third Party Developers



#### CREST API:


Please note that these changes are backwards incompatible changes!

See the following devblog for full details: [//developers.eveonline.com/blog/article/crest-renovations-2016-06](//developers.eveonline.com/blog/article/crest-renovations-2016-06)


- Market orders in the all orders resource are now sorted by order ID
- /types/[typeid:integertype](typeid:integertype)/ is now /inventory/types/</typeid:integertype>
- /types/ is now /inventory/types/
- Removed "motd" from the root API
- Added "id" to the market group "parentGroup" attribute
- The root API is now just version 5; all previous versions have been deleted
- "serviceStatus" in the root API is now just a string value and not a dictionary of "server", "eve", and "dust" values
- "userCounts" is now "userCount" and a single integer value instead of a dictionary of "eve" and "dust"
- Removed every CREST resource that only dealt with DUST and not used by third-party developers for EVE
- The character resource (/characters/[characterid:integertype](characterid:integertype)/) v3 no longer exists and a new v4 has been added</characterid:integertype>
- The "navigation" resource (/characters/[characterid:characteridtype](characterid:characteridtype)/navigation/waypoints/) for setting waypoints has moved to /characters/[characterid:characteridtype](characterid:characteridtype)/ui/autopilot/waypoints/</characterid:characteridtype></characterid:characteridtype>
- The waypoints link is now found under character -> ui -> waypoints along with showMarketDetails and showContract
- Links to characters that used to include the capsuleer link no longer do as that resource has been removed
- Fixed an issue with some types throwing an internal server error due to graphic IDs
- The market history resource has changed from /market/[regionid:integertype](regionid:integertype)/types/[typeid:integertype](typeid:integertype)/history/ to /market/[regionid:integertype](regionid:integertype)/history/ and now takes a "type" parameter exactly the same way the market buy or sell order resources do</regionid:integertype></typeid:integertype></regionid:integertype>
- Regions now link to the market history resource



---


Patch notes for May 2016  Release 1.4Published on Wednesday, June 8th, 2016


## Defect Fixes:



#### Graphics:



- Fixed edge-cases of wormhole distortions being coloured red.



---


Patch notes for May 2016  Release 1.3Published on Tuesday, June 7th, 2016


## Defect Fixes:



#### Miscellaneous:



- A few small improvements to make New Eden a better place for everyone.



---


Patch notes for May 2016  Release 1.2Published on Friday, June 3rd, 2016


## Defect Fixes:



#### User Interface:



- Fixed an issue where the camera would break when jumping through a wormhole with tactical camera enabled.



---


Patch notes for May 2016  Release 1.1Published on Thursday, June 2nd, 2016


## Defect Fixes:



#### Gameplay:



- The bonuses from some Citadel reprocessing rigs will no longer require a character to have assumed control of the citadel since the last downtime in order to work correctly.
- Corrected an issue that was causing the industry window to break if a tactical ammo blueprint was in an active research job.



#### Graphics:



- Icons for wormholes now travel faster and as such will no longer be colour-shifted to the red end of the spectrum.



#### User Interface:



- The Sensor Overlay should now always display locations (such as bookmarks, anomalies) after changing between different view states.
- Fixed an issue with the market not showing data in space after using it in a Citadel and filtering to only show orders in the Citadel.



---


Patch notes for May 2016  ReleasePublished on Tuesday, May 31st, 2016


## Features & Changes



#### Exploration:



- ‘Ligature’ Integrated Analyzer blueprint can now be looted in Data site Info Shard and Com Tower containers.
- ‘Zeugma’ Integrated Analyzer blueprint can now be looted in Data site Mainframe and Databank containers.
- Construction work has now been completed on the Upwell Consortiums five Astrahus citadels.



#### Graphics:



- Updated Nebulae backdrops to use the YUV color space to remove compression artifacts.



#### Market:



- ‘Ligature’ Integrated Analyzer and its blueprint have been added to the Market.
- ‘Zeugma’ Integrated Analyzer and its blueprint have been added to the Market.



#### Modules:



- Two new 'multi-analyzer' modules have been added which can open both Relic and Data site containers.Their blueprints can be found in Data sites and their stats are as follows:
- ‘Ligature’ Integrated Analyzer exploration module - Volume: 5 m3
  - Activation Cost: 20 GJ
  - Structure Hitpoints: 40
  - Optimal Range: 5000 m
  - Activation Time / Duration: 10 seconds
  - Virus Coherence: 20
  - Virus Strength: 20
  - Virus Utility Element Slots: 1
  - Access Difficulty Bonus: 5%
  - Tech Level: 1
  - CPU usage: 25
- ‘Zeugma’ Integrated Analyzer exploration module - Volume: 5 m3
  - Activation Cost: 20 GJ
  - Structure Hitpoints: 40
  - Optimal Range: 6000 m
  - Activation Time / Duration: 10 seconds
  - Virus Coherence: 40
  - Virus Strength: 30
  - Virus Utility Element Slots: 1
  - Access Difficulty Bonus: 7%
  - Tech Level: 2
  - CPU usage: 30


**Miscellaneous:**


- DUST514 items will no longer appear in the market.


**Skills:**


- Skill points trained in the racial Force Auxilliary skills have been reimbursed. Further details are available [here](//forums.eveonline.com/default.aspx?g=posts&t=481876).


**User Interface:**


- Camera - Right-click pan has been introduced
  - The functionality to change the field-of-view zoom with CTRL+mouse wheel has been removed
  - The 'old' camera has been disabled
- Moved the following window commands from 'General' to 'Window' in shortcuts section of ESC menu: - Close Active Window
  - Close All Windows
  - Minimize Active Window
  - Minimize/Maximize All Windows
- Renamed 'Minimize All Windows' shortcut to 'Minimize/Maximize All Windows' and now it also maximizes all minimized windows.
- Allowing combat shortcuts to work on d-scan results.



## Defect Fixes:



#### **Gameplay:**



- Ships with very little hull HP remaining will no longer gain small amounts of hull HP when jumping through gates.
- Ejecting from a ship with very little hull HP remaining may once again cause that ship to explode instead of causing the ship to gain small amounts of hull HP.
- The Standup Target painter, Sensor Dampener and Weapon Disruptor modules no longer appear as if they can use scripts in the fitting UI.
- Changed Gnosis Blueprint Volume to 0.01.
- It is no longer possible to load T2 ammunition into guns without having trained the appropriate skill.
- Empty T3 cruisers in space can now be probed down correctly.
- Fighters are now affected by Micro Jump Field Generators.
- It is no longer possible to disable auto-repeat on entosis links - as it needs to run for more than one cycle to have any effect.
- Ships can no longer use "Safe Logoff" whilst they have fighters deployed in space.
- Wormhole effects are now applied correctly when undocking from a Citadel.
- Fixed issue with Starbase Energy Neutralizing Batteries ignoring Energy Warfare Resistance.
- Energy Neutralizers for sub-capitals are no longer penalized by the signature radius of the target.
- It is no longer possible to give any commands to fighters (except Recall) while the commanding ship is in a forcefield.
- Fixed several issues with tethering.



#### **Graphics:**



- Corrected an issue with the 3d preview of ship SKINs.
- Reignited the engines of the Gallente Supercarrier Nyx.
- Retailored the display of Physically Simulated Cloth and Hair on in station avatars.



#### **PvE:**



- To aid finding the Starbase Ion Field Projection Batteries in Patriotic Measures (5 of 5), we have removed some nebula decorations.
- Sansha Watch NPC spawn issues have been resolved.



#### **User Interface:**



- Fixed an issue where combat shortcuts would not work on d-scan brackets.
- Fixed an issue where after jumping a gate in a tactical destroyer the modules would refresh and slide into view.
- Removed reference and link to EVElopedia from Loyalty Points Voucher info window.
- It is again possible to right-click outpost entries in the corporation window under "Home" - "Details".
- The attribute tab for Warfare Links has no longer a separate entry for Titans, but groups them together with the other allowed ship classes.
- The inventory index tree is now updating correctly when moving containers between corporation hangar divisions.
- The drone window no longer displays very damaged drones with a too long red bar for the armor damage.
- Camera: - Fixed an issue where the tracking camera could be used when jumping through stargates which would result in the camera breaking.
  - Fixed an issue where the safe log off dialog would not respect the 'Offset Interface With Camera' option.
  - Fixed an issue where 'Look At' with the tactical camera could zoom in too close on an object.
  - Fixed an issue where using 'Look At' twice on the same object in tactical camera would not work properly.
  - Fixed an issue where zooming out with the free tactical camera as far as possible would move the camera unexpectedly.
  - Fixed an issue where the attached camera in tactical mode would move with every little ship movement for example weaving with manual controls.
  - Fixed an issue where the camera zoom level would not be correct during the cloaking phase after jumping a stargate.
- Wallet: - Automatic pay settings display correctly and can be configured for corporations that are in alliances.
- Fighters: - Left-clicking the ship while having both the ship and fighters selected will now unselect the fighters to improve consistency.
- Citadels: - It is now possible to open the Ammo Hold of a Citadel while controlling a Citadel through the icon in the fitting screen.
  - The deliveries hangar in Citadels can now be opened in its own window.
  - The context menu for market entries in Citadels does now include the options for the location / solar system.
  - Undocking from a Citadel will now display appropriate warnings (Crimewatch, Contraband, ...) and will close appropriate windows (Clone window, reprocessing window).
- Multibuy: - Improved the notification for failing to add items, which cannot be traded on the market, to the Multibuy window.
  - When an item in the Multibuy window is no longer available at the shown price, the item is being re-added to the Multibuy window more reliably after failing to be bought.
- Fittings related: - The icon for drone bay / fighter bay in the fitting screen is now updating correctly when switching between ships with drones and carriers with open fitting screen.
  - Fixed a problem with importing ship fittings from clipboard including a Small Compact Pb-Acid Cap Battery.
  - Importing a fitting from clipboard will now allow including ice products like Strontium Clathrates.
  - The fitting management tool will no longer unfit subsystems from T3 cruisers, without being able to replace them with new subsystems. This was leading to missing subsystems and broken ships.
  - Fixed an issue where the ship model could move in the fitting window when warping around.
- Descriptions: - Fixed improper usage of CamelCase in the description of the High Speed Maneuvering skill.
  - Corrected excess double spacing in many ship descriptions.
  - Corrected description of the Omnidirectional Tracking Enhancer II.
  - Fixed the description of the skills Sensor Linking and Long Distance Jamming.
