# Patch Notes for Apocrypha 1.2

- **Date**: 2009-05-14T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-apocrypha-1.2-1
- **Tags**: #patch-notes

## Overview
Patch Notes for Apocrypha 1.2 Table of Contents CHANGES FIXES EXPLOIT FIXES Changes  Critical The default overview setting for war, militia, and global criminal targets has been changed. War and militia targets will now blink when previously they did not. Global criminal target

---

**Patch Notes for Apocrypha 1.2**

**Table of Contents**

[CHANGES](#changes)[FIXES](#fixes)[EXPLOIT FIXES](#exploitfixes)

**Changes** 

**Critical**


- The default overview setting for war, militia, and global criminal targets has been changed. War and militia targets will now blink when previously they did not. Global criminal targets will no longer blink.A dev blog detailing this change is coming soon.


**Ships**


- The Naglfar has been overhauled to bring it in line with other Dreadnaughts. The Naglfar will now receive an additional mid slot along with a further 150 CPU. The powergrid has been reduced to 560,000 (-65,000). A new damage bonus has been added which will give the ship an additional 7.5% damage to projectile turrets per Minmatar Dreadnaught skill level. The bonus to citadel torpedo damage has been removed; however, the velocity of citadel torpedoes has been increased to 2,750 m/s while the flight time has been decreased to 25 seconds.
- The signature radius of all stealth bombers has been reduced by a small amount.
- The agility and the scan resolution of some ship classes has been adjusted to allow them to have a better chance of locking ships of their own size before they got to warp. Full details are available [here](//www.eveonline.com/ingameboard.asp?a=topic&threadID=1040109&page=5#129).
- When a Falcon cloaks and is jamming a ship, the icon showing that ECM is in progress and the jamming effect will be removed immediately. Additionally, CONCORD has declared all “BECAUSE OF FALCON” jokes passé.


**Modules**


- The CPU fitting requirements for a bomb launcher has been reduced to 50 CPU. In addition, the description for bomb launchers will state that it can be fitted on a stealth bomber only. Attempting to fit the module on any other ship will fail. This change will now allow the fitting preview window correctly when trying to fit a stealth bomber.
- The description of “Mission Rancorous Researcher (1/5) - Item 'Device'” has been reverted to "This is a thing. It does stuff."  All praise the power of the Device!
- Racial engine trails have been returned to Fighters.
- If a ship cloaks, all active modules that modify attributes, such as ECM, will stop immediately and the icons showing the effect will disappear.


**Weapons & Ammunition**


- The maximum velocity for bombs has been increased but flight time has been decreased. This change means that bombs will travel much more quickly. Maximum range remains unchanged.
- Cloaking a Falcon while there is a jamming cycle in progress and the jammer has been deactivated will now result in an immediate break of the jam cycle on the targeted ship. To clarify: if you start a 20 second jamming cycle on a ship, then deactivate the jamming module and cloak, the jam cycle on the target will immediately cease.
- The description of ECM Burst modules now says "emits random electronic bursts which have a chance of momentarily disrupting target locks on ships within range,"  while the Remote ECM Burst modules description reads "emits an area-effect electronic burst, centered on the designated target, which has a chance to momentarily disrupt target locks on any ship within range."  This change is to clarify exactly what each module does.


**Skills**


- References to “ice harvesting” will be replaced with “ice mining” in relevant skills.


**Player Owned Structures, Outposts and Stations**


- Corporation directors will no longer be spammed multiple times for the same starbase event.  They will receive one mail only.


**Character Creation and New Player Experience**


- Page five of the “Certificates” tutorial has been modified for clarity.
- Page two of the “Attributes” tutorials has been modified for clarity.


**Agents & Missions**


- The spawn rates in the mission "Technological Secrets (1 of 3)" have been adjusted and waves will now appear much more quickly.
- The mission "No Excuse" will now clearly advise players that there will be no faction penalty for shooting the Gallente ships. The ships have been changed to generic models and will no longer drop tags as a result. In addition, you now must destroy all the NPC's to complete the mission.
- Agents Inesmir Jimud and Arechar Amranin of Sisters of EVE will now display an appropriate greeting when meeting a player for the first time.


**Market & Contracts**


- Scan probe launcher blueprints have been moved to the market group under Blueprints > Turrets and Bays > Scan Probe Launchers.


**EVE Voice, Mail & Chat**


- The "Delete" option has now been added to the right-click context menu for corporation mails.


**Miscellaneous**


- We now keep a log on our Web interface when you close your petition.
- An error message has been added when trying to auto-patch using a non-working proxy in Internet Explorer.  This error explains network-related issues.


**Fixes** 

**Critical**


- Socket closed error messages will no longer cause problems on Tranquility following network changes. Following further network testing we have discovered that the issue of socket closed error messages has not been completely eliminated but has been significantly mitigated. Work will continue to eradicate this problem in the future.
- Changes have been made to the autopatcher which will result in a much smoother patching process. Returning players who are attempting to upgrade to Apocrypha from the old classic client will now be asked to do a fresh install to reduce the likelihood of verification errors. The new message will read "there is a new build available. An incremental update for your current build could not be found. Would you like to download a full installer now?”
- Synchronization errors caused by jumping through stargates, changing ships or docking and undocking have now been fixed and are working as intended.


**Need for Speed**


- Changes to shader textures and modelling will no longer put excessive stress on older graphics cards. This means they will no longer overheat while players are docked in a station.
- Database optimizations for the generation of storyline missions have been tweaked, resulting in a lesser load on the server.


**Ships**


- The description of all stealth bombers has been updated to reflect that it can equip a Covert Ops Cloaking Device.
- The description of the Rook has been fixed to read "10% Bonus to Heavy Assault & Heavy Missile velocity per level."
- The description of the Retriever has been changed to say that it has a "Godly" drone bay rather than a "Goodly" drone bay.
- Launching ships which has negative hit points into space will no longer cause exceptions.
- If a player attempts to install a jump clone into a clone vat-capable capital ship and does not have the required amount of money in his wallet a pop up warning message will appear.  The player who pilots the ship with the clone vat will now have the timer closed immediately rather than return an error.


**Tech 3**


- The 4th propulsion subsystem for Tech 3 ships, Interdiction Nullifiers, now utilizes the correct agility bonus per skill level.
- The correct missile rate of fire bonus will now be applied to the Tengu subsystem "Covert Reconfiguration." The description has been changed to "5% bonus to missile launcher rate of fire per level" instead of the misleading bonus to hybrid turrets.
- The description of the "Loki Offensive - Turret Concurrence Registry” has been clarified to show that there is no rate of fire bonus. This subsystem has bonuses to damage, optimal range and tracking only.
- The bonus for the "Proteus Defensive - Adaptive Augmenter" will now correctly state that it is “10% bonus to armor hit points per level.”
- All Tech 3 subsystems will now display their meta group as “Tech III.”


**Modules**


- The 1200mm Heavy Prototype I Artillery has been removed from the “Show Variations” tab as this gun model was never published. The 1200mm Heavy Prototype I Siege Cannon has exactly the same stats and will remain.
- All Gas Cloud Harvesting modules have had their descriptions updated.
- The ECM Burst effect has been fixed and is now weaker.
- Electronic Warfare drones now have visible engine trails.
- The first sentence in the description of ECM Bursts has been adjusted to "emits random electronic bursts which have a chance of momentarily disrupting target locks on ships within range." The description for Remote ECM Bursts has been changed to "emits an area-effect electronic burst, centered on the designated target, which has a chance to momentarily disrupt target locks on any ship within range."
- Attacking a cynosural field will no longer cause an exception as they now cannot be targeted.
- Activating a Strip Miner II module and then using "look at" on an asteroid no longer returns a mass of errors.


**Weapons & Ammunition**


- Grouped laser turrets will now allow a single crystal to be changed out once it has become completely damaged. For example, if you have aa Apocalypse with grouped pulse lasers using Tech II Scorch crystals, with varying degrees of damage you can reload used crystals without breaking the weapon group
- Javelin rockets will now hit at their maximum range as intended.
- The guidance systems for Rage torpedoes have been fixed, allowing them to impact targets at very close range.
- The last shot fired from a volley of guns (projectiles or hybrids) before the clip runs out will now hit targets as intended. Previously the last round had a higher chance of missing due to calculations showing the guns at zero ammunition.
- The flight range of Javelin Rockets has been increased.
- An empty module will no longer attempt to reload after overload has been turned off.
- Rage torpedoes will now hit close range targets.


**Drones**


- Idle drones are no longer displayed as attacking in the targets overview window.
- Mining drones will now display the correct laser effect.
- An exception will not be thrown when a rogue drone attacks a player ship.
- Drones can now be scooped up from 2500 meters or less.  This fixes an issue with some capital ships and sentry drones that could appear out of range when launched.


**Skills**


- The description of the trade skill “Visibility” has been changed to clarify exactly what it does.
- The armored warfare skill no longer causes negative armor issues.


**Player Owned Structures, Outposts and Stations**


- Gallente control towers, along with its faction variants, have had a makeover and now display some previously missing animations.This will be addressed in a future patch
- Fixed an exception error that could occur if you put a production structure online via the production window on the POS management screen, close the management screen and reopen it prior to the structure coming online. Checks have also been added to ensure that reactions cannot be removed from reactors while they are linked to other things. A new error message will be displayed to those who try this.
- A second ghost silo will no longer be displayed when anchoring any Biochemical, Catalyst, Expanded, Hazardous Chemical or Hybrid Polymer silo.
- "Guristas torpedo battery" and "Dread Guristas torpedo battery" have been added to the variations tab of "Torpedo Battery".
- The description of the Experimental Laboratory has been fixed to remove any grammatical errors.
- It is now possible to rent offices at Ghesis V - Moon 9 - Xsense Chemical Refinery.
- "Trash it" will only appear as an option for items in stations. The option will be unavailable for items in control tower bays.
- The fuel consumption and fuel time for heavy water and liquid ozone in starbases will now display correctly.


**Boosters and Implants**


- "Hardwiring - Zainou 'Gnome' KZA500" has been added to the market group implant slot 10 - Gunnery Implants and "Hardwiring - Zainou 'Gnome' KTA10" to implant slot 6 - Missile Implants. Both implants now have buy and sell options in the market context menu.


**Character Creation and New Player Experience**


- The "Targeting" section of the “Crash Course” tutorial is now working properly.
- The "Camera Movement" tutorial now displays the correct number of pages and tasks for completion.
- The correct text is now displayed in the tutorial "RepairShop."
- A typographical error has been corrected in the “Mining Tutorial (6 of 12).”
- A typographical error has been corrected in the “Contracts Tutorial (12 of 17).”
- The text in the "Drones Tutorial (6 of 10)” will now correctly say “Drones in local space."
- A grammatical error has been fixed in the “Creating and managing a corporation” tutorial.


**NPCs**


- The correct models will now be displayed for the Amarr Navy Colonel, Caldari Navy Commodore, Gallente Navy Fleet Captain, Dire Guristas Despoiler and Sansha Administrator. The spawning of these vessels will no longer cause exception errors to be generated.


**Agents & Missions**


- Standings will now be calculated and displayed correctly when Connections and Diplomacy are applied to any character.
- There is no longer a "Continue" button displayed in the conversation window when you talk to an agent remotely.
- The "Continue" button in the agent conversation window will now be changed to "Request Mission" when you click "Complete Mission" and when you click "Decline."
- The lookout towers in the mission "Athran Exigency" will now be displayed correctly.
- Descriptions have been added to the show info for Runner Drones and Webber Drones in the mission "Cash Flow for Capsuleers (3 of 10).”
- The spawn container located inside the Crumbling Angel Antiquated Outpost has been repositioned in order to allow easier player access.
- Sisters of Eve agent Inesmir Jimud will no longer greet you for the first time insinuating that you currently have an outstanding mission. She will now simply greet you by name.
- The mission "Deliver the Goods (2 of 5)” can now be completed successfully when using mining drones to mine the ore.
- A grammatical error has been corrected in the mission briefing for "Vengeance."
- A grammatical error has been corrected in the mission de-briefing of "Balancing the Books (4 of 10).”
- A typographical error has been corrected in the mission briefing for the Amarr version of "A Dark Lesson."
- A grammatical error has been corrected in the mission briefing of "Cash Flow for Capsuleers (10 of 10)."
- A typographical error has been corrected in the mission briefing of "Murderer Brought to Justice."
- The correct NPCs have been added to the level three mission "No Excuse.” Keep your wits about you and concentrate during this mission!
- The mission "Governor's Aide (4 of 5)" from Agent Nossa Farad can now be completed at the drop-off location Nossa Farad's Inquisitor in Chanoun as well as at Zoohen III - Theology Council Tribunal.
- Players are now able to dock at agent home bases when giving the dock command from an encounter location.  It will not matter if the map is open or not.
- After completing the epic mission "Our Man Dagan" and warping to the agent's location, the correct option to approach rather than warp to will now show.
- The mission "Deliver the Goods (2 of 5)” can now be completed by using mining drones to mine the ore.
- A typographical error in the text displayed when using "Ssow info" on agent Gara Kort has been fixed.


**Exploration & Deadspace**


- A typographical error has been corrected in the message displayed upon warping to the "Sansha Hideaway" deadspace complex.
- The spawn container located inside the Crumbling Angel Antiquated Outpost has been repositioned in order to allow easier player access.
- Cosmic Anomalies have been added in the Fribrodi constellation of Metropolis.


**Science and Industry**


- Blueprints will now disappear from the manufacturing list after installing a job from corporation blueprints tab.


**Market & Contracts**


- Contracts will now display the cost of an item in words (hundreds, thousands, millions) even if the figure is not a round number. For example, a contract for an Invulnerability Field II at 200.999.999 ISK will be displayed in word form also as 200.99 Million, much the same as if it were a round number.
- Missing Faction F.O.F cruise missiles, F.O.F heavy missiles, F.O.F light missiles, torpedoes and Sisters scanner probes have been added to the market group, allowing them to be traded normally.
- The 'Vrykolakas' Heavy Nosferatu I Blueprint has now been added to contracts, allowing players to search for the blueprint.
- Previously, if you right click on an item and press "Buy this type" and then proceeded to open the market window to buy the same item, the market window would not allow you to purchase anything unless the first "Buy this item" window had been closed. This has now been fixed and the item will now be purchased normally.
- All faction ammunition and special items such as the Sisters of EVE probes are now tradable on the market.


**Corporation & Alliance**


- Players can now rent offices at Ghesis V - Moon 9 - Xsense Chemical Refinery. CONCORD has evicted the homeless who had taken up residence through the airlocks. Gotta love those guys.


**Graphics**


- All Hyperion ship models have been recalled by the manufacturer and have been given a new paint job on the underside of the hull in order to display the correct textures.
- Animated pistons, gears and cylinders will now be displayed in the preview window for the relevant mining barges and exhumers.
- Fire and burning effects on several ships have been increased to properly reflect the destructive damage unleashed by the mighty Capsuleers.
- Changes have been made to bloom effects for ships in warp resulting in a smoother warp graphic.
- The graphical effects for the Remote ECM Burst are now displayed as intended.
- Exploding objects such as ships and structures now have the correct particle dispersal effect. Previously they would just mirror the velocity and direction of your ship.
- Shadows will now be displayed correctly on a player starbase according to the position of the sun in the system.
- Minmatar stargate models will now display textures correctly when bloom levels are adjusted.
- Warp tunnel effects now aligns with the direction the ship is moving.
- The Radio Telescope will now animate correctly.
- Structure damage in DX9 models of jump freighters and normal freighters has been improved.  The feeling of going down in flames has been increased.
- Changing the bloom setting will no longer affect the warp tunnel effect.
- The EVE gate in New Eden no longer causes distorted warp effects or problems with the solar or star maps.
- The cloaking effect is now translucent to other graphical effects such as gate activation or weapons firing.
- The graphical effect of the Heavy Interdictor bubble now accurately represents its true size.  This includes any skill bonus increases.
- There is no longer a pixelated effect in Minmatar stations.
- The structure flame effect will now display correctly.
- The remote ECM burst effect beam now displays correctly.
- The sun is now visible behind a cloaked ship.
- The shield booster effect for Violator drones now covers the entire ship.
- The Modulated Deep Core Miner II beam has undergone a paint job and has been returned to its blue color.
- The level of detail in all dungeons has been enhanced, resulting in objects remaining in place for longer and in greater detail.
- The new particle effects system ensures that objects do not explode in relation to the movement of the player ship.


**User Interface**


- A corrupt setting in the overview has now been fixed and the overview will now open and display properly when a pilot is in space.
- The correct damage received will now be displayed correctly on all kill reports. Erroneous reports of battleships dying after only receiving 700 hit points of damage will no longer appear.
- The distance displayed over the ship console while a ship is warping to an object has now been fixed and will display correctly. In addition, several exception errors in the logserver have been fixed and will no longer be generated when a ship initiates warp or after it comes out of warp and begins to approach an object.
- Using the right click option in space now works as intended.
- Inviting multiple characters to a fleet will now list all characters that are offline rather than listing one single person. For example, if you were to send an invite out to your entire buddy list and three of those people were offline it will now list all unavailable members. Previously it would only display the first person alphabetically on the list.
- An exception error will no longer be generated when using Show Info on a star while in space. The Show Info page will now load properly.
- A UI glitch that appeared when a player was podded and lost a rank of a subsystem skill has been fixed. The attributes and skills tab will now display as intended.
- The Tutorial Drone will now be checked on the overview settings by default as it is required for the “Crash Course” tutorial.
- You can now both open and close the scanner window with its shortcut (default of Ctrl+F11). If the scanner window is minimized and the shortcut is used, it will maximize the window.
- The "Unlucky" message which is displayed when clicking on the ticker button upon corporation creation will now only display once instead of multiple times when pressed.
- The "Access Denied" messages will no longer display two periods at the end of the sentence.
- The "Clear History" option has been removed when using right-click on the password section at the log in screen. This option had no effect anyway and was therefore redundant.
- The message "no transactions found" will now be displayed when clicking on the transactions tab of the wallet when no entries have been logged.
- The shortcut tooltip will now display the correct shortcut when set instead of displaying "None."
- The overview will now correctly update distances if your ship is moving toward an object while the star map (F10) is open.
- Ctrl+drag now works properly for both resizing selected windows as well as the connected windows below it.
- The "Reset Tutorial State" list will now display the tutorials in alphabetical order.
- A scroll bar will no longer appear when a container size is minimized unless it is needed.
- An icon has been added to the market group "Probes" under "Ammunition & Charges."
- Mobile Warp Disruptors now display an icon in the show info window.
- The attribute display name for “Offensive - Covert Reconfiguration” subsystems for all four races have been changed to “Cloak Reactivation Delay” when clicking on Show Info.
- Importing overview settings now works correctly. Importing a setting will no longer append rather than replace existing tabs.
- A grammatical error has been corrected in the character termination email.
- An inconsistency has been fixed when changing the name of a ship or pod in space. They will now update immediately.
- The URL length has been set at one line when creating a corporation and will not overlap other text.
- The tooltip for info icon in Contracts is now displayed correctly.
- All the solar systems for NPC corporations are now correctly marked with green dots on the star map.
- The list of BPOs refreshes immediately when changing divisions in the Science and Industry tab.
- EVE Voice’s text for its troubleshooter no longer spills over into other areas.
- The selected item's window, portrait and show info icon are no longer missing for the LCO Spatial Rift.
- The production limit attribute has been clarified in blueprint information windows.
- The "show info" command in Auto-link system now works properly for items, ships and modules.
- "Must select 1 choice" is no longer displayed on the scan result window when using a cargo scanner.
- The 100% damage on an active ship will be correctly shown in the damage notification column of the Repairshop window.
- The EVE Mail inbox tab will not now blink continuously after receiving new mail from a blocked character after unblocking the character and viewing the new mail.
- "Reload" and "Reload All" options are displayed correctly in the right context menu of module button after performing group mode.
- The prompt message displayed when a podless player tries to jump clone has been changed to "if you have been podded, please open the ship hangar and board a ship in order to receive a fresh capsule. You will then be able to leave that ship and clone jump."
- A typographical error has been corrected in the prompt message when accessing corporation hangars that do not belong to your own corporation.
- A typographical error has been corrected in the prompt message when attempting to remotely bookmark a location on the map browser.
- No exception will be generated in the log server when clicking the “Buy” button when no type is selected. A notify message will now appear stating, "you cannot place a buy order when there is no type selected."
- The ability to select all via Ctrl+A in the left pane of the reprocessing plant has been disabled.  This resurrects the deselect function.
- The border size of pinned window now remains same when joining/leaving stacked channels repeatedly.
- Ctrl+drag will now work when resizing a selected window in addition connected windows below it.
- The "Load," "Overwrite" and "Delete" buttons will not be displayed if no Preset is selected in the LP store filters.
- In the overview settings, pressing Ctrl+A works for filters/types only. Switching to the states tab and pressing Ctrl+A will no longer remove anything from the overview window.
- The color of lines in the star map will update correctly according to selection.
- In Overview Settings > Ships, moving the selected line up or down by using “Move Up” or “Move Down” buttons now works correctly.
- In the POS management window, tooltips for kinetic and thermal resistances now display correctly.
- Ctrl+A will no longer override the inability to select group entries.
- In the settings window of the market, the checkbox text "From" and "To” and the input box now are all aligned perfectly.
- Overview items will now update correctly when the map is open.
- The "Use" option box will appear even if there are more POS modules than can fit on the screen.
- Chat channels will continue to function normally if the hard drive storing the EVE log files is close to being full.
- Drones are now sorted alphabetically.
- Click and drag will now work on vertically grouped windows.
- The "return and orbit" command for drones will now remain active in the selected item window at all times.
- There is now a "show contract" and an "open certification planner" right-click option when linking to contracts or certificates in notepad or chat.
- Being hit by rogue drone weaponry will now cause graphical effects to show the gun or missile attack.
- Starbase role names have been standardized.
- Explosion effects cannot be felt if the solar system map is open and the player ship is being attacked by NPCs.
- Station glass now occludes objects such as planets or ships as intended.
- The Tech 2 BPO icon now displays correctly in the info window and market details page.
- Splitting a stack in the pick items stage of the contract creation wizard now updates immediately and will work as intended.
- Using CTRL-A to select all now works correctly on subdivisions such as the assets list.  It will select all within a scroll but not groups.
- Dragging and dropping a charge on the fitting window to a capacitor injector-fitted ship will not throw an exception. Dragging ammunition onto the screen will also work as intended.


**Sound**


- 250mm Howitzers will now play the correct sound when fired. Previously they were playing the sound for autocannons.
- Audio levels are now playing the correct sounds on turrets, explosions and stargates until the ship is completely zoomed out.
- The "Play" button on the jukebox will no longer skip to the next track when pressed. It will now fade out and play the current track from the beginning.
- Explosion sound effects will now play when shooting close targets with missiles.
- Sound issues caused by boosters and jump gates when docking into a hangar has been fixed.  We also closed a memory leak in the process.
- Booster audio now activates on dock command, autowarp, etc.


**EVE Voice, Mail & Chat**


- An exception error will no longer be generated in the log server when accessing the "Audio & Chat" option in the ESC menu.
- Column lines have been removed from the EVE Mail folder. Mails from players with extremely long names were crossing over other columns.
- "ECHO Speaking in channel" will no longer be highlighted in the Fleet window after leaving the Echo Test Channel.
- The body of mails will resize correctly when the inbox window is resized.


**Mac**


- URL links on the Mac client will now display correctly rather than having "00" displayed at the end.
- All map pictures will now display correctly in the Cider client.


**Localized Clients**


- A change has been made to how the member status is displayed in player corporations and alliances within the Russian client.
- The text in the contracts window of the Russian client will no longer overlap.
- The "auto target back" setting in the ESC menu has been correctly translated in the Russian client.
- Petition category and queued translations are no longer erased after a Transam downtime.
- The mail sent out when a corporation member has been deleted has been corrected in the German client.
- The text for the petition section "reimbursement, ships and combat" has been corrected in the Chinese client.


**Miscellaneous**


- Several GM tools have been fixed allowing the Customer Support department to assist you better.
- Changing the shader quality or textures through the ESC menu will no longer result in the client crashing unexpectedly.
- Certain textures in some spawn containers were causing exception errors on older video cards and computers resulting in crashes and lock ups. These textures have now been removed.
- The location of the Otitoh IV - Moon 1 - Lai Dai Corporation Factory has been changed in order to allow players the option to dock correctly at the station. Previously a warp attempt to this station would land a player in the "Devils Dig site" but that will no longer happen.
- Entering wormholes or certain deadspace areas will no longer generate an error in the log server.
- Sound effects and the jukebox have been fixed. Fixes to the sound engine mean sounds like mousing over items in the hangar and station environments will now play correctly.
- An icon is now displayed on the show info page for "Mining Pollution Cloud."
- An error will no longer be generated in the log server when activating a salvager module on a wreck.
- All references to LADAR and RADAR will now be displayed as Ladar and Radar. This covers both modules and sites.
- Using "Show Info" on any Valkyrie drone model will no longer result in an error being generated in the log server.
- The certificate for "Harvesting Comptroller" now requires warfare link specialist to gain the improved certificate. This replaces the previous requirement of battlespace technician.
- Scrapmetal Processing has been removed as a requirement for any "Refining Foreman" certificate.
- Multiple items that were displaying Unicode characters in their name or description have been fixed.
- An exception error is no longer generated in the in game petition window (F12) when selecting a petition category without first selecting a group.
- Grammatical errors have been corrected in the description of Battleship Turret certificates for hybrids, projectiles and lasers.
- We have optimized the database calling system. It will now reduce the amount of times it calls for information that stays constant.
- Declining a mission will no longer cause a flood of agent warnings in the log system.
- Deadspace signatures will now load as expected in wormholes.  This will ensure that no more exceptions are thrown when players enter the wormholes.
- A podless character cannot be transferred to space by any means.
- Right-clicking at the edge of any window will no longer generate an exception in the log server.
- No exception will be generated in the log server when right-clicking while trying to resize a window.
- No exception will be generated in the log server on pressing ENTER key repeatedly when the focus is on the get contract button.
- No exception will be generated on confirming the alert message after an invalid "item type" search for linking items in Notepad.
- No exception will be generated in the log server following the mass-trashing of impounded corporation assets.
- No exception will be generated when changing the position of the tabs as windows are opened in tabbed view.
- No exception will be generated on spamming the "Reset" button for "Reset Suppress Message Settings" in the ESC menu.
- The client will no longer lock up if a ship model cannot be loaded.
- If “Load Station Environment” (ESC-menu -> Display & Graphics) is not checked and a player clone jumps into space to a clone vat bay, the picture of the station environment will stick to the screen instead of space being shown. Overview and brackets will be rendered normally. Docking and undocking at a station or relogging the client brings back the normal space rendering. To avoid this issue, you can turn on the “Load Station Environment” option prior to clone jumping (it can then be turned back off after the jump if you like).


**EXPLOIT FIXES** 


- Several exploit issues have been fixed, making EVE a better world to live in for us all.
