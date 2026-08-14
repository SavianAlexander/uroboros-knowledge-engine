# Patch Notes for Incursion 1.1.2

- **Date**: 2011-01-27T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incursion-1.1.2-1
- **Tags**: #patch-notes

## Overview
Incursion 1.1.2 Patch Notes To be deployed on January 27, 2011 Table of Contents FIXES CHANGES Client Update FIXES Character Creation and New Player Experience Some eyeliners were not displaying the correct color. This has now been fixed. Characters who were incorrectly rendered wi

---

**Incursion 1.1.2 Patch Notes**

To be deployed on January 27, 2011

Table of Contents[FIXES](#fixes)[CHANGES](#changes)[Client Update](#clientupdate)

**FIXES**

**Character Creation and New Player Experience**


- Some eyeliners were not displaying the correct color. This has now been fixed. Characters who were incorrectly rendered with white eyeliner when they chose black will have their characters automatically corrected and rerendered.
- Amarr hoods should now save in the proper state when finalizing a character, and should only ever appear on Amarr robes. Characters that were wearing the hood without wearing the robe will have their characters automatically corrected and rerendered.


**Incursions?**


- Based on feedback from the community, we have reduced the rate at which Sansha's regain control of the constellations.
- An issue where the journal was not updating properly has been fixed.
- Deepspace complex beacons have been changed and will disappear when a deepspace complex is completed. This should result in fewer empty deepspace complexes.


**Mac**


- A number of crash issues introduced with Incursion 1.1.1 have been resolved.
- An issue where the in-game browser on the Mac client was truncating HTTP header values to a single letter has been fixed.
- Adding a Web site to the trusted sites list will now work correctly in the in-game browser.


**Exploration & Deadspace**


- Wormholes will no longer bump you when you are on top of them. Minds out of the gutter, capsuleers!


**Market & Contracts**


- The Daytrading skill now works correctly.


**Planetary Interaction**


- Products from ECUs were appearing as too small in the ECU graph. This has been resolved.
- An issue that prevented Extractor Control Unit heads from being placed has been fixed.
- Some previously placed Extractor Control Unit routes were disappearing. This happened when newly created routes exceeded the current route's bandwidth. This has been resolved.


**Graphics**


- The Retriever ship has been updated so that it no longer appears to be gold in color. CONCORD is greatly relieved, knowing that there will be a reduction in bad dog jokes.
- The Mackinaw ship has been updated so that it no longer appears red in color.


**User Interface**


- Non-agent NPCs will now have portraits.
- Pilots now have two options in the overview filter: - No Standing and Neutral Standing. - When "No Standing" is unchecked, only pilots who are in your contact list will appear in your overview.
    - When "Neutral Standing" is unchecked, pilots who are in your contacts as "Neutral" will no longer appear in the overview.
- The contract window will no longer become unresponsive after trying to delete a non-outstanding contract.


**EVE Gate**


- It's no longer possible to create labels with reserved names that have a white-space around them.
- Alliance public profiles will now list all corporations within in the alliance.
- EVE Gate now allows the payment of CSPA charges. Your mail will now be delivered.


**API**


- The cache timer for Wallet Journal calls has been lowered to 27 minutes.
- Legacy support for beforeRefID has been added.
- A maximum date range has been added. Players will only be able to query historical data up to one month previously.
- An issue where the Scotty, the docking manager, would refuse you access to your character sheet. Scotty has been put in his place and will now give it all he's got.
- Passing a 64-bit integer to /eve/CharacterName.xml.aspx no longer causes Scotty, the docking manager, to panic.
- The MemberSecurity data is now formatted according to the rowset style, making it consistent with other API calls.
- Fixed an issue with the API not returning name information on deleted corporationIDs and characterIDs


**CHANGES**

**Character Creation and New Player Experience**


- A history slider function has been added to the character creator. This allows players to undo and redo changes they have made when designing their character.
- Users can no longer proceed to the Portrait screen without equipping a shirt beforehand.


**User Interface**


- The Dock option is now third - under approach and orbit - in the right-click drop down menu.


**General**


- A fix to reduce desync issues caused by the EVE Online physics engine has been implemented.


**Incursion 1.1.2 Client Update 1**

To be deployed on January 28, 2011

**FIXES**


- Fixed an issue where "pilot has no standing" was missing from the background color options.
- Changed the Sansha NPC groups to automatically appear on the overview.
- The option to recreate a character portrait will be available to those who have already created their portrait.


**Incursion 1.1.2 Client Update 2**

To be deployed on February 3, 2011

**FIXES**

**User Interface**


- An extra, invisible tab on the login screen has been removed.
- When using combat commands, items that leave the grid are now correctly removed from the overview when the combat shortcut is released.
- The Selected Item window now opens in the correct size and respects the minimum size if resized.


**Game Mechanics**


- Control Towers will no longer unanchor nearby Mobile Warp Disruptors during server start-up. If a player anchors the disruptor before downtime, the tower will now respect this.
- Fleet bonuses were sometimes not (re-)applied after undocking or jumping. This has been fixed.
- On completing an Incursion players were experiencing unexpected lag. Changes have been made to mitigate this.


**Character Creator**


- Some characters had hoods without wearing a robe, this was deemed illegal by Amarrian authorities and all such images are in the process of being updated.
- Sleepy characters will now have their eyes propped open.


**EVE API**


- The layout of the MemberSecurity API is correct once again.


**Incursion 1.1.2 hotfix**

To be deployed on February 10, 2011

**FIXES**


- When grouping modules and leaving your ship, the modules could sometimes lose their grouping. This has now been fixed.
- Damage notifications for bombs are being sent again.
