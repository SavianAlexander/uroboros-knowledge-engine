# Patch Notes for Incursion 1.1.0

- **Date**: 2011-01-18T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incursion-1.1.0-1
- **Tags**: #patch-notes

## Overview
Patch Notes for EVE Online: Incursion 1.1.0 Deployed January 18, 2011 Table of Contents FEATURES FIXES CHANGES FEATURES Sansha's Nation is finalizing incursions, and they are making their last preparations. Get ready! The new Character Creator is now live on Tranquility, and

---

Patch Notes for EVE Online: Incursion 1.1.0

Deployed January 18, 2011

Table of Contents[FEATURES](#features)[FIXES](#fixes)[CHANGES](#changes)

**FEATURES**


- Sansha's Nation is finalizing incursions, and they are making their last preparations. Get ready!
- The new Character Creator is now live on Tranquility, and your character would very much like to be beautified.
- Various improvements have been made to EVE Gate, including EVE Voice Beta!
- Extended changes and improvements to the Contracts system have been done.
- A number of graphics improvements and updates have been added to the game.
- The API has received numerous improvements.
- The keyboard shortcut system in EVE has been completely revamped. There is a new layout including organized tabs, additional combat commands and new modifiers. CTRL + ALT + SHIFT + Mouse 4/5/6 are all new modifiers.
- Upgrades to the EVE Client make it so CPUs that do not support the SSE2 instruction set will no longer be able to run EVE Online. You can see [this blog](//www.eveonline.com/devblog.asp?a=blog&bid=844) for more information.


**Incursions**


- CONCORD has set up a new LP store to reward players participating in Incursion.
- New implants and capital weapons relating to Incursions are available.
- More details on the Incursion feature and when you can expect Incursion to be enabled can be found in [this blog](//www.eveonline.com/devblog.asp?a=blog&bid=819).


**Contracts**


- Details about improvements to the contracts system can be found in this [dev blog](//www.eveonline.com/devblog.asp?a=blog&bid=833) by CCP Atlas.
- You can now "copy" a contract that you have created from the contract details context menu. This will open up the "Create Contract" wizard with parameters from the copied contract prefilled in.
- Insured ships that are put into a Courier contract will no longer have their insurance voided.
- When you log in, you will now be notified if there are any contracts assigned to you. You can now easily jump into the contract in question.
- Item Exchange Contracts are now the default contract type when you create a contract. They also have a new (repurposed) icon.
- A new "Volume" column in the "Select Items" step of the Create Contract Wizard has been added. Additionally, when creating a Courier contract, the volume of selected items is summed when they are selected.
- Damaged items can now be put into all contracts. If an item is damaged, it will be noted in the Contract Details window.
- Contract details will now show the security level of the system(s) in question. It will also show if any system en route to the system is a different security level than the current system.
- Contract details will now show if a station is player owned and therefore potentially unreachable.
- Contract details will now show if a system is unreachable with your current autopilot settings.
- Added a "Find Contracts" context menu option for plastic wrap containers to allow you to bring up the contract which the container belongs to.
- Added a "show info" context menu option for search results containing one item.
- Added a link to preview an item in the contract details window.
- Loan contracts are no longer supported in the contracts system.
- When you contract a ship with loaded charges, the charges will be removed and are placed into the ship's cargo hold instead of the hangar. If there is insufficient space in the cargo hold, the charges will placed in the hangar instead.
- Contracts with ships in them show a "fitted" tag on each item if it is fitted on the ship rather than located in a cargo hold.
- The create contract wizard has been simplified a bit.
- The ignored issuers list limit has been raised from 80 to 1000. It is filtered on the client instead of the server.
- The number of top level items in a contract has been raised from 100 to 200.
- The contracts start page now includes the count of all contracts assigned to your corporation for all members of the corp. The corporation and your private assigned-to list counts are split up into item exchange/auction and courier, each with relevant links.
- Labels on contracts details now show the text "You will pay" and "You will get" instead of "price," "money offered" and "offered items."
- Want to Buy contracts now always show the requested items in a list even if there is only one item.


**Graphics Improvements**


- [God-rays](//www.eveonline.com/en/incursion/article/149/a-few-words-from-team-trilambda) were added to Incursion-infested systems. These can best be seen by orienting the camera so that the player's ship occludes the sun in infested systems.
- Ship booster lensflares use the new depth buffer. This means that boosters don't cut through solid geometry any more.
- Changes to the way suns are rendered have been made to improve performance.
- Changes to the way the Tactical Overlay is rendered have been made to improve performance.
- Sansha's-infested systems now have a greenish hue.
- Depth effects were added. This was needed to make effects such as god-rays possible.
- Fixed windowed mode in the Windows client. This makes the client appear to be in full-screen mode while staying in windowed mode. This change frees up a bit of screen real estate for users.
- The detail shader on Sansha's capital ships has been improved, resulting in better looking capital ships.
- "Out of memory" errors are now handled more gracefully, and more "out of memory" error messages have been added to the client.
- A number of graphics-related memory leaks have been plugged.


**Wormholes**


- Sleeper NPCs will now properly use their energy draining effects on players, which increases the difficulty of Sleeper sites in wormhole space.


**EVE Gate**


- We have introduced EVE Voice integration into EVE Gate, which is in a beta state for now.
- All of EVE Gate was localized into German and Russian, which can be switched in the Account Settings.
- The editor for emails, biography and the like has been replaced with one less prone to making erroneous markup, making EVE mail more reliable.
- You can now view profiles without logging in. You can show off your new fancy avatar to your friends without logging into EVE Gate.
- The contact limit has been increased to 1024.
- Contact labels were added to EVE Gate.
- In place of the old contact folders, we have introduced contact labels that work just like mail labels.
- EVE Gate will now remain up for downtime.
- The following features will now be up and running during downtime: - Login and character selection
  - Profile settings
  - Broadcasts, both on Home and profile pages
  - Character, corporation and alliance profile pages. Certain features, however, are disabled when you click them. For example, trying to add a new contact during downtime will give you an error.
  - Read-only standings shown on profile pages.
- The following are disabled during downtime/VIP: - Mail
  - Calendar
  - Contacts
  - EVE Voice
  - New mail/contacts/calendar counters on both the Home and character selection pages
  - Upcoming Events on the Home page
  - Add/Edit/Delete Standings on char/corp/alliance profile pages
  - "Send a Message" on char/corp/alliance profile pages
  - PLEX tab on Character Sheet
- You can now view the status of your subscription from your character sheet
- You can go directly to the market or the PLEX website from the character sheet and purchase PLEX


**API**


- Fixed an issue with YAML parser causing some player wallet journal requests to error.
- New Wallet Journal API - No longer rate limiting but will rather return cached results from the earlier call.
  - Same call, /char/WalletJournal and /corp/WalletJournal
  - Requires full API key
  - Optional inputs rowCount (to control the number of mail headers displayed) and fromID (the non-inclusive messageID to read FROM into past mails).
  - Functions much like the new mail API.
- Calendar API - No longer rate limiting
- Modified /char/UpcomingCalendarEvents - Returns next 50 upcoming events from characters, your corporation or alliance.
  - Requires FULL API Key
  - Cached for 57 minutes
- Modified /char/CalendarEventAttendees - Returns the attendee status of events
  - Requires FULL API Key and a comma separated list of eventIDs (also supports ids as that variable name)
  - Requires proper roles for corporation/alliance events.
- Notification Header API - No longer rate limiting but will rather return cached results from the earlier call.
  - Adding char/NotificationTexts
  - Returns the body text of notifications
  - Requires FULL API Key and a comma separated list of notificationIDs as the variable ids.


**Character Creator**


- A new character creation interface has been added, and Race, Bloodline and Gender are now selected using a new interface.
- Both old and new players will be able to use the reworked EVE character customization system to create a new Avatar and Portrait.
- We are adding support for an optional third name during the new character creation process. This is being done in order to expand the amount of available names in the EVE database and avoid having to purge older names. When you create a new character, you will put in your first two names in one box with a space between the names, and then use the second box for your third name.
- New Characters can have a selection of education options to choose from; this dictates their starting location.
- Current characters will have a grace period before having to commit to a new character avatar and portrait. During this grace period you can take your time before finalizing your new avatar and portrait to suit your tastes. Once this grace period is over all characters will be forced to create a new and updated character portrait and avatar during the login process. A final date for the end of this grace period will be announced. Stay tuned to the MOTD and news on [www.eveonline.com](//www.eveonline.com) for more information.


**Macintosh**


- Antialiasing is now disabled for Leopard users. This should help avoid reported client startup problems.
- You can now switch between windowed and full screen mode via the ESC menu.
- Users can now choose to disable Multithreaded OpenGL via ESC menu settings. This option affects CPU load and graphics performance.
- Running EVE in the background should no longer severely slow down other applications.


**Planetary Interaction**


- Players can now upgrade command centers from basic all the way up to elite without replacing their colonies.
- Only basic command centers will be seeded on the market now; larger centers will now be purchased as upgrades via the upgrade window.
- Extractor control units (ECUs) have been introduced on all planets. The ECUs can be built from the build menu, replacing extractors.
- Extraction is now done by extractor heads that are installable via the ECUs.
- ECUs also allow installation of extraction programs. Players can now create extraction programs that run up to 14 days. These automated extraction programs will harvest resources based on the settings in program creation.
- Prior to installing an extraction program, placed extractor heads can be moved by clicking the button at the center of the extraction head. Extraction heads can be moved via drag and drop to resource hot-spots for a greater extraction amount.
- You can set the area that your extractor heads will extract from, which will affect the length of the extraction program and amount of extraction.
- Overlapping extractor heads from different ECU's will cause a reduction in extraction amount from each extractor head.
- Pinned UI windows are now affected by the global window transparency settings.
- The new ECU window will display a colored graph to indicate the deposit of each cycle.
- The output per cycle of ECUs diminishes over time. The output is, however, variable in a way that even though it generally decreases, local "hotspots" can still occur.
- Sounds have now been added to cover changing resource intensity and interference from other extractor heads.
- Routing materials is now more intelligent. Processors are prioritized based on how close their hopper is to being filled. Storage pins are routed in equal amounts.


**FIXES**

**EVE Gate**


- When editing a calendar event, the character counter for the description field is now correct when you open the window.
- Inbox, corporation, and alliance labels are now auto added to the appropriate mails, and can be removed just like in the EVE client.
- EVE mail recipients now display correctly when composing mail using IE8.
- Scroll bars have been tamed, and there are no more unsightly scroll bars when selecting contacts to invite to events.
- You no longer get a CSPA charge when trying to create an event without a name.
- You now receive more informative messages when restoring EVE mails from the trash.
- Calendar events are now sorted sequentially in month view.
- Clicking cancel in "edit calendar event" popup no longer resets scroll position.
- When cancelling an action on a mail/contact label, the drop-down menu now closes correctly.
- You can no longer create calendar events in the past.
- The corporation "Add contact" link from the broadcast page now works as intended.
- On creating a new event in a future month, the calendar retains the view rather than resetting to the current month.
- When creating a label by pasting text, the "Create New" button now gets enabled.
- Long titles no longer break page alignment; they are truncated instead.
- You can now view corporations with two subsequent dots in their name.
- When deleting a mail label, it no longer keeps the counter from the old label when creating a new one.
- You will no longer get an error if you have a broadcast from a deleted character.
- The tab-order when logging in now goes to the "Keep Me Logged In" checkbox before the login button.
- "Faction" is now translated in both Russian and German.
- When you click abort after clicking remove broadcast, the remove link now stays usable without reloading the page.
- Colored mail labels no longer break the label.
- You can now search for characters with apostrophes, dashes and dots in their name.
- Numerous fixes were done to improve the experience when using Internet Explorer.
- Fixed an error where the time remaining on the character sheet was incorrect in some cases.
- You can now remove participants from an event in Opera.


**Player Owned Structures, Outposts and Stations**


- Jump bridges can now be successfully probed down.
- An incorrect message that displayed when dropping large quantities into assembly arrays has been fixed.
- Office rental at Outposts can no longer be 0 ISK.
- Fixed an issue where it was possible to anchor weapon batteries inside PoS shields.


**Science and Industry**


- Rorqual manufacturing jobs now default to "my cargo" for job input/output.
- The quantity of Pyerite in Compressed Pure Jaspet and Compressed Pristine Jaspet was switched around in the refining message window. This has been fixed.
- You can now build Electronic Attack Ships and Heavy Interdictors in Tier 2/3 Amarr Factory Outposts.
- Brackets will no longer display when in Planet View.


**Skills**


- A "Message not found" dialog would appear in certain cases when training skills. A proper error message has now been added to describe the error.
- An issue with Elite certificates has fixed.
- The Business Tycoon Standard certificate now displays the correct requirements.
- Fixed a typo in the Remote Sensing skill description.
- An extra "the" has been removed from the description of "Cloak Operator Elite" certificate


**Ships**


- The Widow Black Ops bonus will now correctly affect ECM burst modules.
- The Tengu Gravitational Capacitor subsystem will now correctly affect warp capacitor need.
- CPU and Powergrid now rounds correctly to two decimal places.
- Nidhoggur's "Shield and Armor" description text has been updated to reflect its Capital status.
- Fixed an infrequent issue with shield recharging while undocking from a station.
- The Noctis now has the Primae as a variation and vice versa.
- Sensor strength of T3 ships fitted with Dissolution Sequencer subsystems are now correctly calculated when racial sensor strength implants are present.
- Despite the pressures of being a modern day capsuleer pilot, it will no longer be possible to eject from one's own pod!
- Fixed many cases where the collision radius of a ship was larger than its model size.
- Freighters now have race-specific propulsion types.
- It is now possible to link tournament prize ships in chat.
- The Capacitor Regeneration Matrix subsystem description has been fixed to reflect the bonus applied.


**Market & Contracts**


- An issue with contract message spam has been resolved.
- You can now correctly search for journal entries by date.
- Price warning pop-ups text for market orders has been improved to include orders being edited.
- Fixed an issue with moving items mid contract creation.


**Modules**


- Modules returned through ship repackaging will now correctly fit to another ship.
- Microwarpdrives will now work after undocking after being warp scrambled prior to docking.
- Fixed an issue with Tractor beams occasionally not working.
- Fixed an issue with ship maintenance bays occasionally causing modules to appear offline.
- Used mining crystals will now correctly reload.
- Civilian modules can no longer overheat indefinitely.
- Fixed an issue with ECM burst modules gaining aggression inside a PoS forcefield.
- Fixed an occasional issue with cynosural beacons producing erroneous jump results.


**Boosters and Implants**


- Low-Grade Grail Omega radar sensor strength bonus is now calculated correctly.
- Using Mining Foreman Links in fleets caused the mining lasers cycle timer to go out of sync. This has been fixed.


**Weapons & Ammunition**


- The group "Ammo" is now called "Projectile Ammo."
- Hail ammunition now has the correct tracking modifier applied.
- Charges will now correctly move from the cargo hold when dragged and dropped onto a stack in weapon array ammunition storage.
- Fixed an issue with Doomsday device timers prematurely resetting.
- Wolf Rayet systems will now affect Standard Kinetic missiles appropriately.
- Right-click contextual menus will now correctly display the ammunition that was last used when attempting to reload.


**Exploration & Deadspace**


- The exploration site Drifting Cask has been anchored and can now be properly discoverable.
- The "warning sign" in 8R-RTB was improperly placed and has been removed.
- The on board scanner will no longer put green dots on your ship.
- Wormholes can no longer be moved.
- It is no longer possible to lose a probe by moving it to a large distance outside the solarsystem
- The mysterious "???" deepspace complex sites will no longer show up when scanning.


**NPCs**


- Fixed an issue with Sleepers that were not properly draining cap from player ships.


**Corporation & Alliance**


- You can now use HTTPS in corporation/alliance links.
- Corporations that own outposts will no longer show as having an office there if they don't actually use an office slot.
- Fixed an issue where a notification was not sent out to the personnel manager when a pod pilot applied to the corporation.
- Attempting to add a bulletin to an alliance after having left now fails gracefully.
- When you create an alliance, your corporation is no longer listed as having accepted an application to the alliance.


**Agents & Missions**


- There are 40 new empire storyline encounter missions. Now with more space-shooty-fun-times!
- "The Maze" now has less cluttered acceleration gates.
- Changed mission expiration counter to be "...mission expires at" rather than "...mission expires in" to please the hamsters.
- Issues with missions being offered by agent Nakkito Ihadechi have been resolved.
- The warning message for declining missions will no longer read, "...within the next less than a minute..." It will now display the actual number of seconds left.
- Fixed a minor issue where starting research with a research agent could sometimes cause the research to begin at a negative value of some decimal points.
- Mission: Making Mountains of Molehills (5 of 10) should no longer send some pilots through Low-sec space.
- An agent's conversation window would sometimes have duplicate entries if you were in a fleet. This has been fixed as they are tired of repeating themselves.
- The "Terrorist at Large (2 of 4)" completion item now drops from the correct NPC.
- Level 5 missions should no longer send you to high-sec .
- Exploration site, "The Line", should no longer randomly change scenery.
- The mission "Giving Shelter" now gives the correct drop-off location in the agent briefing.
- The mission "Beefing Up" now has the correct item destination listed in its description.
- The site "Sansha Hub" will no longer prematurely end if you shoot the wrong thing.
- The missions "Cleaning House" and "Sansha on the Horizon" now have visual differences.
- For the mission "Nidupadian Yorak Eggs (1 of 2)," Keren's head now only drops once.
- Fixed issues with the four Empire's epic arc's quit behavior. When quitting a mission in one of the four empire epic arcs, you will now quit the arc itself, as intended. The "Blood-Stained Stars" arc, however, remains unchanged.
- Exploration site "Blood Raider Base" now has more sane travel distances.
- High-end ores have been removed from several sites and missions.
- Several mission briefings were not displaying properly in the journal, this has now been fixed.
- Friendly NPCs in mission "Clearing a Path" will no longer show as enemies.
- Fixed a small issue concerning locator agents and downtime.
- A full stop was missing in a tutorial. This has been corrected.
- Forgotten Outpost mission issues have been fixed.


**Miscellaneous**


- Dark Blood Colonel drops a Bhaalgorn BPC instead of the ship itself.
- You can no longer zoom infinitely into Spacial Phenomenons, which had caused a graphical glitch.
- Shooting with grouped weapons resulted in an inconsistency with damage messages if the simple damage notification setting was enabled. Both "hit" and "hits" were used. This has been fixed.
- The calculator now accepts numbers that have been copied via the clipboard.
- The "warp to location" option is only available to scan result only when the player is at warpable distance from that location.
- Filtering Options on the "Your First Days > Finding a corporation to join" has been bolded.
- Sensor strength of T3 ships fitted with dissolution sequencer subsystems were calculated incorrectly when racial sensor strength booster implants were present. This no longer happens.
- Ship configuration messages regarding fleet member usage needs has been updated on the Rorqual.
- Using Mining Foreman Links in fleets caused the mining lasers cycle timer to go out of sync. This has been fixed.
- Fixed the spelling of the "Ukomi Super Conductor."
- SBU and TCU attack notification messages now correctly display "Structure" instead of "Shields" in the correct circumstances.
- You can now login to game even while using the settings menu.
- Fixed an issue where the repair tool would crash if additional files existed in the installation directory.


**EVE Voice, Mail & Chat**


- In some rare cases there were discrepancies in how read mails were counted; this has been fixed.
- Chat channel names created using special characters will now create logs normally.


**Drones**


- Fixed an issue where a player could sometimes lose control of Fighter Bombers after they had been launched.
- "Augmented" drones are now properly classified as Faction rather than Tech II.
- Fixed an issue with assigned Fighter drones getting lost when the owner docks.
- The drone window will now update correctly when transferring from a ship´s drone bay to a ship based corporate hangar.
- Fixed a misleading message when attempting to launch drones in Triage mode.
- Updated super-carrier bonus descriptions to include regular drones.


**User Interface**


- A character that has been kicked from a corporation no longer shows up in the corporation chat member list until they relog. They are now immediately removed.
- The overview now updates correctly when a war declaration becomes active or goes inactive.
- The fitting window now updates the amount of CPU left when a module goes offline for any reason.
- The "Selected Item" window now updates when a selected drone is scooped.
- Planets and moons can no longer be targets of "look at" since they didn't really play nice with the camera drone.
- When viewing a route on the map, if the cursor was placed over any solar system, the route line disappeared. This has been fixed.
- Fixed an issue where right-clicking a probe's scan sphere made the resize graphic appear.
- The "Show Composition" window now shows the correct standings for a corporation.
- Extremely long lists of cyno arrays will now open in a separate window.
- Fixed the date search function within the audit log of secure containers. If you have the date selected and you press Enter you now get lines from that date.
- You can now unblock and allow a character in a chat channel without any issues if done at the same time.
- Energy Neutralizer range now shows up on the Tactical Overview.
- Adding multiple skills that resulted in the skill training queue to go over 24 hours resulted in an empty completion bar. You will now get an error message instead.
- When you press ALT + Enter after having clicked on account management on the login screen, it will no longer open the account management page.
- The notification tab will now correctly stop blinking after all notifications have been deleted.
- Fixed a defect which displayed "you are here" twice instead of once when you opened the star map.
- Fixed an issue which reversed the zoom mechanics when in planet mode.
- Skill points are no longer referred to as "Skillpoints".
- The "Sell this item" menu option is no longer shown for blueprints that have been used before.
- The Jukebox now handles playlist files differently. There may be some fallout for users who bypassed the client user interface when adding playlists. If you are having issues with playlists, you will need to remove them and add them using the Jukebox's UI.
- Fleet broadcast history no longer truncates text.
- Attempting to cancel a trade session that has already been completed now displays a notification: "Trade could not be canceled."
- You can no longer export fittings if you have no fittings saved.
- Fixed an issue that let you bookmark contracted ore.
- Deleted Fleet adverts no longer have the option to be deleted again.
- A spelling-mistake was corrected in the "Display and Graphics" tab.
- Newly created Jukebox playlists can no longer be named the same as the EVE default playlist title.
- Changing settings in the Market window with keyboard will now retain focus as expected.
- NPC bounty prize transaction description no longer lists location as "None" when you are in unknown space.
- The "Group of Cattle" description has been fixed.
- The sensor strength icon in the fitting window now updates correctly when ship is changed while the window is open.
- The Loyalty Point Store now has a welcome page.
- Accented characters can be used for label names (in both mail and contacts).
- Wreck windows will now retain position and stack correctly.
- Standings icon in the show info window now displays correctly for the full range available.
- Bookmarks in the In-game Browser now have a vertical scroll bar for multiple entries.
- Ship names with an ampersand will now display correctly in the character selection screen.
- The Planetary Launchpad user interface will now behave correctly when attempting to launch commodities while cloaked.
- The right-click menu is now available for characters in the mailing list management window.
- When opening the help window, the initial focus will now be on the search field.
- Fixed a small issue that could cause line spacing to go awry on the character selection screen.
- Fixed an issue where the Flatten/Un-Flatten buttons did not behave correctly on the map.
- Bookmark folders can now share a name with another item in the context menu without affecting the order of the menu items.
- Category columns now handle secondary sorting alphabetically when sorting items.
- Made small text fixes in regards to localization of in-space objects.
- Meta level sorting now counts no meta level as lower than 1. Also changed so that 0 meta level shows as empty.
- The Assets window now displays "Volume" in the correct column.
- Fixed a small issue that could cause the open contracts slot counter not to update itself.
- Fixed a minor issue regarding the "Export Overview" window.
- Slight polish in the "Browse Fittings" section has been applied.
- Minimizing and Maximizing a chat window will no longer clear its contents.
- You can now drag items from the "browse", "search", and "quickbar" lists ni the market. This allows you to drop them in chat ot make links.
- Added "Show Info" to your current system's contextual menu on the top left of the screen. (CSM)
- When comparing items they now have the correct context menus. (CSM)
- Several menu options have been moved around to more logical locations based on player feedback.
- Scan results that can be warped to are now represented by the correct bracket icon.
- Small tweaks have been made to the corporation voting window.
- Pilots will now be informed of the potential one-way move when moving items from the fitting window to a corporation hangar.
- Fixed an issue that caused "ghost" modules to appear as fitted when using the fitting service on capital ships.
- Small fixes have been made to stacking agent windows.
- The jukebox should now behave correctly when you expand and collapse it.
- Wrecks should now display correctly, whether or not they are empty.
- Calendar filters should now properly apply to the Upcoming Events & Latest Updates windows.
- Made small usability tweaks to how highlighting in sub-menus works.
- Stacked chat windows should now stay stacked upon login.
- The skill queue pop-up window message should now suppress itself correctly.
- Fixed a minor text overlap issue in the skills window.
- Fixed a rare random issue that could cause the local channel not to load.
- Minor fixes have been made to the pixel placement of corp logos in character information windows, they had the wrong aspect ratio.
- Made a small fix to how corp names were handled in the mail recipient line.
- CSPA charge is no longer charged to a player for closing the warning window.
- Drag and drop should now work properly for contacts.
- Scroll bars in the contracts UI should no longer have a large impact on client FPS.
- The scanner window now correctly remembers its size and position.
- Ship scanner no longer uses the old capacity UI element.
- CPU and Powergrid usage figures now have discernible decimal points.
- The corp bulletin edit field now wraps text as expected.
- Copying and pasting text from the character sheet no longer removes spaces.
- Locking pinned windows should now also work on windows that were already pinned.
- The Assets window now displays "Volume" in the correct column.
- Users can now filter the lockdown view in corporation assets.
- Fixed a tooltip display for the Industry tutorial missions.


**World Shaping**


- J140524 has moons labeled correctly now.


**Mac**


- Fixed an issue where the Mac client would crash when using CMD + TAB while running the client in full screen mode.
- Fixed an issue where Mac patches that where not distributed to the Web site caused an error when patching.


**Localized Clients**


- The Russian description of Gunslinger AX-1 has been changed to reflect actual attributes.
- The Russian description of the Nighthawk's rate of fire bonus has been fixed from 10% to 5%.
- The "kopieren" option in a blueprint context menu has been moved to the right place.
- Minor grammar fixes in the ship "show info" screen have been done for the German client.
- Updated the Nidhoggur description in the Russian client.
- Updated the description on the Sleipnir for the Russian client.
- The Cruise Missiles market group is now translated in Russian.
- Fixed the Russian description of the "Dysfunctional Solar Harvester."
- Localized the tab text of the carrier ship maintenance bay for the German client.
- Alliance logos should no longer get cut off in the login screen of the German client.
- Corrected the translation and text display in the Career Advancement window for the Russian localized client.


**API**


- Certificates will no longer refer to erroneous iconIDs in the static data dump.
- Error "This Yaml implementation does not support Dictionaries as Dictionary keys" no longer given for wallet reftype 10 or 37 (player input).
- The FacWarStats.xml.aspx API now returns the correct data.


**Graphics General**


- Textures on certain ships (such as the Utu and Adrestia) were turning green when graphic quality was set too low. These were remade and no longer turn green when a player zooms out.
- Dustfield particles have now been decreased in size, giving them less of a shard appearance while traveling in a fast ship.
- You are no longer prompted to reboot when turning shadows off or on.
- A memory leak that involved mining drones has now been plugged.
- Re-aligned a misplaced light on the Apotheosis model.
- Fixed issue where anti-aliasing changes would make UI labels disappear.


**CHANGES**

**Character Creator**


- All existing character portraits can be re-customized one time. You will not have to create your character from scratch and will be able to modify the existing portrait.


**API**


- The CharacterSheet.xml.aspx page now also contains Date of Birth and Security Status.
- The Research.xml.aspx API is no longer rate-limited, and will thus always return a result.


**Player Owned Structures, Outposts and Stations**


- It is no longer possible to use Electronic Warfare effects against starbase structures.
- Starbase structures should now be approximately as difficult to probe down as a T1 cruiser.
- You can now anchor a POS in a 0.4 system without faction standing.
- Ships which are jumping to a cynosural field located close to a starbase forcefield will now land at a slightly increased distance of up to 15km. This means that pilots will have a slightly increased travel time to get to safety within a starbase.


**Mac**


- The windowed/full screen mode setting is now accessible from the escape menu again.
- The Mac browser now caches all changes in the correct location.


**Corporation & Alliance**


- You can now hide rejected alliance applications.
- Corporate wallet management a bit less confusing! - Trader, junior accountant, accountant and divisional account access were changed regarding their corporate wallet access.
  - Divisional Roles give you access to take from the corporate wallet (which includes buying stuff) as well as seeing the balance of the division when it is selected.
  - Junior accountant: - Can view bills but cannot pay them.
    - Can view wallet divisions' balance.
    - Does not imply he has access to those divisions.
    - Can view shares.
  - Accountant: - Everything above plus:
    - Can pay the bills.
    - Able to view journal and transaction logs.
  - Trader: - Can view transaction logs.
    - Requires divisional access to do any actual trading.


**User Interface**


- Base attributes are no longer remappable.
- You can now easily access PLEX purchases from your character sheet.
- A confirmation message is now displayed when cancelling a market order and it can be suppressed like most warning messages.
- Small changes to right-click menu options for fitting have been made.
- Contract information windows can now be pinned like most other windows.


**EVE Gate**


- An "All Mail" tag for EVE mail will now provide a count of unread messages.
- EVE Gate contacts labels now have a count of members like the in-game client.
- Removing a broadcast with comments now needs confirmation.


**GENERAL**

**Miscellaneous**


- People and Places bookmarks can no longer be placed into other players' jettisoned cargo containers.
- The Krusual Tribe's name has been capitalized correctly.
- The criminal icon is now removed from local chat after the criminal aggression timer is elapsed.
- Now you can retry loading an ammo type you failed to load because you were cloaked.
- Boarding another ship does not result losing booster effects anymore.
- Hacking mini-profession naming inconsistencies have been fixed.
- It is no longer possible to activate siege-style modules while jumping.
- Career agents' window now plays nice even if the autopilot cannot find a route to the agents.
- When selling something to a NPC on behalf of your corporation, the entry is now colored correctly as you would expect from a corporation entry.
- When attempting to send a contact notification to a character that is set to not be contactable by anybody, you now get an appropriate error message.
- In some rare cases the ship was not removed correctly from space after logging off. This has been fixed.
- You can no longer attempt to cloak if you are not 2000 meters from the edge of a ship, rather than 2000 meters from the center of a ship.
- Character -> Alliance relationships are now correctly displayed in the Standings tab of the Alliance information window.
- When filtering recipients for mail, the paging is now consistent.
- The redundant "Capacity" attribute has been removed from drones.
- The volume slider no longer snaps to zero level on left-click.
- Capacitor drain effects will now correctly be displayed on the overview next to the origin of the effect.
- Spelling has been corrected in Combat Log Fleet messaging.
- Spelling has been corrected for Cynosural Suppression Strategic upgrade.
- Traffic advisory messages will no longer appear on autopilot routes.
- The mute button now behaves consistently when the jukebox window has been collapsed.
- Fixed a missing texture on a fan in Caldari Stations. Now you can see the air conditioning at work.
- Depth sorting was making pipes appear in a strange way. This was fixed so that depth sorting is better.
- Fixed the location of turrets on the Ishtar model.
- Fixed the portrait of a large collidable structure so that it doesn't appear so bright.
- Fixed white spots on models that were the results of ambient lights gone wrong.
- Fixed an issue where the icons for the Zealot and Omen Navy issue were interchanged.
- Camera drones have been tweaked so they can no longer zoom in too close to a ship and cause graphical glitches.
- The boss's capsule in "Cash flow for Capsuleer (10 of 10)" will no longer disappear when doing a "look at".
- A warning will now properly display when taking screenshots on a second monitor.
- The mouse cursor will no longer disappear when alt-tabbing to a full-screen client.
- Fixed the "set interest" function in the advance camera options.
- When taking a screen shot when using multiple monitors, it will no longer only capture a portion of the main screen.
- Fixed an issue where male character portraits were being shown without shirts. No shirt, no shoes, no service. CONCORD rules!
- Fixed an issue that was causing the client to have an ungraceful exit.
- Fixed an issue that caused shadow issues in-space.
- The Hulk and Covetor's shield hardener effect has been fixed.
- An unintended TV scan line effect in explosions has been removed.
- The Paladin has had an Alpha Map/Shader issue corrected.
- Fixed a graphic issue that was causing colonies in Planetary Interaction to flash when submitting changes.
- Zooming in and out will no longer make God-rays appear out of alignment.
- Fixed an issue where Hulk and Covetor had no in-game icon and models failed to load; this also prevented new ship models from loading.
- Fixed a camera issue where zoom level was lost after session change in pod.
- The EVE client will now remember the un-maximized window size after maximization.
- The quality of the texture on the Echelon ship has been improved.
- Locator Agents can no longer locate pilots in wormholes.
- A problem with mixed results from Sister Deep Space Scanner Probes and Core Scanner Probes have been fixed
- Hemorphite and Radiant Hemorphite now yield the correct amount of tritanium after refining.
- Fixed an issue in the Star Map > Animation >Enabling "Auto zoom to selection" option which caused a ship to lose camera focus when a player was docked in station.
- The Starmap > Systems I've visited view inconsistency has been fixed
- Atext issue in the description of PLEX has been corrected.
- Fighter bomber can now be scanned with combat scanner probes
- The distance to asteroid belts was not always updated correctly when warping in map view; this has been fixed
- The Scoop to Drone bay option has been fixed.


**Weapon Grouping**


- The way you group your modules has been changed. You now simply drag one module on to another module of the same type and meta level.
- You can now drag groups of modules on to another module or group of same type and meta level and they will merge.
- You can now peel one module out of a weapon group by shift dragging of the group.
- There is now a group all/ungroup all button in the ship UI that groups or ungroups all weapons.
- You can now group modules of the same type and meta level that have ammo in them.
- If the ammo is of the same type we even it out by moving some of it into your cargo hold.
- If the ammo is of different type we move all of it to cargo hold.
- You can now group modules that are damaged.
- Only the damage of the most heavily damaged module will be shown in the UI.


**Skills**


- The Drone Link Augmentor skill requirement was switched from Scout Drone Operation 4 to Combat Drone 3 in order to fix an underlying issue with bonuses.
