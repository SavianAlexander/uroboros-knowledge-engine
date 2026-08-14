# Patch Notes for Escalation to Inferno

- **Date**: 2012-04-24T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP Navigator
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-escalation-to-inferno
- **Tags**: #patch-notes

## Overview
Patch notes for EVE Online Launcher 1.318 To be released on Friday, May 11, 2012. The launcher now first tries to download patches that exists and apply them instead of creating them and if that fails, then download the existing patch. The launcher will now check all files in t

---

**Patch notes for EVE Online Launcher 1.318**

To be released on Friday, May 11, 2012.


- The launcher now first tries to download patches that exists and apply them instead of creating them and if that fails, then download the existing patch.
- The launcher will now check all files in the client and runs an update if any file is malformed, previously it was looking at the client build number in common.ini to determine if an update was required, meaning if common.ini was OK but other files not, then a client update was not started. This does not cover launchers that are set to not show up unless an update is required, they still using the old method of looking at the client build number in common.ini
- Fixed an issue where patches where not being resumed correctly if the launcher was closed in mid-download of the create patch step. Resulting in a broken patch.
- The play button was being enabled long before updates where finished, if pushed it would cancel the update and start the out of date client.


**Patch notes for EVE Online: Escalation to Inferno 1.0.3**

To be released on Wednesday, May 2, 2012.

**User Interface**


- It is now possible to toggle the overload status of damaged modules.


**Patch notes for EVE Online: Escalation to Inferno 1.0.2**

To be released on Thursday, April 26, 2012.

**User Interface**


- The font-size in the overview is now scaled properly when using UI-scaling.
- The 'Travel to' option in the fleet broadcast window will now work as intended.


**Patch notes for EVE Online Launcher 1.312**

To be released on Thursday, April 26, 2012.


- If the Launcher encounters an error while creating a patch, it will attempt to download a premade patch file instead. This should fix a broad spectrum of errors that occur during the "Creating patch" step in the Launcher.
- When applying patches, if a patch failed on a single file, the Launcher would error immediately. It now it finishes patching what it can and then errors, leaving a less broken client.
- If patching fails, the .patch file is deleted so that the bad data that caused the issue isn't used again when the user tries to update again after the failed update.
- Launcher logs are now written to files with the naming convention launcher.[year].[month].[date].log instead of just launcher.log.
- Additional, more meaningful logging.
- A multitude of UI, localization and other minor bugs where fixed.


**Patch notes for EVE Online: Escalation to Inferno** **1.0.1**

To be released on Wednesday, April 25, 2012.


### Fixes


**Items**


- Characters can once again access unanchored Secure Containers in space.  Note: Until the secure container has been anchored and has a password, it is NOT secure - **ANYONE** can access it!
- Removing station container restrictions on items from the Lifestock, Frozen and Radioactive groups.  You can now sort your Frozen Foods and Janitors into containers as you see fit.


**Market and Contracts**


- The range filter in the market window has been fixed so now it will retain the previous selection.


**User Interface**


- Long item names are now shown correctly in the cargo window.
- The ship HUD is now being displayed correctly after a session change with open planet view.
- Orca pilots in NPC corps can again open their ships corp hangars when in space.
- You no longer have to inject commas between search terms in the text based asset search. The keyword option hints will also match based on the beginning of the keyword rather than anywhere.


**Localization**


- The Japanese translations of race and faction names are properly shown in the Japanese client.
- The attributes panel of the character sheet is using the translation of the word “points” in localized clients.
- Number formatting settings are now taken from the user’s regional settings instead of from the system’s regional setting.
- Various linguistic improvements have been made throughout the client.


**Patch notes for EVE Online: Escalation to Inferno**

To be released on Tuesday, April 24, 2012.


### **Features**


**User Interface**


- All electronic warfare effects that you are on the receiving end of are displayed in icon format above your ship UI. These icons display who is ewaring you, what ship they are in and what type of ewar it is. Right clicking these icons also provides you with a useful context menu.
- There is a new hairstyle available for female characters.
- Entries in most table like scrolls, such as wallet transaction history, can now be copied with CTRL+C. If entries are selected, only those will be copied, but if nothing is selected and the focus is on the scroll, all the entries are copied. Pasting into other programs such as spreadsheets will line the entries up into rows and columns properly.
- 'Clear Content' and 'Reload MOTD' menu options have been added to the chat channels.
- There is now a right click option on the group/category trace in market details which allows you to find that group in the browse tab.
- It is now possible to add personal notes to quickbar items. This is done through the right click menu ("Add additional text").
- It is now possible to mark your own orders in market details. To enable this, a setting checkbox needs to be checked in the market settings tab. The orders marked as yours have 'modify order' option added to their menu.
- A new text-fade effect is used in overview entries when fleet broadcast or electronic warfare indicators are visible and overlap the text. Also used in overview column headers when the sort triangle overlaps the text.



### **Changes**


**Crimewatch**


- The first phase of refactoring the Crimewatch system has been completed. This phase is mostly invisible from a gameplay perspective, but paves the way for future work on the criminal flagging and aggression mechanics. See [this video](//www.youtube.com/watch?v=g3jK-XZ2KnM) for more details.
- Setting a character to +10 standing will no longer give them automatic permission to legally take from your containers in space.
- Jettisoned containers and ship wrecks are now tagged with the owner, corp and fleet at the time of creation, rather than testing for loot-rights every time they are accessed. This will mean that if the container’s owner logs off, leaves fleet, jumps or docks, then the other pilots will not lose loot-rights access to his containers. This also means that the white/yellow/blue colouring of container icons more accurately reflects their true status.
- Characters in capsules will now show up as criminals on the overview just like when piloting any other ship.


**Ships**


- Titans can now lock a maximum of three targets.
- XL turrets have had their signature resolution set to 2000m.
- Capital Turrets that are fitted to titans now have a new damage-scaling attribute; targets with a signature radius smaller than this size will take reduced damage from these turrets. This does not apply to dreadnaughts.
- Siege modules have had their tracking penalty removed.


**Incursions**


- Vanguard and Assault Sites have been revamped with the following changes: - NPCs have been grouped into waves and groups have been randomized; this will prevent blitzing and increase the random element within the sites.
  - Spawn triggers moved from individual NPCs to the group as a whole.
  - Lowered the rewards from Vanguard sites by 10%.
  - For more information see [this blog](//community.eveonline.com/devblog.asp?a=blog&nbid=28587).


**NPCs**


- All common Rogue Drones will no longer drop alloys and will instead have bounties in line with other NPCs.
- Meta 0 modules in NPC loot tables have been replaced with Metal Scraps.
- The brackets of spawn containers (for hacking containers in mini profession sites) are now being grayed out after being viewed to make it easier to know which containers are not hacked yet.
- NPC's will always aggress you when you warp into their aggression range.


**Market & Contracts**


- A lot of modules have been added to the market that previously could only be found in Contracts. Mostly these are officer, deadspace, faction and storyline modules. Note that this only means that players can now buy and sell them between themselves.
- Modules are sorted on the market by decreasing metalevel. So when you scroll down you should see increasingly more awesome modules.


**Worldshaping**


- The security status of systems in Etherium Reach, Malpais, Oasa, Outer Passage, Perrigen Falls, The Kalvela Expanse and the Spire has been adjusted upwards to bring them more into line with the rest of nullsec.


**User Interface**


- The Corporation Icon is now part of the Neocoms default layout. For users who are not in a player corporation they will be directed by default to the Recruitment tab.
- The 'leaf' groups in the market can now be collapsed like all the other groups.
- The 'Pose' icons within character creation and re-customization now display a clearer representation of the actual pose.
- A few improvements have been made to the quickbar in the market. Items can now be dropped on the quickbar tab, it is possible to multi-select items in the quickbar, items in the quickbar can be copied over to another folder by CTRL dragging them to the folder, and now asset items can be added to the quickbar.
- The most common user interface elements used to represent players can now be dragged over to various edit fields to add the character’s name. These fields include the private fields when creating contracts, edit field in the 'auditing' tab, and member edit field in the 'transactions' tab of the corp wallet.
- The most common user interface elements used to represent item types can now be dragged over to various edit fields to add the types name. These fields include search fields in corp/personal assets, fields corp/personal transaction tabs, and an edit field in the window when creating an item exchange contract.
- In Crucible 1.5, color coded security info was added to the solarsystems in the 'Route' tab of a show info window of a solarsytem. This security info has now also been added to the 'Related Solarsystems' tab for regions, and the 'Adjacent Solarsytems' tab for solarsystems.
- 'Select Station' window for remote market orders now has 2 columns, station name and number jumps, and it's possible to sort the list by either one of those columns.
- Hints that only repeated the original text in the scroll entry have been removed.
- 'Select/Deselect All' buttons have been added to contract creation.
- The currently active ship is no longer listed as available for trade during contract creation.
- A 'Client' sub-menu has been added to the menu of transactions.


**Modules**


- The Thukker Modified 100MN Microwarpdrive is no longer listed as a 100MN Microwarpdrive variant.


**Agents & Missions**


- Agents' showinfo windows will now properly explain the minimum standings requirements needed to use them.


**Graphics**


- Smoothing of shadow transition across geometry LODs.
- Many small clothing intersections fixed.
- Occasional graphical issues on NEX store previews fixed.


**Technical**


- New file format for objects now result in faster loading and more efficient caching.
- General optimization of the module display in the HUD. Dragging modules around and such will be much snappier.


**Miscellaneous**


- A few types which were erroneously removed from Tranquility in Crucible 1.5 have been restored, most notably the old mines and their blueprints. People who were previously in possession of these types will have them re-added to their assets over the following few days.



### **Fixes**


**Agents & Missions**


- Driving a Wedge Part 1 messages are now human-comprehensible.
- Agents in space now correctly identify their location when you try to talk to them remotely.


**NPCs**


- Wrecks from NPCs killed by things other than players (such as in certain Factional Warfare missions) will correctly show as abandoned upon creation.


**Player Owned Structures, Outposts and Stations**


- Fixed an issue where starbase fuel notifications weren't properly removed from the calendar when an online tower goes to anchored or is destroyed.
- Standing and security loss for property damage is now correctly messaged in the character sheet -> security status transaction details.


**CONCORD and Kill Mails**


- Player security statuses in the UI should now always be rounded to one decimal place, to match how the enforcement code rounds them. This should mean that the UI will always consistently report whether or not you're at or below -5.0.
- Security status gains from NPC kills should once again be awarded to every player involved.
- An issue has been fixed that stopped pilots from being able to add items to abandoned Jetcans using these containers as if they were their own.
- When Illegally looting a container during a legal fight, the offending pilot now receives a warning that the action will also flag them to their opponent's corporation.


**Graphics**


- Resolved and edge case where the sun lens flare would sometimes disappear after the warp tunnel was initialized.
- Fixed an issue where warping through a planet would stop the warp tunnel from displaying in certain instances.
- Resolved a defect where the station hangar scene would be rendered black if you disabled the station environment and alt+tabbed.


**User Interface**


- An issue with the displayed messages when leaving or joining a chat channel with an edited name has been fixed.
- Text entered using an IME is no longer concealing previously typed text, while it is being edited in the IME.
- The in-game log is no longer breaking, when trying to display multi-line messages.
- The overview is now sorted correctly directly after undocking.
- A display issue with the Character info window has been fixed.
- The Jukebox will no longer create a duplicate icon on the Neocom when it has been collapsed.
- An issue with the right click context menu on empty areas within the chat windows has been fixed.
- It is no longer possible to paste strings containing letters or other illegal characters into a numeric field to avoid scams (letters or spaces at the end will be stripped off, but a warning sound is played).
- Overview entries are now being removed or added correctly when filtering by standing or fleet membership and their status is being changed.
- An issue with dragging and dropping fittings onto and inside folders within the Market quickbar has been fixed.
- It is now easier to place the cursor on empty lines, for example in the Bio or the Notepad.
- An issue with the Station Services menu resizing when small station service buttons are used has been fixed.
- It is now possible again to open show info windows by clicking the (i) button in solar system map hints (and other hints are being hidden while expanding one stack of hints).
- Fixed an issue where when hiding all windows while the Items and Ships window were merged with the Station Services panel, the Items and Ships window would become unusable.
- An issue with the alphabetical arrangement of entries in the Legality tab has been fixed.
- Only one confirmation popup window is shown, when trying to close the game several times by clicking the close icon (or Alt+Ctrl+Q) repeatedly.
- Significantly improved an issue where moving planetary interaction extraction pins would cause a performance loss.
- Fixed an issue where a text string was missing in the Wallet drop down for the Datacore Fee transaction type.
- In a localized client, local chat no longer becomes locked when jumping through stargates.
- 'Show English tooltips' no longer blocks drag/drop functionality from list view of hangar.
- 'Show English tooltips' no longer blocks access to right click menu.
- Hovering over incomplete skill requirements in showinfo screens will once more show the required training time.
- Instead of doing nothing, world map search now returns an error if you try to search with 2 or less character.
- The transparency of stacked and pinned windows is now persisted correctly after relog.
- 'Any' search type will now return results for corporation tickers.
- Brackets of stations are now updating correctly when adding them as waypoint.
- Several html encoded characters like < and > are now shown correctly in the overview.
- Market region headers are now correctly aligned.
- Fixed an issue where when hiding all windows while the Items and Ships window were merged with the Station Services panel, the Items and Ships window would become unusable.
- Fixed an issue where words with an apostrophe in them would break onto two separate lines in mission text
- The correct message for voting to unlock a blueprint now appears in the Open Votes window in Corporation/Politics.


**Localization**


- The description of the Naga states the correct bonuses in the German client.
- An issue with some item names showing the old versions in both the German and Russian clients has been resolved.
- Exporting market data from a localized client is working again.
- Various linguistic improvements and formatting changes have been made throughout the client.


**EVE Voice, Mail & Chat**


- Join channel menu entries for fleet are now correct.
- Previously clicked links are no longer being added when dragging fits or the solar system icon into chat.
- The color of text in a MOTD is no longer reverting to its default color after a link.


**Miscellaneous**


- The 'Micro Shield Transporter' sound effect will now cycle without an abrupt stop.
- The Support, News, Account Management and Patch Notes buttons have been removed from the log in screen as they are now located in the launcher.
