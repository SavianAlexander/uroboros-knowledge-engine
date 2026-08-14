# Patch Notes for Quantum Rise 1.0.2

- **Date**: 2008-11-27T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-quantum-rise-1.0.2-1
- **Tags**: #patch-notes

## Overview
Patch notes for Quantum Rise 1.0.2, released 27 November 2008   Table of Contents CRITICAL CHANGES FIXES CRITICAL Duration timers on modules can now be enabled and disabled. This will allow players who experience discomfort with duration timers the option of disabling the eff

---

**Patch notes for Quantum Rise 1.0.2, released 27 November 2008**

**Table of Contents**

[CRITICAL](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=177#critical)

[CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=177#changes)[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=177#fixes)

**CRITICAL**


- Duration timers on modules can now be enabled and disabled. This will allow players who experience discomfort with duration timers the option of disabling the effect completely.
- To address performance issues, we have made changes to the EVE Mail system in Quantum Rise 1.0.2. You will now be able to download only your first 1000 undeleted EVE Mails. In order to access additional Mails, you will need to delete mails currently in your inbox in order to make space. Additionally, EVE Mails sent by NPCs that are older than three months will be deleted. CONCORD EVE Mails are excluded from this deletion, however, they still fall under the 1000 EVE Mail limit. This change will be delayed by 24 hours and will come into effect on Thursday 04 December 2008.


**CHANGES**

**Need for Speed**


- The collision ball set up on various Large Collideable Objects, especially in mission sites, has been simplified to increase overall server performance.
- Performance warnings that were displayed within the server logs have been investigated and fixed. The result is that number of database calls has been reduced which results in lower latency overall. In simple terms this means less lag overall!


**Ships**


- All blockade runners (Crane, Prorator, Prowler and Viator) now have a 5 second reactivation time when using a covert ops cloaking device.
- The shield recharge time on the Orca has been changed to 2100 seconds
- The bonus for cloaking which is applied to blockade runners now correctly states "-98.5% to -99.25% bonus to cpu need of covert ops cloaks"


**Player Owned Structures, Stations and Outposts**


- Increased the capacity of the Large, X-large and Capital ship assembly arrays by 500m3. This will allow items other than the largest possible ships to be stored or assembled within them. This change permits for ships to be assembled whenever blueprints are held in the array.


**Graphics General**


- The cache settings for the Classic mode and Premium mode are now stored separately.


**Miscellaneous**


- Moving multiple items between containers is now working properly. You will no longer receive a message telling you the item is locked.


**FIXES**

**Ships**


- The correct armor repair bonus has been applied to the Occator. The ship will now give a 5% bonus to armor hit points repaired per level.


**Weapons & Ammunition**


- You can no longer move charges between grouped or ungrouped weapons within the fitting screen
- Attempting to group modules other than turrets or launchers will now display the message “You can only group turrets and launchers.”
- Loading ammunition into weapon groups will work properly in all cases. Attempting to load an odd amount of turret ammunition or missiles into a weapon group will split the ammunition over all grouped weapons and any odd number will not be used and will be returned to the hangar or cargo hold. For example, attempting to load 51 cruise missiles into a group of two Cruise Missile Launcher II’s will display as 25 charges and the additional missile will remain in your cargo or hangar.
- A pop up notification window will now appear for both weapon groups and single weapons when trying to load more ammunition than the turret, launcher or weapon group can hold.
- You can no longer drag and drop ammunition into grouped weapons on the fitting screen when a different type of ammunition is already fitted. Fitted charges will need to be removed before you drag and drop any new ammunition into the weapon group.
- Turret damage is now displayed correctly in the player logs. Wrecking and excellent hits will be shown in all of their pew pew glory.
- Players will no longer see phantom ammunition appear in their personal hangar after removing a loaded fitted turret to the Corporation hangar. All loaded ammunition will now be correctly stored in the Corporation hangar when the turret is unfitted there.
- The blueprint for Gurista Citadel Torpedoes has been removed. In addition, Gurista Torpedoes will no longer display the "I" after their name i.e. Gurista Doom Torpedo I will now display as Gurista Doom Torpedo.


**Skills**


- It is now possible to start skill training a level 0 skill from the Certificate Planner. This means that skills that have not been trained to Level 1, and were added to be trained at a later date, can now be started normally via the Certificate Planner.


**Player Owned Structures, Stations & Outposts**


- The order of modules within the production tab of player owned structures will no longer change when reloading or sorting fuel within the tabs. This fix will directly affect the listing of silos, reactors and moon harvesting arrays.
- Shooting at a station service with turret weapons will no longer generate an exception error once the station service is at 0%. This situation occurred when shooting a station service which was at 0% directly after downtime.
- An error message is no longer generated when attempting to move items into the Corporation hangar. When items were totalling in excess of 1000 items, this error message was being displayed.


**Market & Contracts**


- The “Item Name (exact)” filter is now working properly in the contracts window. If no contracts are found then the “No Contracts Found” message is properly displayed.


**Graphics General**


- Orbital maps in the solar system show info window now display correctly.
- Medals can now be created with characters that are not English i.e. Chinese, Cyrillic or Greek. Current medals which use these characters can be changed by submitting a petition to our Customer Support Team
- It will now be possible to create a medal using UNICODE characters in the medal name.
- Character portraits will now be captured correctly when using the "capture portrait" option. The image will be displayed in the My Documents>EVE>capture>portrait as one large picture rather than four passport sized pictures.
- Players will no longer see a ship giving off smartbomb effects after the smartbomb has been turned off. This was happening when a ship was destroyed by a smartbomb and the pod was still active


**Graphics Premium**


- The missing fourth turret on the Harpy has been replaced.


**User Interface**


- The character sheet will now list skills and attributes in the correct alphabetical order from A-Z in their respective windows.
- The price history tab in the market window now shows the correct price history. For example, two decimal places have been added so prices will list as 1.00M, 1.25M, and 1.50 M instead of 1M, 1M, and 1M.
- Fitting stacked modules from the Corporation hangar will no longer display an "Admin Lock Trace" warning.
- The Gremlin Javelin Rocket Blueprint has been fixed and now displays the Tech II icon.
- The information window displayed when using "show info" has been adjusted to the proper height. The minimum height had been increased to display medals, however, we have decreased the size once more but height will adjust automatically to display medals as necessary.
- Scroll bars will no longer appear when opening the character sheet.
- Jumping through a stargate with the mini map open (F11) will no longer cause the map to break. Your position will now display normally via the indicator on the map.
- Opening and closing the fitting window within a five second time frame will no longer generate an exception error.
- On selecting a locked object (in space or in overview), the 'selected item' icon remains the same. Players had been experiencing multiple icons when using selected item which were being seen in duplicate or triplicate.
- Character sheet will now show updated attributes and augmentations after a clone jump.
- The market buy and sell order window was slow if you were in a system that your autopilot was set to avoid. The performance has now been improved.
- Corporation listings under the station services icon will now display as intended. Corporation “Apply to Join” buttons will no longer overlap.
- The box art icon in Windows Vista's Games Explorer no longer says “Trinity”.


**EVE API and Static Data Dump**


- The missing column attribute for the certificates in the EVE API has been added.
- The certificate tables added to the Quantum Rise data dump will now display as intended. Unnecessary wide columns have been shortened.


**Miscellaneous**


- Fixed a server side warning that occurred when moving items.
- Reprocessing a mixture of mission loot and salvage will no longer cause an exception error to be thrown.
- The In-game Browser has been fixed and all appropriate buttons and tags are working as intended. Forms and form fields within tables now work properly.
- The "Open monitor" feature which was opened by shift+ctrl+alt+M has now been reinstated in a new form.
- A right click menu has been added when accessing cargo containers in an inactive ship’s cargo hold.
- Certificates and certificate relationships have been added to the bulk data files.
- The Basic and Standard Common Ore Refiner certificates no longer display a blank window when opened and the number of prerequisite skills for them has been reduced from 7 to 6.
- Space junk clean up is now running during downtime but will not delete anything it is not supposed to.


**Exploit Fixes**


- Several exploits have been fixed making New Eden a better place for everyone.
