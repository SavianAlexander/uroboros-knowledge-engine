# Patchnotes for Apocrypha 1.0.2

- **Date**: 2009-03-26T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patchnotes-for-apocrypha-1.0.2-1
- **Tags**: #patch-notes

## Overview
Patch Notes for Apocrypha Fixes, Changes and Improvements Critical Fixed a crash that was being caused when new icons were generated in systems with a secondary sun (i.e. some wormhole systems). Ships Updated the capital ship collision mechanic to lessen bumping issues currently b

---

## Patch Notes for Apocrypha



## Fixes, Changes and Improvements



### Critical



- Fixed a crash that was being caused when new icons were generated in systems with a secondary sun (i.e. some wormhole systems).



### Ships



- Updated the capital ship collision mechanic to lessen bumping issues currently being experienced by some players.
- Fixed a typo in the description of the Loki.
- Tech 3 subsystem bonuses will no longer have a stacking penalty. This will be fixed in a future patch
- Tech 3 ships with very low hit points will no longer show show negative hit points when viewed in the repair station panel.



### Modules



- Updated the shaders being used for warp disruption bubbles.
- Slowed down the rate of fire on Sisters Probe launchers to 1.5s. It was potentially causing server-side issues due to its speed.
- Combat and Deep Space probes now have new icons to aid in differentiating between them. Additionally, their descriptions have been updated to better indicate what they are for.
- Fixed a typo in the name of the "Emergent Neurovisual Interface Blueprint." It was previously listed as "Emergent Neuroptical Interface Blueprint."
- Tech 3 subsystem volumes have been updated to 40m3.
- Warp disrupt probes now display the correct launcher group in the Show Info window.
- Deep Space Scanner Probe I and its variations have had their strength reduced.
- Modified the inertial stabilizer attributes to show the correct multiplier value. It was showing a multiplier of -20% instead of 0.8.



### Rigs



- Fixed an exception being thrown when looking at rigs while in a ship with no rig slots.



### Weapons & Ammunition



- Going through a jump bridge or using a cynosural field will no longer cause ammunition that is being reloaded from being lost.
- Scan probes of all types will now correctly list their variations.



### Drones



- Drones with sufficient range will now be able to engage control towers.
- The firing effect for Bouncer I and Bouncer II is now correctly located on the model.
- Having the drone models option unchecked in Escape > Display & Graphics > Effects > Drone Models will no longer cause exceptions to be thrown when drones are ordered to attack.
- Fixed the zoom option when looking at sentry drone models. They can now be seen in all their glory, assuming you aren't making use of the feature in the previous entry...



### Skills



- When training learning skills via the skill queue, the trained skill bonus was not taken into account on the "remaining time" display. This has now been fixed.
- You can now drag skills from the certificate planner directly to the skill queue.
- You can now add skills to the training queue that will complete after the 24-hour limit. This change means that skills can be queued up to 23 hours and 59 minutes, with the final skill added bringing the queue to the maximum limit.
- You can now always add a skill to the queue via right-clicking it. Previously, it was not possible to do this while the queue was open.
- The skill currently in training will now be highlighted.
- A missing error message has been added to the skill queue system.
- The training queue will now correctly display a color for partially trained skills.
- Tech 3 subsystem skills will now display a proper description.
- Corrected an error message when trying to add too many skills to the training queue.
- A notification message has been added when skills are added to the training queue.
- Changed the name of the Astrometric Triangulation skill to Astrometric Rangefinding to better fit the skill's new role.



### Player Owned Structures, Outposts and Stations



- Updated the shaders being used for force fields.
- Fixed an error in the anchoring animation of ship assembly arrays.



### Character Creation and New Player Experience



- Changed the sentry type in one of the new player missions as the one used was doing too much damage.
- Removed a spider drone from one of the new player missions. Its presence was making the mission too difficult for new players.
- Fixed a typo on page six of the tutorial "Crash Course."
- Page six of the salvaging tutorial has now been re-written and will provide more clear and concise information.
- Fixed an error in the tutorial system where the back button was functioning incorrectly.
- Changed the tutorial window to allow for the correct display when goodies are being given out.
- The old scanning tutorial was still available. It has been removed as it is outdated.
- Corrected a button reference in the fitting screen tutorial.
- The tutorial window will now display corectly even when using a low resolution display.
- The background music will now correctly fade out when the racial introduction videos are playing.
- Fixed a typo on page one of the "Armor Tanking" tutorial
- Completing the tutorial "Crash Course" while in wormhole space will no longer cause an exception and a blank career funnel window to be opened. Instead you will be informed that you cannot access the career funnel while in wormhole space.



### NPC's



- Certain rogue drones were being listed as having a bounty of 0.0. This has been removed.
- Some sleeper structures were listed as having a bounty of 0.0. This has been removed.
- The description of one "Lieutenant Onuoto TS-08B" stated he was flying a Succubus-class cruiser. This has been corrected to frigate class.
- Some tutorial NPC's were not generating wrecks when destroyed. This has been corrected and wrecks will now drop as intended.



### Agents & Missions



- Fixed an exception being thrown when removing an offered mission from the journal. This, however, has no effect on the actual rejection of the mission.
- Fixed some grammar in the mission "Humble Beginnings" so that it is somewhat less suggestive. In addition, the mission objectives have been added to the mission briefing.
- Fixed the triggers in a couple of missions that were too slow. Some missions were unable to be completed under certain circumstances.
- Declining a mission will no longer automatically result in an offer of a new mission.
- Removed a confusing beacon in the mission "Rancorous Researcher (3 of 5)."
- In "Vitoc Vector - A terrible thing (4 of 4)," the mission critical can was not reachable due to the positioning of structures around it. These have been moved and the mission can now be completed.
- Fixed an issue causing the dock command to fail when issued from mission bookmarks when the map was open.
- Some missions were being incorrectly placed in an accepted state, rather than offered state. This has been fixed.
- The mission "Hungry For Entertainment" can now be completed.
- The expiry time is now correctly updated when accepting a mission.
- When declining a mission from a research agent the warning message will now correctly warn you of the possible consequences.
- Reorganized the mission details page so that it does not look like the loyalty points are a bonus reward.



### Epic Mission Arc



- An Amarrian commander was misnamed in a mission briefing. This has been corrected.
- Some rogue drones had incorrect names. These have been corrected.
- Fixed a typo in one of the mission briefings.
- Fixed a couple of typos in a post-mission agent conversation.
- When talking to a new epic arc agent the mission description was not displaying correctly. This has been fixed.
- In the last mission of the epic mission arc for the Caldari, the completed mission text was not being sent to the journal properly. This has been fixed. Additionally, the agent now correctly thanks you for helping the Caldari State.
- Modified the mission "Goading the Leader" as it was not possible to complete the stated objectives.
- Fixed a typo in the description for the Minmatar mission "Dal Segno Al Fine."
- The journal text for the epic arc mission "The Caldari Commander" no longer references Minmatar instead of Caldari
- The mission "Recovery" has had a trigger fixed that could cause the mission to remain in an incomplete state.
- Fixed an incorrect gender reference in the mission "It's Not Over Yet."
- Fixed an issue in "Dal Segno al Fine" that would give a warp to location option instead of an approach location option.
- The mission "Tracking the Queen (1 of 3)" has had its difficulty and timers reduced.
- Modified the mission description of "A Beacon Beckons" to better explain the mission objective.



### Exploration, Deadspace



- Modified the Angel Battlestation model in various sites to better fit into the environment.
- Modified the layout to the "Regional Angel Data Terminal" site to allow access to two containers that were unreachable.
- Warping to an encounter site at range will now work the first time you warp there. Previously your ship would land at 0km from the beacon no matter what range was set for the ‘warp to’ command.



### Wormholes



- Fixed an issue with several wormholes that caused them to have an incorrect number of jumps.
- Fixed a race condition that was causing errors when a wormhole collapsed.
- Fixed the sorting order of celestial objects in wormhole systems to sort and display in the correct order.
- Removed asteroid belt beacons from those wormhole systems that had them. These belts were empty.
- Some rare spawns have had their loot quality improved.
- Updated the difficulty on salvaging sleeper wrecks. Salvaging Sleeper wrecks was too easy.
- Fixed a wormhole signature that was too low (only affected a single wormhole).
- Corrected the scan group of the "Barren Perimeter Reservoir." It was showing as Gravimetric and is now properly displayed as a Ladar site.
- The "Perimeter Checkpoint" site has had some of its clouds removed to reduce its brightness.
- Fixed an issue with the AI where it was not correctly warp scrambling and webbing multiple targets. They should be much more efficient and ensure you stay put and die much more easily. Gotta love them NPC's!



### Science and Industry



- Corrected the skill requirements for manufacturing from the Tengu defensive subsystem blueprints.
- Text was not displaying correctly within some drop down boxes. This has now been fixed.
- Fixed the error message given if you try and invent from a BPO.
- Renamed the "Hybrid Tuner Data Interface Blueprint" to "R.A.M.- Hybrid Technology Blueprint."
- Salvager/Codebreaker/Analyzer/Gas Harvester II blueprints now have a Tech 2 icon.
- Removed the invention tab from several Tech 1 items which did not have Tech 2 counterparts.



### Market & Contracts



- Added the Gallente Mining Laser to the searchable types in contracts.
- Removed the unreleased "Moon Harvester II" from the market listing.
- The market groups for Rigs and Subsystems will now display different icons.
- Added some missing faction ammo types to the market.
- Fixed an exception being thrown when clicking "show route" in a contract.



### Graphics



- The textures of several Minmatar Tech 2 ships were incorrect with the Apocrypha release. These have been updated to the correct textures.
- Some ships were missing their correct colors when low quality shaders was enabled. This has been resolved.
- The missing "armory" model has been returned to the game.
- Fixed some display issues with Angel walls.
- Updated the cargo container explosion to use the new graphics system.
- Fixed a missing beacon model in the tutorial area.
- Glare Crust ice asteroids had the incorrect model. This has been corrected.
- Tech 2 hybrid guns will now use the correct model and texture.
- Modified the messages in the optimize settings dialogue to be clearer for low/minimum spec machines.
- Replaced some missing displays on the billboards.
- Hull fire effects on damaged ships have been updated.
- Fixed an issue where activating a cloaking device while the map is open would cause the model to still be visible on your client (although you are cloaked to other players)
- Fixed several wreck and deadspace objects that had incorrect shaders which caused them to appear incorrectly.
- Show info on stars will now correctly display their icon.
- Fixed numerous models which had incorrect radii, centers or both (100+ models).
- Some of the Tengu subsystems were missing engine trails. These have been scanned down, looted and returned.
- Some explosions were being cut short due to graphical cleanup. These will now be displayed in all their glory.
- Corrected the alignment of the beams from lasers.
- The ice harvester was incorrectly using the strip miner effects. It will now display the correct effect.
- Improved the smart bomb effect to have less impact on FPS.
- Corrected the pod cloak/uncloak transition so that there is no longer two copies of the pod.
- Fixed some transparency issues on the "Chief Republic Baldur."
- Resolved an issue that was causing a white square to appear over the fitting screen window.
- Several missing icons in "show info" windows have been restored.
- Some drones had a texture map that was too large. This has been corrected and drone models will now display correctly.
- Realigned some of the engine trails for the Legion.



### User Interface



- When opening the map, the point of interest will now correctly default to your current system.
- Fixed the animation speed of the map when selecting solar systems; it was too slow.
- Fixed an issue causing the scanner to break if it was stacked while you were resizing probes.
- The overview export would cause the client to crash if an illegal character was used in the filename. This has now been fixed.
- You are now able to export overview settings when they contain the "defaultmining" preset.
- The ability to drop modules on the center of the fitting screen and have them automatically fitted to the correct slot has been returned.
- Fixed the ability to cycle backwards through windows using ctrl+shift+tab.
- Fixed some capitalization issues on the fitting screen.
- The show info icon in agent conversation windows now has a tooltip.
- Returned a differentiation in the color tags for both good and high standings in the overview.
- Bookmark folders can once more be ordered alphabetically.
- Fixed the Assets window to correctly display your assets when it is set to solar system.
- Fixed the Assets window to correctly show the correct number of jumps when searching.
- Notification messages will be displayed when the hide windows option has been selected.
- If you change the UI colors while the fitting screen is open it will now correctly keep the new color
- Fixed an issue with the map where the right-click functionality for the camera movement was incorrect.
- Right click menus and tooltips are no longer displayed if the system (ESC) menu is opened.
- Fixed an exception being thrown when maximizing the show info window of a ship you are not flying.
- Fixed an issue that would cause a "100%" scan result to leave you off grid from the actual site.
- Removed wormhole systems/regions from the filter options for recruitment advertisements.
- The route highlighting on the map will now correctly follow the route chosen. Previously it would occasionally get lost.
- Fixed an exception being thrown when closing the ESC menu on the login screen.
- On the fitting screen, the maximum locked targets cell is correctly highlighted when a module affecting it is being touched.
- Removed some outdated tips of the day from the character selection window.
- Cynosural field brackets will now be displayed correctly when opening the map.
- An exception that was thrown when clicking on an empty slot in the fitting screen has been fixed.
- Fixed an issue that would cause the show info window to not display for items in loot containers.
- Shield flux coils will correctly preview the loss of shield hit points in the fitting window.
- Fixed an issue in the map where repositioning the control panel would also move the camera.
- The autopilot route line will now display even if the map is set to show no lines.
- Fixed an issue that would cause the on-board scanner to jam if it finishes a scan while you are in warp.
- Fixed an issue that would cause the scanner to be unusable if a probe expires during the scan.



### Localized Clients



- Modified the layout of the contract page to display Russian text correctly.
- Fixed an exception being thrown when opening EVEmail in the Russian client.
- Fixed an error preventing the About EVE window from loading in the Russian client.
- An exception will no longer be thrown when scrolling through the EULA in non-English language clients.
- Tutorial texts on some windows will no longer overlap.
- Corrected the translation of the "confirmed kills" column in Russian.
- Corrected some truncated text on the settings panel when the client is set to display Russian.
- Corrected a translation for the map UI in German.
- Added a number of missing Russian translations.
- Updated a number of Russian translations to fix errors in translation and overlapping text.



### EVE API and Static Data Dump



- Fixed an issue which caused the API to display an incorrect value for your character's attributes.
- Fixed an incorrect cachedUntil time in the API. This was causing issues with some applications.



### Miscellaneous



- The ESRB notice is now displayed no matter what language you have your client set to.
- Removed the debug code accidently left in place that was creating a "memdump.txt" file.
- Updated the descriptions of the cartographer certificates to reflect the changes to the scanning system.
- Fixed an issue with dragging items from a ship to a station container. This caused the item to be locked regardless of the container's settings.
- The volume of the background sounds in the hanger has been reduced.
- The sound volume for acceleration gates has been turned down a little.
- The downloader for patches will now automatically retry if there is a temporary network error.
- If a downloaded patch fails verification it will be removed from the cache directory.
- Aura's voice will have slightly less emphasis on the right speaker.
- The installer and patcher will now check for available diskspace before starting the extraction.
- Importing a malformed XML file for ship fittings now gives an error message rather than failing silently.
- Jettisoned cargo containers and wrecks will now show up on the directional scanner.
- The patcher/installer now has an option to prevent the automatic cleanup of downloaded files. By default, this option will delete the downloaded file once it has been installed.
- The downloader would sometimes crash if using "browse" to select the install location. This has been fixed.
- If you are patching from Quantum Rise or an older client which was also the classic client, the installer will clearly state that you are receiving an installer, rather than appearing to be a patcher.
- When changing an owner and a name of a fitting it will no longer change name/description first and then the owner, but the other way round.
- Fixed a race condition when opening the fitting screen, which would cause an exception.
- Fixed a typo in the patcher/installer when validation failed.
- Fixed an issue with ships and grouped guns that could, in rare cases, prevent login.
- The text label for "suppress turret sounds" has been renamed to be more accurate (the volume is reduced, not removed).
- Icon rendering has been fixed.
- Modified the installer/patch downloader to interface better with UAC. Previously on non-admin accounts the download process would fail to start due to access rights.
- Fixed an issue that would cause characters to be stuck if a cynosural field closed while a character was in mid-jump. Jumps will now be completed successfully.
- Turning off the Mining Foreman Link - Laser Optimization no longer causes loss of harvested ice.
- Modified the audio mixing for several items, such as warping, jumpgates and scanner probes.
- Fixed a typo in the description of "Strange Construction Blocks"
- Camera shake during warp is now active again (unless you choose to disable it of course).
- Corrected the title displayed in the patcher/installer.
- Corrected the grammar in the EVEmail sent when a corporation is expelled from factional warfare due to low standing.
