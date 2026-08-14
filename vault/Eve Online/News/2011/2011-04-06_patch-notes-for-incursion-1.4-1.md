# Patch Notes for Incursion 1.4

- **Date**: 2011-04-06T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incursion-1.4-1
- **Tags**: #patch-notes

## Overview
Patch notes for Incursion 1.4, released April 6, 2011 CHANGES EVE Gate Improved security on EVE Gate including an additional layer of protection to the EVE Gate logon system. Streamlined the character selection process so that you are presented with the character selection screen le

---

**Patch notes for Incursion 1.4, released April 6, 2011**

**CHANGES**

**EVE Gate**


- Improved security on EVE Gate including an additional layer of protection to the EVE Gate logon system.
- Streamlined the character selection process so that you are presented with the character selection screen less often.


**Image server**


- Added support for fetching inventory type icons.
- Added support for ship and drone renders.
- Optimized various parts of the system so that we can send some of the hamsters to help elsewhere instead.


**Contracts**


- The new search function for contracts has left beta and the old search has been removed.
- You can see CCP Atlas' dev blog for more information: [//www.eveonline.com/devblog.asp?a=blog&bid=833](//www.eveonline.com/devblog.asp?a=blog&bid=833).


**API**


- Raising the maximum rowCount of journal transaction walker to 2560.
- Changing the Market Transaction calls to behave just like the Journal Transactions.


**Ships**


- The Flycatchers' bonus to Light Missile damage reduction factor per level has been changed to a missile explosion velocity bonus per level.
- The command center hold of the Primae was increased to 2000 m3 allowing transportation of two command centers at the same time.


**Fleets**


- When you create a fleet, you're now automatically made squad commander by default.
- Loot logging is now enabled on all fleets by default. You can still steal stuff while in a fleet, but everyone will know!


**Need for Speed**


- Starbases in low-security space that have the 'Attack if other security status is dropping' setting active will now choose their targets in a way that is better for the server CPU.
- Warping within the same (heavily-populated) grid is now handled more efficiently. Additionally, warping on to a very heavily loaded grid from elsewhere is now handled more efficiently.
- The server was previously sending the damage state of in-flight missiles to clients. As clients cannot lock missiles, this no longer happens.
- The way that damage updates are distributed to fleet-mates has been improved.


**Missions & Complexes**


- Team Commie Pinkos is gradually releasing new DED Complexes in our efforts to close the content gaps in EVE. Seven new complexes are now available in the game; more information is available in a dev blog by CCP Big Dumb Object: [//www.eveonline.com/devblog.asp?a=blog&bid=861](//www.eveonline.com/devblog.asp?a=blog&bid=861)


**NPCs**


- All NPCs that use jamming have been streamlined in functionality and you can now fit your ship to counteract them.


**Corporation & Alliance**


- Corporations can now have up to 100 ship fittings stored on the server.


**Player Owned Structures, Outposts and Stations**


- The type of anomalies spawned by sovereignty upgrades now will be affected by the security status of the system. See CCP Greyscale's blog ([//www.eveonline.com/devblog.asp?a=blog&bid=883](//www.eveonline.com/devblog.asp?a=blog&bid=883)) for more information. Please note that these changes will take effect within the first week after deployment and will not all be updated immediately after the patch is deployed.


**User Interface**


- The calculated security status of solar systems will now be displayed as negative where appropriate (See: Player Owned Structures, Outposts and Stations).
- 'Show Contracts' option is now available in the menu of non-NPC corporation info.
- Player portraits are visible in the following user interface windows in which players interact: Trade, Give Money, Chat Invite and Selected Object in space.
- The width of the 'runs' boxes in Science & Industry has been increased to account for the production of items in larger batches, such as ammo.
- Player-owned stations now appear like NPC stations in the UI with their location displayed as a prefix before the Station name.
- Individual bookmarks may now be permanently removed via the right-click menu while flying in space.
- The column with the image of the fleet boss will now contain standings as well, instead of having it in a separate column.
- Pilots now have multiple default overviews to choose from: All, Drones, General, Loot, Mining, PvP, WarpTo
- Now you can select all items, click 'repackage' and the process will simply skip those items on which the operation cannot be performed without stopping the repackaging process.
- Character portraits in 'Show Info' may now be viewed in a separate window at a higher resolution.
- When using the Autopilot, Waypoints will display as separate icons so pilots can tell them apart from regular jumps.
- An Incursion chat channel has been added that can be accessed from anywhere in the universe. This channel can be used to share information gathered about Incursions from outside of affected constellations.
- Players can now store 50 fittings on the server, making them accessible from any computer. Additional fittings may be saved locally into an XML file.


**Character Creation**


- Code optimization has increased overall performance in the character creator.
- Characters now have the option to add vicious hero scars and burns.
- A collection of piercings, studs and facial modifications have been added.
- Represent your bloodline in ink with new and classic tattoo designs from the EVE universe.
- Added a new pair of sunglasses.
- Added male and female tank tops.
- There is now a free station service to allow you to re-customize your appearance from any station.


**Mac**


- Updated the icons for client and patches.


**Miscellaneous**


- Capsuleers no longer have to get into their un-piloted ships in order to strip the fittings. A powerful imaginary electromagnet now removes fittings remotely via the right-click menu of the ship.
- Career and Tutorial missions now have a massively increased duration and you will not lose standings for quitting, declining or timing out.


**FIXES**

**EVE Gate**


- The main EVE banner located on the EVE Gate homepage now displays correctly in the in-game browser.
- Players can now edit a contact's standings while looking at their broadcasts.
- The EVE Voice widget can now be used by players running non-English versions of Windows 7.
- Netbook users can now reach the buttons on the bottom of the popup in the calendar event window.
- The unread message counter for "All mail" displays the correct number and will not count the same message multiple times anymore.
- The mail editor can no longer be re-sized horizontally.
- The right side of the broadcast page of one of your contacts only displays his/her contact, and not yours.
- The character, corp and alliance information on the profiles now displays correctly in IE8.
- Missing localization in German and Russian has now been added when viewing the "latest forum posts" section of a character profile.
- Players can now exercise their communication manager roles during their first visit on EVE Gate.
- The line stating the time of the last post on a user's broadcast page, if that particular user has never posted before, has now been removed.


**Image server**


- Invalid URLs now result in a 404 Not Found page instead of a yellow screen of fail.
- Results providing broken images have been reduced significantly.
- Missing NPC corp logos were updated to the image server.


**Aggression**


- Aiding someone who is currently in a war, will now flag the aider to everyone the recipient is at war with which now includes alliance wars.


**API**


- Renaming Character Sheet element "unpublished" to "published" to conform with the Skill Tree API. All skill rows should contain all elements now.
- Fixed an error with displaying the alliance of characters in new player corporations.
- Fixed an issue with the Wallet Journal walker marking itself as consumed prematurely.
- Walker should now always allow for a full month of data and will just display the "first page" in the history if it receives weird input.


**User Interface**


- Info windows for planetary interaction structures no longer open on releasing the mouse button while hovering over them; this was causing involuntary pop-ups when users dragged the planet view around.
- Planetary interaction construction interface can no longer be tricked into believing you have placed a command center by jettisoning it into space.
- It is no longer possible to assign shortcuts to keys already used by the default schema, for example you can no longer assign F1 to "Open Calculator".
- Website trust request in IGB now displays the URL where the request originated from correctly.
- The killmail information window will now retain size and positioning after being closed and re-opened.
- When trading, holding Shift will once again split the stack after dragging into the trade window.
- Inactive probes can now be destroyed via the Scanner window.
- With a destination selected, you can clearly see the security status of the next system on route, even in planetary interaction mode.
- The Sovereignty dashboard was found to be only updating current system information intermittently. The dashboard now updates immediately when pilots move between systems.
- Clone jumping with the corp hangar open would cause the corp hangar window to become unable to close, this no longer happens.
- Players are now notified when they attempt to move more than the allowed number of bookmarks to their cargo.
- A conflict in the Sovereignty dashboard that occurred on viewing Sovereignty via the Star Map has now been resolved.
- An issue with re-sizing the scanner window has been fixed.
- Using the 'Buy this' option in the Market was opening in Advanced mode if you had Advanced toggled for placing buy orders. This made no sense so now 'Buy this' always opens in simple mode.
- Redundant decimal points visible after the percentage stats for the ship hitpoint readout have been removed.
- The delay in switching to a large channel has been decreased.
- When filtering the star map by Sovereignty, the data now loads faster.
- Players with over 300 contacts with good standings can now create standings-based fleet adverts.
- The system name is no longer repeated when retrieving the password for a container.
- The wallet will no longer get stuck if you are given roles while having a corporate wallet open.
- The description for the Minmatar Republic now refers to the star cluster rather than world.
- Neutral contacts are now given a colortag in default overview settings.
- The Certificate planner now updates on application of unallocated skillpoints.
- The Neocom portrait is no longer obscured by the name bar.
- In-game keyboard shortcuts are now inactive in the Character Creator.
- All needed confirmation windows are now being displayed, when unfitting a grouped weapon directly into a corp hangar.


**Science and Industry**


- It is now possible, once again, to invent a Large Core Defence Field Extender II.


**NPCs**


- The loot from Terrorist Overlord Inzi Kika typically contained small hybrid ammo. Inzi Kika has ceased moonlighting as a hauler of frigate ammunition and now carries large hybrid ammo.
- Drones set to 'aggressive' were getting confused and not engaging Sansha ships. Drones have now realized that Sansha are not friendly and engage accordingly.


**Modules**


- Mobile warp disruptors will now show up on probe results as intended; previously they did not have sensor strengths so could not be found. Small/Medium/Large disruptors are now approximately as easy to find as Frigates/Cruisers/Battleships respectively.
- Several modules like tracking disruptors no longer reset their cycle, when the target explodes.
- An unneeded attribute has been removed from the Micro Auxiliary Power Core I and its variants.


**Weapons & Ammunition**


- Faction FoF missiles have now appropriate faction tags.


**Ships**


- The Widow will now properly bonus the ladar sensor strength on ECM Burst modules.
- It is now again possible to fit a subsystem to a tech3 ship by right-clicking the module and selecting "fit to active ship".


**Drones**


- A correct message is now displayed when not all drones are selected to engage a target.


**Character Creator**


- Amarr robe has been improved.
- Clothing changes are now much smoother.
- The neck can now be sculpted from any angle.
- The location of the avatar is unchanged when exiting and re-entering the Portrait screen.
- The position of the avatar is unchanged by zooming in and out in the Portrait screen
- You can no longer create a Portrait without eyes being visible within the image
- Each Race-Bloodline-Gender combination now has the appropriate colors available for hair and eyebrow combinations.
- An issue with removing the female bra within character creation has been fixed, unfortunately.


**Market & Contracts**


- The creation time for auctions no longer shows current server time.
- An issue that caused half-translated message boxes upon modifying market orders has been fixed.
- The default range for searching contracts is now Current Region.
- When searching for a specific blueprint type, the filter now works correctly.
- When viewing all contracts assigned to you from the start page, the price filters are now cleared correctly.
- Visibility level 5 now works for 'region' range setting rather than just '40 jumps'.


**Corporation & Alliance**


- When paying dividends to corporation members, the notification now correctly specifies that the dividend was paid to members rather than shareholders.
- You'll no longer see old bulletins when you switch corporation.
- Viewing corporation member's hangars did not show changes to the inventory until a session change occurred. You are now able to refresh the view of the hangar by using the right-click menu or by re-opening the window.
- Previously, after dragging items onto corporation member's item hangars and refreshing the view the dragged items appeared to have vanished. This has now been resolved.


**Wormholes**


- Ghost wormholes that would show up as type 'Unknown' in scan results and have nothing but empty space when warping there have now been eliminated.


**World Shaping**


- The Ashab gate in Amarr has been moved to a more convenient location for people undocking from stations in the system.


**Mac**


- Fixed an issue where switching between fullscreen and windowed modes (without changing resolution) wasn't having any effect.


**Localization (German)**


- The consistency of the Welcome pages has been improved. The text has been reviewed for linguistic issues.
- Several changes for style and consistency have been made throughout the game, especially on the NeoCom and station services.
- EVE Gate will now remember the language settings when logging out.


**Localization (Russian)**


- Numerous changes for style and consistency have been made throughout the game, especially items’ & missions’ descriptions; messages, categories and map UI.
- Russian abbreviation for "billion" has been changed.
- Remaining obsolete translations of the term "cruise missile" have been brought in line with the revised translation.
- EVE Gate will now remember the language settings when logging out.
- Correct Russian translations are now being used for various types of implants.


**Player Owned Structures, Outposts and Stations**


- Installing upgrades will now correctly modify your next cycle's bill.
- Installing infrastructure upgrades without a daily upkeep will no longer generate empty notifications.
- Previously, if a player left a ship within a password protected forcefield occasionally the ship was driven out of the force field upon log in. This has been resolved.
- It is now possible to build jump freighter in fully upgraded Amarr Factory Outposts.


**EVE Voice, Mail & Chat**


- Text and editing issues with Welcome Mail for Mailing Lists no longer occur.


**Miscellaneous**


- After boarding a ship that had been ejected into space from another ship's Maintenance Bay, pilots would sometimes be unable to dock at a station. This has now been fixed and you can now dock in peace.
- The calculated damage on kill mails is now more accurate.
