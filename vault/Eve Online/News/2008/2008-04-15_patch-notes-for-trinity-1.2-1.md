# Patch Notes for Trinity 1.2

- **Date**: 2008-04-15T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-trinity-1.2-1
- **Tags**: #patch-notes

## Overview
Trinity 1.2: Patch Notes, released 15 April 2008   CRITICAL Junk-in-Space has been activated and will go live after Downtime on 16 April. In Trinity 1.1: Boost Patch we deployed the Junk in Space Cleanup Program whereby anchored containers will have a 30 day timer from the last

---

## Trinity 1.2: Patch Notes, released 15 April 2008



### CRITICAL



- Junk-in-Space has been activated and will go live after Downtime on 16 April. In Trinity 1.1: Boost Patch we deployed the Junk in Space Cleanup Program whereby anchored containers will have a 30 day timer from the last time they were interacted with and they will then be deleted when the timer expires unless they are in proximity to a Starbase. Another part of this program is that drones, fighters, shuttles and rookie ships in space will be deleted on the first of every month and while the clock started ticking on 12 April we decided to give it a bit more time so the system will become active during downtime on 16 April. For more information on this feature, please read this [Dev Blog.](//myeve.eve-online.com/devblog.asp?a=blog&bid=540) Bookmarks may become invalid after Junk in Space Cleanup Program is activated on Wednesday, 16 April. If you have any bookmarks that were created by right clicking a container in space and selecting "Bookmark location" the bookmark will point to the container ID. When the container is then deleted by the Junk in Space Cleanup Program the bookmark will point to a container which doesn't exist and therefore it becomes invalid. This also affects bookmarks that are copied and transferred between characters, when trying to move them to People & Places the action will fail silently, meaning no error message is displayed. You can prevent this by visiting your bookmarks before Wednesday, 16 April, and re-create them so that they don't point at containers but rather at coordinates in space (right click in space next to the container and create a bookmark).
- NPC corporations will no longer be selling shuttles



### FEATURES & CHANGES


**Technical**


- Stackless Python has been upgraded from version 2.5.1 to version 2.5.2. To quote the Python 2.5.2 release announcement: "This is the second bug fix release of Python 2.5. Python 2.5 is now in bug fix-only mode; no new features are being added. According to the release notes, over 100 bugs and patches have been addressed since Python 2.5.1, many of them improving the stability of the interpreter, and improving its portability." For more information on Stackless Python and EVE, please read this [Dev Blog.](//myeve.eve-online.com/devblog.asp?a=blog&bid=488)


**Ships & Modules**


- Ships with more modules fitted then the slot layout allows will no longer be able to undock. This can happen if the slot layout is balanced in a release and the ship is fully fitted during the deployment downtime. Simply unfitting the excess modules will allow the ship to undock again.


**New Player Experience and User Interface**


- The insurance, repair shop, medical and bounty station services have been transformed into windows to allow for welcome pages.


**Graphics – General**


- In an effort to prepare for future graphics projects we are collecting information about graphics cards. This will allow us to better target the hardware of EVE's player base.


**Installer, Updates and Patches**


- Unicode characters are now supported in the name of the installation folder.
- The uninstaller will now ask if you also wish to remove the settings and cache folders and all client hotfixes that have been installed.


**Miscellaneous**


- Multiple bug fixes were made to our GM tools and some new features implemented to improve our customer support.



### FIXES


**Ships**


- Combat Recon ships are now able to use acceleration gates that allow Force Recon ships.


**Modules**


- An error message should now display when you try to activate a cynosural field while traveling faster than 500 m/s.
- Activation duration and the Capacitor usage of Sensor Boosters, Tracking Computers and Remote Sensor boosters have been reduced.


**Drones**


- Faction drones have been added as variations of other drones


**Player Owned Structures, Outposts and Stations**


- Structures requiring sovereignty to be onlined now require sovereignty or they will be offlined, thus if the sovereignty is lost these structures will become offline.
- Structures that can be anchored inside a Control Tower force field such as assembly arrays will no longer become incapacitated when damaged into structure.


**Character Creation and New Player Experience**


- A message asking if you would like to continue at the end of the beginner tutorial "Aurora: Crime and Punishment" has been removed, since it's the end of the tutorial and you could not continue if you wanted to.
- An issue has been fixed where players were not automatically warped during the New Character Tutorial if they previously cancelled it and restarted the client while in a station.


**NPCs**


- Some NPC drones did not have a model in the premium client, this has now been fixed. The following NPC drones where affected: Spider Drone I, Spider Drone II, Mammon Drone, Asmodeus Drone, Beelzbub Drone, Belphegor Drone, Dragonfly Drone, Incubus Drone, Moth Drone, Scorpionfly Drone, Tarantula Drone and Termite Drone.
- Khanid Rookie now has proper tracking.
- The Amarr Navy Apocalypse has had its rate of fire reduced and damage increased to stop the laser effect from being a continuous beam.


**Agents & Missions**


- The mission "Vitoc Vector" has been fixed and re-enabled.
- The overseer structure from the mission "Angel Extravaganza" has been removed and the mission re-enabled.
- Rogue Drone exploration sites now properly drop when the first hacking attempt is successful.


**Science and Industry**


- A server side exception that cropped up when installing blueprints into mobile laboratories for copying has been fixed.
- The base manufacturing time of the warp disrupt probes and bombs has been increased to be in line with other charge type manufacturing.
- The base research and manufacturing times of the shield boost amplifier I blueprint have been changed to be more in line with other modules.
- The Ares Oscillator component manufacturing requirement has been reduced to be in line with other ships of the same class.
- The Helios photon microprocessor manufacturing requirement has been reduced to be in line with other ships of the same class.
- Laser Sensor Clusters components have been correctly renamed to Ladar Sensor Clusters.
- A typo in the item Golden Mykoserocin has been fixed
- Vernillion Mykoserocin has been correctly renamed to Vermilion Mykoserocin


**Market & Contracts**


- It is now possible to add market groups to the quickbar in the market window.
- The "View Market Details" right click option should now always open the market details tab instead of the last selected tab.
- Items and folders in the market quickbar should now be sorted alphabetically.
- An issue with adding items to the market quickbar overwriting already added items has been resolved.
- It is now possible to filter market orders by CPU usage, trained skills and min/max deviation from market average price.
- Market filters set in the settings tab can now be toggled on/off in the details tab for sell/buy orders.


**Corporation & Alliance**


- Added new operations filters to adverts; Logistics, Mercenaries, Role-playing, Trade.
- New filters for time zones.
- Corporations not in alliances are now listed as "none" rather than "unknown".
- "Days" has been changed into "Duration" for the duration of the advert.
- Min and max corp. members filter has been cleared up.


**Graphics - General**


- An issue where planets and moons caused a drop in frames per second rendering has been resolved.
- The mysterious "Star in the North" that has been baffling everyone with its mysteriousness has now suddenly and mysteriously disappeared.
- The ship jump animation is now also played in the solar system ships are jumping out of.
- Generating character portraits should now be working correctly.
- The 1152x864 resolution has been added back to the client, it is still broken on some machines but since it works on some we decided to put it back.
- Changing display adapters while in space should no longer crash the client or cause all windows to become blank.
- Character portrait rendering was becoming more erratic the more portraits where rendered, this issue should now be fixed.
- Portrait rendering has been improved to invalidate cached method call files it can no longer use; this should in turn reduce the size of the cache folder in some cases.


**Graphics - Premium Graphics Content**


- The station interior of Yulai IX - CONCORD Bureau in the Premium client was of Caldari design, the interior has now been redecorated in Gallente high fashion.


**User Interface**


- The jump tab in the capital navigation tool should now be working for characters that are not in an alliance.
- Moon icons should now be displayed in space regardless of distance.
- Operating system names instead of numbers are now displayed in the OS select menu when creating technical petitions.
- A grammar error was corrected in the ESC menu -> info window settings.
- The client should no longer crash while using the in game profiler (Alt+Ctrl+Shift+m).
- The scanner button in the HUD should now close the scanner window if it is already open.
- The ship cargo button in the HUD should now close the cargo hold window if it is already open.
- The fleet member list should now update when the structure of the fleet changes, players moved or invited, squads/wings moved or renamed etc.
- The right click option Add Bounty should now work when right clicking player characters.
- The error preventing the Capital ship navigation window from being closed has been resolved.
- We have added a right click menu option to the character sheet to allow you to view the market details of skills.


**Mac**


- Added ability to turn on tracing similar to existing Linux functionality, so that Mac ISD Bug Hunter volunteers and normal users willing to help out track down problems, can provide extra useful information when using the bug report system.
- Several stability issues were fixed, resulting in better client stability and experience for everyone.
- Fixed the graphics for the Cargo Capacity indicator.
- Fixed an issue where the in-game clock would start accelerating out of control resulting in forced client restart and destruction the client settings.


**Linux**


- Added better voice capture re-sampling support to get voice input working with more microphones under ALSA.
- Several stability issues were fixed, resulting in better client stability and experience for everyone.
- Fixed issues with “open browser” links (such as when the autopatcher refer you to manual patching)
- Fixed several issues where the client would hang instead of restart after changing various settings
- Fixed the Cargo Capacity indicator
- Fixed an issue where the client would hang when clicking the Log off button on the ESC menu.


**Localized Clients**


- The Remove Advert dialog box should now be translated to German.
- The "Show only available" text in the lower right corner of the market window should no longer be out of bounds in the German client.
- A client side exception that popped up when receiving mail in a localized client has been fixed.


**Miscellaneous**


- Jump clones can now be installed at NPC stations again, provided that standing requirements are met.
- Solar systems will no longer be unloaded after 8 hours of inactivity; they will instead remain loaded until the next server downtime.
- A server side exception that occurred when plotting a route to an unreachable solar system has been fixed.
- Vista: Media Center should no longer restart after EVE is launched.
- A client side exception to do with scroll bars in some windows has now been fixed.
- A sever side exception to do with missiles when they impact has been fixed.
- Rating petitions should no longer create a duplicate petition.
- Alert mails sent out by the server for monitoring purposes have been causing excessive load and have thus been reviewed, mails deemed unnecessary have been stopped.
- LogServer logging and formatting has been improved to provide even more useful information.


**EXPLOIT FIXES**


- Several exploit issues have been fixed, making EVE a better world to live in for us all.


**Trinity 1.2-1 Server-side changes deployed 15 May 2008**


- Wrecked Caldari station has been added.
- An issue where conquered stations would not automatically switch ownership has been fixed.
- Customer Support tools has been improved.
