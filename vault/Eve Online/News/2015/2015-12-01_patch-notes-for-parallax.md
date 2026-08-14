# Patch Notes For Parallax

- **Date**: 2015-12-01T10:10:28.000Z
- **Category**: patch-notes
- **Author**: CCP Falcon
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-parallax
- **Tags**: #patch-notes

## Overview
Patch Notes for Parallax 1.10 Released on Tuesday, December 1st, 2015 FIXES: Miscellaneous: The backend system received some improvements and bug fixes.     Patch Notes for Parallax 1.9.1 Released on Thursday, November 26th, 2015 FIXES: Gameplay: The skill trai

---

Patch Notes for Parallax 1.10Released on Tuesday, December 1st, 2015


## FIXES:


**Miscellaneous:**


- The backend system received some improvements and bug fixes.


Patch Notes for Parallax 1.9.1Released on Thursday, November 26th, 2015


## FIXES:


**Gameplay:**


- The skill training bonus from Cerebral Accelerator is now working again correctly directly after consuming the booster.


Patch Notes for Parallax 1.9Released on Tuesday, November 24th, 2015


## FIXES:


**Gameplay:**


- Fixed an issue with Corporation applications where DUST characters would sometimes be unable to join a corp if they had pending applications to multiple Corporations
- The code for validating skill queues has been improved and is now more robust.
- Self destructing through the clone bay window is again no longer possible while being in a ship (which caused characters to get stuck).


Patch Notes for Parallax 1.8Released on Thursday, November 19th, 2015


## FIXES:


**Gameplay:**


- Reimbursed lost skill points for the skill training issue from November 12th: Unallocated skill points were added to all characters, which lost skill training time due to skill training resets between the downtime on November 12th and the downtime on November 13th.


Patch Notes for Parallax 1.7Released on Monday, November 16th, 2015


## FIXES:


**Gameplay:**


- The missile velocity bonus for the sharpshooter mode on the Jackdaw is now consistently applied.


Patch Notes for Parallax 1.6Released on Thursday November 12th, 2015


## FIXES:


**Gameplay:**


- The code for training of skills has been improved to reduce problems with broken skill queues.
- New Eden has been made a better place by fixing a potential exploit.
- The missing bonus from Imperial Navy Warfare Mindlinks to Electronic Superiority warfare links has been added again.


** Technical:**


- Fixed a problem, which has probably caused broken ships after jumping in rare cases.


**User Interface:**


- A proper message is displayed again when trying to inject the same skill twice.


Patch Notes for Parallax 1.5.1Released on Wednesday November 11th, 2015


## THIRD PARTY DEVELOPERS:



#### XML API:



- The API no longer makes any attempt to fake the quantity of materials being stolen by siphon units.
- The flat and the hierarchical variants of the AssetList endpoints are no longer cached individually.
- Fixed a server error in the char/MailBodies and char/NotificationTexts endpoints when the mail body or the notification text contained a closing CDATA token.
- Fixed a server error in the KillMail and KillLog endpoints when any of the kill reports that were to be presented had individuals that inflicted negative damage to the victim.
- Fixed a server error in the eve/CharacterID and eve/OwnerID endpoints when a given character name exceeds 100 characters in length. A 122 error is now thrown in these cases.
- Fixed a server error in the eve/CharacterID and eve/OwnerID endpoints when the list of character names contained duplicates. Duplicates are now ignored.
- Fixed a server error in the eve/CharacterID and eve/OwnerID endpoints when the list of character names is an empty string. A 122 error is now thrown in that case.
- Fixed a race condition in the eve/CharacterID and eve/OwnerID endpoints with regards to caching that caused a server error.
- Fixed a server error in the planetary interaction endpoints when the planetID parameter was missing or invalid. A new 136 error is now thrown in these cases.
- Fixed a server error in the corp/AssetList endpoint when two or more siphon units were stealing from the same structure.


Patch Notes for Parallax 1.5Released on Tuesday November 10th, 2015


## FEATURES & CHANGES :



#### Missions & NPCs:



- As Holy Amarr mourn the loss of their Empress and the search begins for a replacement heir, The Drifter armada have returned and the time has come to step up and defend the Throne Worlds from this hostile attack.



## FIXES :



#### Gameplay:



- The shield amount of Control Towers and Customs Offices is now starting at the correct value after a reinforcement.
- Fleet bonuses, which affect the cycle time of modules (like mining lasers or shield boosters), are now applied more consistently after changing positions in the fleet. (Comment: Other problems with fleet bonuses are still being investigated.)



#### PvE:



- Sites (Cosmic Anomaly/Signatures) will again continue to process all triggers when it has been marked as completed.


Patch Notes for Parallax 1.4Released on Monday November 9th, 2015


## FIXES:



#### User Interface:



- The fitting screen is now populating correctly after boarding a ship from a Ship Maintenance Array. This should also fix other related problems like missing right-click menus for modules (when they wouldn't show in the fitting screen).


Patch notes for Parallax 1.3Released on Thursday November 5th, 2015


## FIXES:



#### User Interface:



- Deleting custom filters now works as intended and does not delete the last filter in the list
- Ignoring signatures will now correctly cause all other unignored signatures to appear in the solar system map
- Cosmic signatures will all continue to display in the Solar System map if all were displaying and one is right clicked
- Signature list will no longer snap to the top of the list after each scan/refresh
- HUD is now visible on top of the Solar System map when in fullscreen mode
- Bindable Zoom hotkeys now function correctly in the Solar System map
- Probe Scanner filter hotkeys will now only apply if the window is active or if the mouse is held over it. As a result, Save Location will now work correctly when numbers 1-5 are used in the name of a location
- Directional Scanner visualisation is now toggleable via the Solar System Map
- Probe Scanner window now obeys transparency and pinning settings


Patch notes for Parallax 1.2Release on Thursday, November 5th, 2015


## FIXES:



#### Technical:



- Fixed a memory leak on the server.
- The code for boarding of ships (for example at starbases) has been improved. This is also addressing an issue with missing modules in the fitting windows.



#### User Interface:



- Orbital strikes now generate kill reports again
- The window for remapping attributes is now showing correct values while using a cerebral accelerator.
- The show info window for R&D agents is now showing again the required skills correctly.
- Ship attributes (especially the shield value) should now stay correct after fleet jumps into (previously) time dilated system.
- An issue with displaying the notification when starting a self destruct on a structure has been fixed.


Patch notes for Parallax 1.1Release on Wednesday November 4th, 2015


## FEATURES & CHANGES :


**Market:**


- The Pilot's Services and Pilot's License Extensions (PLEX) market groups have had their icons updated to the new PLEX icon.


** Ships:**


- The Viator is now once again receiving the benefits of its Gallente Industrial skill bonuses.



## FIXES:


**Technical:**


- Fixed an issue where activating a Multiple Pilot Training Certificate would require you to log off and on again before you could start training skills with the new training queue.
- Freshly trained skills are now properly effecting your ships and modules, even if they completed while the character was offline.


**User Interface:**


- Fixed an issue where the unreleased Endurance Expedition Frigate was visible in the ISIS window.
- Reduced client lag when opening the skill queue window.
- Fixed a bug which caused the skill queue window to fail to open.
- Probe Scanner window background now obeys transparency and pinning settings.
- Fixed an issue where the new map would not load properly if you have bookmarks created in the system you are trying to open the map in.


Patch notes for Parallax 1.0Release on Tuesday November 3rd, 2015


## FEATURES & CHANGES :


**Audio:**


- Added an option in the audio menu to allow players to opt out of the dynamic music system and play only the original 2003 EVE soundtrack.
- Published a new theme song for Parallax.


**Gameplay:**


- Jump Fatigue is now capped at a maximum of 5 days, while reactivation is capped at 12 hours. Anyone who has either of these timers at a higher level than this will find their timers have been reduced to these new limit


**Graphics:**


- The graphics settings menu now offers a 'Camera Bobbing' option, this will toggle whether or not the camera will perform a gentle animation when left idle.


**Miscellaneous:**


- The server is now counting PVP kills for each ship item, in preparation for the forthcoming 'Kill marks' feature. The marks won't show up on ships yet, but once they do all these kills will give you a head-start. The clock is ticking, and as of now, we are keeping score! [See this dev-blog for more details](//community.eveonline.com/news/dev-blogs/sovereignty-jump-fatigue-reductions-and-more-in-parallax-on-november-3/).
- The wing commander of a fleet receives now fleet bonuses from the fleet booster.
- Fleet bonuses from the skills Leadership, Skirmish Warfare, and Information Warfare are now stacking penalized together with bonuses from other sources like modules. **Attention:** This change only impacts the targeting speed bonus from the Leadership **skill**, the agility bonus from the Skirmish Warfare **skill**, and targeting range bonus from the Information Warfare **skill**. The bonuses provided by the warfare link **modules** have not changed.


**Ships:**


- Any item that is scoopable can now also be scooped to a ships fleet hangar using the right click menu.
- A character with a criminal flag in a high-sec system is no longer able to board/switch ships whilst in space.


**SKINs:**


- Added new Raata Sunset SKINs for most T1 and T2 Amarr ships. Tech 1 SKINs will available immediately, while Tech 2 SKINs will be available the following week. The full list of SKINs are:
- Crucifier Raata Sunset SKIN (Permanent)
- Executioner Raata Sunset SKIN (Permanent)
- Inquisitor Raata Sunset SKIN (Permanent)
- Magnate Raata Sunset SKIN (Permanent)
- Punisher Raata Sunset SKIN (Permanent)
- Tormentor Raata Sunset SKIN (Permanent)
- Retribution Raata Sunset SKIN (Permanent)
- Vengeance Raata Sunset SKIN (Permanent)
- Anathema Raata Sunset SKIN (Permanent)
- Purifier Raata Sunset SKIN (Permanent)
- Sentinel Raata Sunset SKIN (Permanent)
- Crusader Raata Sunset SKIN (Permanent)
- Malediction Raata Sunset SKIN (Permanent)
- Coercer Raata Sunset SKIN (Permanent)
- Dragoon Raata Sunset SKIN (Permanent)
- Heretic Raata Sunset SKIN (Permanent)
- Arbitrator Raata Sunset SKIN (Permanent)
- Augoror Raata Sunset SKIN (Permanent)
- Maller Raata Sunset SKIN (Permanent)
- Omen Raata Sunset SKIN (Permanent)
- Sacrilege Raata Sunset SKIN (Permanent)
- Zealot Raata Sunset SKIN (Permanent)
- Devoter Raata Sunset SKIN (Permanent)
- Guardian Raata Sunset SKIN (Permanent)
- Curse Raata Sunset SKIN (Permanent)
- Pilgrim Raata Sunset SKIN (Permanent)
- Harbinger Raata Sunset SKIN (Permanent)
- Oracle Raata Sunset SKIN (Permanent)
- Prophecy Raata Sunset SKIN (Permanent)
- Absolution Raata Sunset SKIN (Permanent)
- Damnation Raata Sunset SKIN (Permanent)
- Abaddon Raata Sunset SKIN (Permanent)
- Apocalypse Raata Sunset SKIN (Permanent)
- Armageddon Raata Sunset SKIN (Permanent)
- Redeemer Raata Sunset SKIN (Permanent)
- Paladin Raata Sunset SKIN (Permanent)
- Revelation Raata Sunset SKIN (Permanent)
- Archon Raata Sunset SKIN (Permanent)
- Aeon Raata Sunset SKIN (Permanent)
- Avatar Raata Sunset SKIN (Permanent)
- Bestower Raata Sunset SKIN (Permanent)
- Sigil Raata Sunset SKIN (Permanent)
- Prorator Raata Sunset SKIN (Permanent)
- Impel Raata Sunset SKIN (Permanent)
- Providence Raata Sunset SKIN (Permanent)
- Ark Raata Sunset SKIN (Permanent)


**Structures & Deployables:**


- Outposts, Infrastructure Hubs, Territorial Claim Units, Station Services (if not disabled), and Command Nodes now have a new behavior related to the Entosis mechanic: Defensive Regeneration. These items will now slowly automatically capture themselves in the defender's favor if there are no active Entosis links targeted on them. The rate of regeneration is unaffected by the Activity Defense Modifier or any other variable, and is fixed for each different type of structure. The regeneration time for each type of structure is shown in the type's window.
- Strategic Infrastructure Upgrades that are installed in an Infrastructure Hub may now be manually offlined by a character with Director roles in the owning corp. When an upgrade module is offlined, any dependent starbase structures will immediately be offlined, and cannot be re-onlined until the necessary IHub upgrade itself is put back online again. Any upgrade that is offline will not contribute towards the IHub's weekly bill. When a character installs a new upgrade or onlines an existing upgrade, he must pay an upfront fee equal to the weekly bill for that upgrade. Installing/Onlining upgrades requires the Station Manager role.
- Additionally, the weekly bill based on the current upgrade status is now visible in the IHub Manager window. This display will update in real time as upgrades are installed/onlined/offlined. See [this dev blog](//community.eveonline.com/news/dev-blogs/sovereignty-jump-fatigue-reductions-and-more-in-parallax-on-november-3/) for more details.
- TCUs and IHubs can now be self destructed by directors in the owner corporation. The self destruct countdown will take 20 minutes to complete. Directors and CEOs in the owner corporation are able to cancel the countdown.


**Technical: **


- Brain in a Box and Dogma Rewrite: Performance optimization (mostly for fleet jumps and for Jita) and code refactoring of core systems of the EVE codebase. This includes a full code rewrite of skill training, fleet bonuses and the heat system - but without any functional changes. This change enables possibilities for further performance improvements and game design changes. More details about this will be available soon in a Dev Blog.


**User Interface:**


- The Route Info Panel will now more accurately represent the distance to waypoints when in a wormhole system. Adding a single waypoint will display as "Unknown Jumps", whereas multiple waypoints will display as "X+ jumps", giving the distance between the waypoints as X.
- Changed the icon for the Pilot's License Extension item.
- Added a refresh button to the Sovereignty tab of the Corporation window, to allow the data to be refreshed without closing the window.
- Added 'Jump' option to right click menu when clicking a saved location that is a stargate, in the People & Places window.
- Clicking any notification regarding corp applications will now open the recruitment tab of the corporation window.
- Crystal Damage now shows as % in tooltips.
- A success message is now displayed after sending a bug report, which contains the ID of the sent bug report.


**New Probe and Directional Scanning Interfaces (Added as Beta feature default ON):**


- Probe Scanner window
- Hotkey for Analyze, mappable via the Shortcuts tab in the System menu (ESC), also possible to use RETURN key while the window has focus
- Moved Destroy Probes button away from Recall Probes button
- Moved Recall Probes button away from Analyze button
- Added hotkeys to Filter options. 1-5 keys now allow you to show/hide types on the fly while window has focus
- Probe section of window has been made collapsible and resizable
- Resizing scan range can be modified by ALT-MOUSEWHEEL
- Spread probes formation be modified by CTRL-MOUSEWHEEL
- Uses new standalone solarsystem view, accessible through the window or command with F9 as default mapping
- New shortcut command to In/Decrease scan range. No default mapping.
- Fixed issue where probes moved far out of scope when moving plane was close to being parallel to the view angle of the camera
- Overall UI cleanup
- Directional Scanner
- Hotkey to Scan, mappable via the Shortcuts tab in the System menu (ESC)
- Uses new standalone solarsystem view to visualize the scan.
- Directional Scan option in radial menu in system view to automatically align the scan angle
- Option to align the solarsystem view to the space camera
- Overall UI cleanup



## FIXES :


**Gameplay:**


- Fixed an issue where Supercapital Ship Assembly Arrays wouldn't go offline when their system's Infrastructure hub was destroyed.
- Drones may now agress freight containers if directed to do so, following all the normal legal restrictions and capsuleer safety settings.


**Corps and Alliances:**


- When an application to join a corporation is rejected, the rejection text is now visible to both parties in the Recruitment section of the Corporation window.
- Fixed an issue where an Outpost that is in Freeport mode would sometimes prevent a corporation from renting an office, due to running incorrect standings checks. Whilst an Outpost is in Freeport mode, all corporations will now be able to rent an office (subject to capacity) regardless of standings.


**Graphics:**


- Corrected a rendering issue in the ship fitting window
- Fixed shading inheritance on Large POS batteries.
- Improved the display of the turrets on the Mobile Tractor Unit.
- Adjusted the placement of a sprite on Claw hull


**PvE:**


- Multiple grammatical errors in mission texts have been fixed.


**User Interface:**


- Kill report timestamps are now recorded with precision up to the second instead of to the minute.
- You now get a clearer message on what happens when you're changing default sovereignty vulnerability time, when there's already a pending change.
- The applications tabs in the corporation window now have a hint saying you have no ads when that applies.
- Corporate divisions with long names will now be handled gracefully by the member details window.
- Automatic Pay Settings for corporate bills will now display alphabetically for all pilots.
- The amount of shares shown in the Show Info window of a corporation now includes the initial shares.
- You no longer see the menu option to configure POCOs when you don't have the roles to do so.
- Fixed an issue where show info windows for medals would be blank.
- Fixed an issue the would cause "Lock Blueprints" vote to appear as empty.
- Warp Scrambler descriptions have been updated to include their effect on Micro Jump Drives.
- Description of Medium Auxiliary Nano Pump II has been fixed.
- Fixed typo in description of Covert Ops skill.
- When an application to join a corporation is rejected, the rejection text is now visible to both parties in the Recruitment section of the Corporation UI
- Fixed typo in description of "Minmatar Graduation Certificate (signed)".
- Fixed typo in fighter certificate description.
- Fixed formatting issue in description of multiple pirate implants.
- Fixed typo in 'Infrastructure hub reinforced' notification.
- Changed name from "Thermic" to "Thermal" in all names and descriptions for consistency with damage name.
- The descriptions of all adaptive nano platings have been updated to more accurately indicate their function.
- Fixed missing icon in 'Clone Contract Revoked' notification.
- Fixed an issue resulting in aura opportunities window being blank.
- Fixed tooltips in old and new map when using the 'Recent Sovereignty Changes' filter.
- Fixed an issue where having a route selected when in wormhole space would cause the World Map Control Panel to not appear in the old map.
- Improved messaging when aborting ship self-destruct so that it is less ambiguous.
- Fixed a grammatical error in the message received when attempting to overload modules without the Thermodynamics skill.
- Fixed sovereignty info panels sometimes not updating correctly when structures change states.
- Fixed several minor grammatical errors in the tooltips for certificates.
- Corrected capitalization of 'To' column header in the Contracts window.
- The eye icon next to saved location folders will now always persist between logins.
- Fixed an issue that would break the contract window when creating a courier contract containing saved location vouchers.
- Fixed an issue where the sovereignty info panel was not updating correctly when structures command nodes begin to decloak.
- The tournament ship banning window now only lists ships that are allowed by tournament rules



## THIRD PARTY DEVELOPERS:


**XML API:**


- Killmail coordinates are exposed via the 'x', 'y', and 'z' attributes within the 'victim' element. Their values default to 0.0 for killmails that occurred prior to Parallax.
- Cartesian space coordinates of the victim's vessel in killmails are now recorded and exposed via the XML API and CREST.


**CREST API:**


- Killmail coordinates are exposed via the keys 'x', 'y', and 'z' via 'position' in the 'victim' dictionary. The 'position' key is not present for killmails that occurred prior to Parallax.
- The fitting resource is now exposed and available for GET, POST, and DELETE requests. You will need to request the charactersFittingsRead and/or charactersFittingsWrite scopes to use it.
