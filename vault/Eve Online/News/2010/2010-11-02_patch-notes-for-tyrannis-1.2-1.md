# Patch Notes for Tyrannis 1.2

- **Date**: 2010-11-02T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-tyrannis-1.2-1
- **Tags**: #patch-notes

## Overview
Patch notes for Tyrannis 1.2 Deployed Tuesday, November 2, 2010 Features We have changed the inventory system to use 64-bit numbers. Please read CCP Cerber Cattus’s Dev Blog for more information about this change. A number of changes and improvements have been made to the API:

---

**Patch notes for Tyrannis 1.2**

Deployed Tuesday, November 2, 2010

**Features**


- We have changed the inventory system to use 64-bit numbers. Please read [CCP Cerber Cattus’s Dev Blog](//www.eveonline.com/devblog.asp?a=blog&bid=813) for more information about this change.
- A number of changes and improvements have been made to the API: - Created a new API page that returns the body of mails.
  - Created a new API page that returns the current status of your account.
  - Created a new API page that returns character information as found in the Show Info window.
  - The Factional Warfare Systems API now returns correct data.
  - The Standings page now only reports standings, and not contacts.
  - The Character Sheet now returns the ancestry and date of birth of a character.
  - Some fields now return 64bit values. Please refer to the second volume of the API blog series for more information.
  - Most pages will now return the cached data rather than an error if you query it too soon.
  - A lot of cachedUntil fields has been fixed.
- See this [Dev](//www.eveonline.com/devblog.asp?a=blog&bid=796) [Blog](//www.eveonline.com/devblog.asp?a=blog&bid=798) [trilogy](//www.eveonline.com/devblog.asp?a=blog&bid=801) for more information on these changes.


**FIXES**

**API**


- Group and Category IDs in the Static Data Dump are now 32-bit.


**Weapons & Ammunition**


- Module icons would sometimes overlap the visible item slots after grouping weapons. This has been fixed.


**User Interface**


- An issue where the corporation logo creator would sometimes be placed off center has been fixed.


**In addition, this patch includes the following fixes which were previously released in the Tyrannis 1.1 optional patches:**

**Skills**


- When moving skills into the skill queue, there was no skill book icon, just a blank rectangle. This has been fixed.


**Planetary Interaction**


- All pending structure placements in Planetary Interaction will now correctly display as yellow icons.
- Scrolling through the processor pin schematic window will no longer affect the planet mode zoom.
- Fixed an issue where exporting via launchpad occasionally failed.


**Agents & Missions**


- The Loyalty Point store now displays the correct number of required items.


**Starbases, Outposts & Stations**


- The control tower management window now shows "Put online" and "Change type" instead of "Put" and "Change".
- In the sovereignty dashboard, only the first word in the location name was displayed, this has been fixed and the full name is now displayed.


**User Interface**


- When opening the scanner the alert sound is no longer played.
- Windows will now retain their correct size when you open and close them.
- You can now view member hangars through the corporate hangar as intended.
- Hiding passive modules in the HUD no longer hides all modules.
- In the sovereignty dashboard only the first word in the location name was displayed. This has been fixed and the full name is shown correctly.
- Resolved an issue where corporations who were part of an alliance had blue alliance stars against corporation members. The correct green star will show for corporation members.
- If you moved a window half way off the screen it would bounce back into full view when you opened a new window. This has been fixed.
- Certifications now show the level required for component skills.
- Chat channels will no longer reset to the default positions every time the client is restarted.
- Chat channel logs now show the channel name again as originally intended.
- The password for a chat channel is now shown correctly when editing the details of a channel.
- Fixed an issue where errors would be created while right clicking multiple probes.
- When using CTRL + Up to select previous chat submissions will now place the cursor at the end of the line.
- The move items sound effect now plays correctly.
- The welcome screen for trial accounts is now bigger and better.
- Fixed an issue where stacking chat channels created client errors.
- Message boxes are less transparent so the text is easier to read.
- The alert sound is no longer played when opening the scanner.
- The sound effect is now correctly played when activating modules.
- The People & Places window no longer jumps to the front over other windows when jumping/docking.
- Windows will now retain their size when you open and close them.
- Pinned windows are again persistent after re-logging or closing the windows.
- Snapped windows stay put after closing another snapped window.
- Pinned windows are again persistent after re-logging or closing the windows.
- A stacked window will now open in the appropriate location after closing and reopening.
- The icons on the fitting screen are now sized correctly.
- The snap indicators will now help you again when resizing the window, just like they used to.
- Cargo scanner window size and position will no longer change when you re-scan.
- Fixed an issue where the chat channel window order was rearranged during a session change.
- Tech 3 blueprints now render correctly.
- The labels in the Fitting Preview are now shown correctly.
- The cursor is now located correctly when changing market orders.
- Fixed an issue where the corporation logo creator was off center.
- Partially trained skills now display correctly in the character sheet.
- Copy and paste will now copy the correct portion of text in the chat window.
- Fixed an issue where dragging the certificate planner over a stack of windows created exceptions.
- Wreck windows will no longer open in the center of the screen, but in the same location as the last moved window, or any stack of wrecks.
- The Drones window now renders the action labels correctly.
- Amount/Price columns did not auto-size correctly. They now size themselves correctly so that you can see the full text.
- The Federal Intelligence Office requested their logo back. We had just had our morning coffee, and gave them their logo back.
- It is now possible to resize pinned windows.
- Itemized bookmarks can now be dragged from a location, such as a cargo hold, straight into a bookmark folder.
- The overview is now forced to clean itself after you have jumped. It didn't before, which was messy.
- When you get an expedition you will now get a message box stating so.
- Containers now remember their position when you close them.
- Character portraits no longer render in white while waiting for the portrait to download.
- The Assets window will no longer jump to the front when you jump, dock or otherwise change state.
- Triangles for ascending/descending sort order are now rendered in a standard format.
- Icons on the fitting screen are now sized correctly.
- A rare scenario that would remove all brackets in space has been fixed.
- The agent conversation window will now open in the middle of the screen as it should.
- The client will now correctly remember the position of all stacked windows.
- When creating weapon groups ghost icons were sometimes left floating in space. These have been cleaned up.
- It was possible to get in a state where you were unable to switch chat channels. This has been fixed.
- An issue with double entries appearing on the overview has been fixed.


**In Game Browser**


- Fixed the 'trust request' notification pop-up from websites


**Miscellaneous**


- When moving items, the cursor is now anchored in the top left corner of the items, as it previously did.
- System channels, such as Local, now persist correctly and cannot be closed.
- The asset window no longer goes blank if it was open while your ship was docking.


**Patch notes for Tyrannis 1.2 Client Update**

Deploying Thursday November 11, 2010

**FIXES**

**User Interface**


- When you mouse-over a bold text link it will now highlight correctly.
- When switching to the Attributes tab from the Skill history tab, the text will show correctly.
- The size of text will no longer decrease in a chat channel when typing in any language.
- When opening a new list, the previously viewed market list will now collapse.
- Folders will no longer be selectable when using CTRL+A on a tree structure, such as the Places list.
- The Station Services window will no longer appear in a random location on the screen when restoring an overlapping window.
- The amount field in the Transfer Money section of the Corporation wallet has been fixed. You can directly write into the field when the window opens.
- Containers in space will now open in the same location as the last moved window or any stack of containers. Jettisoned containers, salvaged containers and wreck cargo containers have now all been tamed to conform with each other.
- Fixed a small issue with the Upcoming Events window.
- Fixed an issue with End & Backspace functionality in text fields.
- If the starmap is open while a player undocks, objects in local space will not appear on the starmap.
- When the in-game browser is minimized it will no longer distort text in the browser.


**API**


- A line of code in the API was updated to fix errors with mailing lists. The toListID on the MailMessages API will now return an empty string, instead of 0 if it wasn't sent to a mailing list.


**EVE Voice, Mail, & Chat**


- Color formatting in chat will now work correctly.
- When leaving the Voice Chat Channel it longer produces an error.


**Weapons & Ammunition**


- Fixed an issue with modules were being unresponsive to mouse clicks.


**Miscellaneous**


- Fixed the Repair Tool .exe to work even when it cannot find the msvcp71.dll file
- Fixed an issue where players will be able to successfully reprocess single items or a single stack of items.


**Changes**

**User Interface**


- The code module used for entering text in EVE has been replaced with a newer, harder, better, faster, stronger one. Several problems that were encountered in areas like EVEMail are now a thing of the past.
