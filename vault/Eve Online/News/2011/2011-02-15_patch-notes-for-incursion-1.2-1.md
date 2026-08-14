# Patch Notes for Incursion 1.2

- **Date**: 2011-02-15T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incursion-1.2-1
- **Tags**: #patch-notes

## Overview
Patch notes for Incursion 1.2, released February 15, 2011   Table of Contents FIXES FIXES Experimental Contracts Full details on experimental contract features can be found in a blog from CCP Atlas entitled Contracts Features. Blueprint copies and blueprint originals can

---

**Patch notes for Incursion 1.2, released February 15, 2011**

**Table of Contents**[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=221#fixes)

**FIXES**

**Experimental Contracts**


- *Full details on experimental contract features can be found in a blog from CCP Atlas entitled *[*Contracts Features.*](//www.eveonline.com/devblog.asp?a=blog&bid=833)
- Blueprint copies and blueprint originals can now be searched independently by selecting the appropriate option in the Category drop-down.
- Auction, Want to buy and Want to sell can now be searched independently.
- Security filters have been added allowing you to search any combination of high security, low security and null security space.
- An "Auction" tag has been added to auction contracts to differentiate from Item Exchange.
- Clicking an entry in the contracts search results will now highlight that entry.
- Full result ordering and order direction are now combined into one drop-down box and moved to the top of the window in an attempt to clear up confusion between full-result (server-side) ordering and per-page (client-side) ordering. When the full-result drop-down box changes a search is initiated and the per-page sorting is changed to match.
- Added buttons to toggle between 'detailed' view and 'list' view.
- A new column, "Date Created" has been added.
- "Find in contracts" has been removed from places where it doesn't belong. It should now follow "view market details" more closely.
- If you change the per-page sorting it persists between searches until you change the results sorting.
- The location drop-down now remembers your last five location searches between sessions.
- The "Item Type" input field now accepts simple wildcard searches using the '*' token. You can enter quite advanced queries into this field when combining the wildcard search with the metatype and category searches. - An example might be 'Module:Pith*hard|Deadspace' which will search for any modules starting with pith and containing 'hard' of the metagroup 'deadspace'.
- Fixed an issue where some filter fields did not remember their values when the window was closed and reopened.
- The page will always scroll to top when switching between pages.
- Several grammatical and typographical errors have been corrected in the UI.


**Market & Contracts**


- In-progress courier contracts now have an in-space submenu for the drop-off and pick-up stations when you are in the correct system, which is similar to how missions work.
- Creating a courier contract from a plastic wrap will now fill in the destination for you allowing for easier 'forwarding' courier contract creation.
- Contract right click menu in all contracts search views now includes a 'station' submenu with two submenus in the case of courier contracts.
- Contracts now enter 'require attention' mode when there are six hours left instead of 24.
- Item selector in create contract wizard now shows the number of selected items and will display in red if you go above 200.
- Context menus have been added to the item list for 'Want To Buy' contracts.
- Reward per jump is now shown in the contract details window. this will now show you how much isk per jump the contract yields using your current autopilot settings. Reward per jump is likewise shown in the Create Contract windows and uses the creator's autopilot settings.
- The create contract window for courier services now shows you if your route will pass through a security boundary.
- The state of your sell window (normal/advanced) will persist (remember your last used setting) on a character basis.
- Market orders in Player-owned outposts will now display the system name as well as the station name.


**Assets & Items**


- Asset searches can now be sorted by number of jumps so that you can easily view your proximity to locally stored assets.
- You can now drag and drop items into closed containers without having to open them first.


**Agents**


- Added a verification message when you remove agents, so removing the wrong agent by mistake becomes less likely.


**Exploration & Deadspace**


- The Sansha Incursion sites no longer allow Rorquals to enter.
- Outgrowth Rogue Drone Hive has had its overseer drops brought more in line with other similar complexes.


**Clones**


- Jumpclones can now be remotely destroyed from the character sheet. The window has been updated also.
- When moving your active clone to another station, the list of possible destinations will contain the region and security status
- Clones with insufficient skill points will now be greyed out as a warning when buying a new clone.


**NPC's**


- It is no longer possible to lose a ship to CONCORD by only using logistic modules (like remote armor repairer, shield transporter, energy transfer array, ...) or logistic drones. They cannot be activated in high-sec on targets with Global Criminal Countdown (GCC) or outlaws and they will be deactivated if the target gets GCC while being assisted.
- Officer difficulty has been increased to reflect their value.
- Incursion sites are now taxed in the same manner as regular bounties.
- Adjusted Incursion site contribution to give slightly less influence. We also adjusted the influence regain in low- security and null security, to make sure they can be completed.


**Sound**


- An issue has been resolved where Incursion sound effects were not playing for some players when entering an Incursion systems.
- An issue has been resolved where Incursion sound effects were not playing for players who login with their ship docked in station.


**User Interface**


- Priority modification in the overview settings now has drag-and-drop functionality.
- The 'Autopilot' tab in the starmap now has drag and drop functionality for sorting waypoints.
- The right click menu item has been added to the route label in space so that it is now possible to clear all waypoints from space without going to the starmap.
- Market and Fleet collapsible menu stacks now have redesigned icons with indenting for better usability.
- There has been a slight modification to the character sheet to sort out some irrelevant information.
- It is once again possible to capture portraits of characters in-game.
- "Show contracts" links on show info pages of other characters have been moved off the main page and into the menu.
- An issue with the Drone UI when switching ships no longer occurs.


**Character Portraits**


- You no longer need a shirt to make a portrait but simply require something on your top, either a jacket or shirt. Proper garments for the lower body and feet are required.


**EVE Gate**


- Searching for long strings in EVE Gate returned snipped search results. This has now been fixed so that the result text is wrapped.
- EVE Gate display of corporations with long names has been fixed.
- The character name challenge when logging into EVE Gate for the first time has been changed to be case sensitive.
- Previously, when viewing the broadcast wall of one of your contacts who had set standings towards you so you can see his wall, the contacts on the left side were actually your own and not his. This has now been fixed.
- A fix has been deployed for improved performance to EVE Gate.
- Some minor updates to the EVE Gate layout have been added.


**Localization**


- A number of translation/localization related issues have been resolved in various parts of the UI and item descriptions in game, as well as EVE Gate.
- Previously unlocalized text in the character creator has been revised and translated.
- 'Incursion' is now consistently being referred to as 'Übergriff' in the German client.
- The translation for the term command center, in Planetary Interaction, has been changed to 'Befehlszentrale' since the previous version was potentially offensive.
- The EULA has been reverted to the English version for legal considerations.


**Client update #1 for Incursion 1.2**

To be deployed on February 16, 2011


- 18 new Alliance Logos added.
- The fleet window will no longer expand every time it is re-opened when in a fleet
- Left clicking some windows was opening the window options menu. This functionality has been returned to right-click only
- An issue with Killmails reporting incorrect damage has been resolved


**Client update #2 for Incursion 1.2**

To be deployed on February 22, 2011


- When dropping items onto a container icon the items would be deposited as locked by default. They are now deposited as per the container settings.
- When creating a contract with a plastic wrap you will now get a message confirming the total size of the contract with the plastic wrap.
- The Type field in the contract’s search is no longer case sensitive when searching for items.
- When copying a contract containing a blueprint you will now get a warning that the contract wizard cannot tell between a blueprint original and copy.
- On rare occasions after accepting a courier contract a ‘complete’ button would not exist. This has been corrected.


**Hotfix for Incursion 1.2**

To be deployed on February 22, 2011


- 43 new Alliance logos have been added.
- All players will now be able to stack items correctly in customs offices hangars.
- When you finish a courier contract by right-clicking it, the bookmark for it will now disappear correctly.
- Courier contracts containing an assembled ship can now be forwarded correctly.
- In rare cases it was possible that the warp disruption effect of focused warp disruption field generators was not removed correctly from the victim when jumping to another system. This has been fixed.
