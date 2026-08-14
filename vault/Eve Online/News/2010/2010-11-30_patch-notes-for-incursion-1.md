# Patch Notes for Incursion

- **Date**: 2010-11-30T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incursion-1
- **Tags**: #patch-notes

## Overview
Patch Notes for Incursion Released Tuesday, November 30, 2010 Table of Contents FEATURES CHANGES FIXES FEATURES Ships A dedicated salvaging ship, the Noctis, has been added to EVE Online. No longer will you have to use ships less suited for this line of work. The Noctis is a salva

---

**Patch Notes for Incursion**

Released Tuesday, November 30, 2010

Table of Contents[FEATURES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=214#features)[CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=214#changes)[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=214#fixes)

**FEATURES**

**Ships**


- A dedicated salvaging ship, the Noctis, has been added to EVE Online. No longer will you have to use ships less suited for this line of work. The Noctis is a salvager’s wet dream and comes with some specialized bonuses, a large cargo hold and eight high slots for salvagers and tractor beams. Please check out [this Dev Blog](//www.eveonline.com/devblog.asp?a=blog&bid=797) for more information and some nice images.
- The statistics for the Noctis are as follows: - Slot layout – 8 high, 2 mid, 3 low
  - Powergrid – 250 MW
  - CPU – 300
  - Base speed – 155 m/s
  - Cargo capacity – 1,460 m3
  - Rig slots/Calibration – 3/400
  - Shield/Armor/Hull hit points – 1700 hp/2200 hp/3200 hp
  - ORE Industrial skill bonus: 5% bonus to Tractor Beam and Salvager cycle time and 60% bonus to Tractor Beam range and velocity per level
- Blueprint Originals for the Noctis can now be purchased from Outer Ring Excavations stations.
- The new ORE Industrial skill book, required to pilot the Noctis, can now be purchased from school stations everywhere.


**CHANGES**

**Ships**


- The Hawk assault frigate has had its bonus to kinetic missile damage changed from 5% to 10%. It also has an additional 2MW added to its powergrid.


**Drones**


- Fighter Bombers used by Super Carriers have been changed: - They do much less damage to sub-capital class ships now.
  - They will also contribute much less lag to future fleet fights but they were previously making the servers cry.


**Weapons & Ammunition**


- Rockets have had an explosion velocity boost. It means they will inflict more damage on faster moving targets whilst also gaining a straight damage boost through changes to rocket damage and rocket launcher rate of fire.
- Quake has had its velocity and capacitor recharge penalties removed.
- Hail has had its capacitor recharge penalty removed, its tracing speed penalty reduced and its damage boosted.
- Gleam has had its shield hitpoint and signature radius penalties removed.
- Conflagration has had its tracking speed penalty reduced and its damage boosted.
- Javelin has had its velocity penalty removed.
- Void has had its tracking penalty reduced and its damage increased.


**Need for speed**


- In order to facilitate fleet fights, network timeout values have been increased substantially from eight minutes. This will allow users to successfully jump and/or log into extremely loaded solar systems where the client will need to wait a very long time to complete. The players will also receive more informative messages under these extreme circumstances.
- Repeating modules will no longer get into a “stuck” state, where they cannot be switched off.
- Improvements to module activation and reload responsiveness have been made.
- Decisions about who should receive damage notifications were optimized.
- Jumping through a stargate will now create less server load.
- Compile-time constant handling was improved to give better runtime performance: As a result of replacing certain data look-ups with fixed constants, both client and server should be able to run slightly faster.
- Fixed an issue in which a client receiving out of order packets would fail to load grid when jumping into a system.
- A large amount of damage and effects states were being recalculated for every observer during fleet warps and mass jumps. This process is now much more efficient.


**Market & Contracts**


- The Ships section of the market has been reorganized and is now primarily sorted by hull class. In addition, all faction and special release ships have been added to the market so you can now trade them there in addition to contracts.
- It is no longer possible to create Loan contracts. Furthermore, existing in-progress loan contracts will become invalid in January 2011 as a part of a major Contracts refactoring. If you have a loan contract in progress you are encouraged to complete it before the end of this year to avoid any possible inconvenience.


**Graphics**


- The EVE client is now resizable in Windowed mode, allowing the players to stretch their client over several monitors. Now EVE Online is much more beautiful in ultra-widescreen resolutions. This feature is not available in the Mac Client.
- There is a new version of Windowed Mode called Fixed Window. It is similar to the regular Windowed Mode but lacks any title bars, frames or borders. Fixed Window is not available in the Mac client
- A new option, “Horizontal offset” has been added to the settings menu. It allows the player to have all menus on one monitor and focus on his ship in another monitor.
- EVE now supports anti-aliasing. The beauty of virtual space has never been more… beautiful. Anti-aliasing is unfortunately disabled on the Mac client at the moment. We are working hard to get the anti-aliasing feature enabled in our Mac client in a future release.
- Fighter Bombers now have a new missile effect, which looks awesome and doesn’t make the servers beg for mercy at the same time.
- Microwarpdrives now have their own brand new icon.


**Mac**


- Enabled Alt+F4 capabilities, allowing users to activate modules with this keybinding.


**Miscellaneous**


- A “Volume” column has been added to the hangar view by default; “Category”, “Meta Level” and “Tech Level” have been added as optional columns. Individual columns now can be toggled on and off through the right click menu.
- The order of options in right click menus has been changed and grouped to make it more consistent. This means that the more dangerous options like ‘Trash’ appear towards the bottom of the menus with more useful options such as ‘Show Info’ appearing at the top.
- You can now move items and ships to their respective hangars by dropping them on the corresponding icon in Neocom.
- Deadspace, faction, officer, and storyline items now have an overlay icon like the Tech II and III items.
- Probes can now be added to the overview.
- Corporation assets can now be filtered according to region or number of jumps.
- Players with Starbase Defense Operator roles will now receive notifications about control towers under attack.
- You can now rename ships in your hangar without making them active.
- When the camera is offset, the user interface can follow. Under the Camera Offset slider there is a checkbox that will center the UI elements wherever the camera is focused.


**FIXES**

**User Interface**


- Item sorting now works correctly even in cases where some columns have been removed.
- Tooltips no longer stay visible during drag-and-drop.
- Text will now be correctly highlighted in storyline mission briefings.
- You can now receive client updates through the login window without actually logging in. This means you will be prompted about a client update as soon as you boot your client rather than waiting to input your username and password.
- Dragging an item into the chat window no longer causes the window to lose focus.
- The right-click menu will now be more responsive when working in hangars with very high item counts.
- There will no longer be any icon overlap in the assets window.
- An issue causing the F11 Map browser to snap abnormally has been resolved.


**EVE Voice, Mail & Chat**


- White spaces on notes are now counted as characters and are saved properly.
- An issue has been fixed which was causing the EVE mail window to experience an excessive load time when first accessing it in a new session.


**EVE Gate**


- Mails will no longer throw an error if a ship or character is linked in it.


**Localized Clients**


- The buttons to install or uninstall client updates are now translated and are present in their proper locations in the Russian and German clients.


**EVE API**


- Inconsistent formatting of element and rowset names in mail calls has been fixed.
- Having an empty inbox will no longer cause errors in mail calls.
- Mail messages no longer show their read/unread status as it did not update properly from the different methods of reading your mail and caused confusion.
- Quantities of -1 will no longer show up for unstacked items.
- New corporations are no longer seen as a NPC corp by the API.
- The MailMessages API no longer return the Read bit, as it isn’t guaranteed to be correct.
- The toListIDs flag on MailMessages now returns an empty string rather than 0, if it wasn’t sent to a mailing list, as this is more consistent.
- The toListIDs flag has been renamed to toListID, as you can only send a mail to 1 mailing list at a time.
- The API is now aware of all skill types, not only published ones. No calls should fail for characters who've somehow gotten unpublished skills injected.
- Science and Industry and Container Logs now returns the correct quantities.


**Mac**


- Fixed a Z-buffer issue that caused flickering on ATi cards. This was fixed for the R600 previously and now covers R800 as well.


**Miscellaneous**


- Wrecks will no longer jump around in space, when a tractor beam is activated on them.
- Orbiting and colliding NPCs and player ships are no longer rendered in wrong location by the client compared to the server.
- Ships are now coming out of warp smoother, without “rubber-banding”.
