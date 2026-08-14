# Improvements and Bug Fixes

- **Date**: 2003-05-30T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-27
- **Tags**: #patch-notes

## Overview
Improvements, 1031 - 1054 Agents Access to level 3 agents has been made available. Complete a lot of level 2 missions and your agent might offer you the chance to proceed up the agent ladder. Added new agent service "Rumours", for publishing scenario locations. Improved market suppl

---

**Improvements, 1031 - 1054**

**Agents**


- Access to level 3 agents has been made available. Complete a lot of level 2 missions and your agent might offer you the chance to proceed up the agent ladder.
- Added new agent service "Rumours", for publishing scenario locations.
- Improved market supply/demand features so that agent's would be less tempted to give out non- available items (if the missions are configured in that manner).
- Some agent trade missions are now declinable. Declining a mission does have a slight standing penalty though.
- Improved agent config loading for increased performance of all agent ops (they're still slow, but it's better...)
- Skills are now starting to affect agents properly.
- Improved and simplified agent's handling of agent config values and agent's memory of chars.
- Cargo scanning now works on entities.
- Cargo scanning is now accuracy based and a scanner is not operated at optimum range, it may return incorrect results.
- Fixed cargo scanning of entities to only return the actual cargo and not the fitted items.
- Added ability to ship scan entities.


**Modules and Charges**


- Ship scanners no longer return false results from scanning spawn containers.
- Heavy Missiles, i.e. Havoc, Thunderbolt, Widowmaker and Scourge have had their damage increased by 50%.
- Modules have had their volume decreased to suit to ships capable of using them, some modules had too high volume and were hard to loot because of this.
- Smart Bomb module is now marked as an offensive weapon (which it wasn't before).
- Modules which are all of non-targeted, non-ranged and non-offensive should now stay active and can be activated during warp.
- Projectile weapons have had an increase in damage, but are still not capable of having as much ammo as hybrid weapons.
- Anti Warp Scramble module is now available on the market.
- Skill requirement for the Havoc Heavy Missile was set to Cruise Missile skill, this has been fixed.
- The max range for stasis webifiers has been increased alot, Stasis Webifier I for example will now operate up to 10.000 meters.
- Heat Sink has been lowered in CPU usage to even it out with the gyrostabilizer.
- The CPU Enhancer had incorrect hitpoint values, often causing crashes during module repairing. This has been fixed.
- The gyrostabilizer was giving modification values to hybrid weapons as well as projectile weapons, it will now work as described, i.e. only projectile weapons.
- When the activation of a module that is offline silently brings it online, the client should now be notified and the module context menus should be correct accordingly.
- Focused Medium Pulse Laser had an fall off of 1.100, which should have been 11.000. This has been fixed.
- The 125mm railgun and 150mm railgun have had their tracking speed decreased from 0.12 to 0.06, railguns are long range weapons but they were behaving as blasters when it came to close combat.
- Cargo scanning is now accuracy based and a scanner is not operated at optimum range, it may return incorrect results.
- Frequency crystals: Multifrequency M, Standard M, Multifrequency L, Standard L and Ammo: EMP M have had their damage increased by a little bit. The values that were on the live server were incorrect.


**NPC´s**


- There are now 30 new pirate types out there.
- The response time for empire police, faction militaries and CONCORD in 0.5 - 1.0 security space has been increased.
- Convoys should now pick the correct ships for the race of the NPC corporation that owns the convoy. Rather than any random convoy ship.
- Added ability for npc's to make use of status web modules if they have that facility available.
- Fixed cargo scanning of entities to only return the actual cargo and not the fitted items.
- Added ability to ship scan entities.
- Cargo scanning now works on entities.


**Combat**


- Podding now always results in a security status penalty when applicable regardless of who started the fight (if it started when the pod was inside the players ship for instance) to all parties involved in damaging the pod.
- Destroying the ship who is considered to have instigated the aggression between you will no longer result in kill security status penalties.
- Bug in the faction and security loss/gain was fixed, players will now always loose and/or gain security and faction standing when attacking and killing a player or a NPC.
- All combat damage messages should now go to the log window. Before this, the ones that were not displayed were discarded.


**Communication**


- 100 ISK CSPA service charge no longer required when initiating communications with anybody who is in your corp, in your gang (as well as anybody who has put you in their address book)


**Other improvements**


- Added a description for the basic "jettison" cargo container noting that it doesn't last long in space. Also added a mention of this and that other players might loot containers to the in-space tutorial.
- Gang invitations from blocked characters get automatically ignored. You have the option to block the character in the join gang dialog.
- Secure cargo containers should work acceptably (minor issue: on password change, the password is not checked if you have successfully opened the container before).
- You will now find that repairing your ship is much cheaper than it was.
- Sun occlusion now works for planets. For those cards that support it, this is good news. Because now stations, asteroids, planets don't make the sun turn on and off but occlude it naturally. Old behaviour still in for cards that don't support this one.


**Bug Fixes, 1031 - 1054**


- Modules would never autorepeat if their target was not present, unfortunately this also applied to modules which didn't need targets and therefore because nothing was no longer present, they wouldn't repeat.
- If modules were active when someone jumped between solarsystems they would stay active in the module ui (again), fixed this.
- Fixed an error that occurred when a secure container was opened straight after being assembled.
- Gyrostabilizer, heat sink and magnetic field stabilizer were boosting attributes even if they were not toggled online, this has been fixed.
- Server/DB state mis-match in factories causing all sorts of problems has been fixed
- Afterburner Effects have been brought back
- Corporation - Exception after being podded and returning to hangar has been fixed
- Autopilot - Autopilot not disengaging problem is fixed
- Tabs that form when items/ships merge are no longer cluttered
- An error that occurs when accepting the rental fee of an office has been fixed
- A few random errors occuring in space have been fixed
- Trying to login after being booted from the server raised an exception - fixed
- There was an error in war surrender which was fixed
- The info in market email after market transaction is no longer incorrect
- Executioner had capacity 135 but the description says 225 - fixed
- An error sometimes occured with using autopilot and jumping to another system, has been fixed
- Unsupported operand type(s) error when buying something from the market - fixed
- Corp wallet no longer shows bills double
- Error while engaging a convoy "AttributeError: Warping instance has no attribute 'finalExplosion'" - fixed
- Activating the "merge hangar into station panel" option while in space gave you a black screen - this option has been disabled while in space
- Refining skill not working properly
- A couple skill level exploits have been fixed
- Some repairshop damage discrepencies fixed
- Animation of mining lasers sometimes didn't work properly during/after mining - fixed
- A bug with inviting a player to a gang who has a cargo container close by has been fixed.
- Deposits of 0 to the corporation wallet are registered in the transaction journal.
- Ability to fly Cruiser without fully trained Cruiser skill
- When buying items on some market range, closest should be chosen
- CHAOS: esc>graphics tab spawns multiple Monitor Setup Menus - Fixed
- Bookmarks - not updating - Fixed
- Vanishing dialogs/windows on jump - fixed
- Searching for names and displaying results - Improved
- Shares, text error when owning none - Fixed
- Transaction window sorted wrong way(oldest first) - Fixed
- Autorepeating afterburner status displayed incorrectly after jump - Fixed
- Changing ship name, char length misinformation - Fixed
- Error in shipscan of convoys - Fixed
- Able to accept courrier missions without having the money to pay the collateral - Fixed
- Text error when having no assets - Fixed
- Toggling to fullscreen prompts a crash to desktop - Fixed
- Sell orders are not registering - Fixed
- Skill learning bug - Fixed
- Error when merging hangars under station panels - Fixed
- Skill stuck at "completion imminent" - Fixed
- Bookmarks, No Drag & Drop - Fixed
- Window content goes outside of frame when multiple options are set in votes - Fixed
- Focus problem with windows - Fixed
- Problem when closing the configuration window - Fixed
- Partial Ammo Load Error - Fixed
- Item hangar does not refresh after quick sell - Fixed
- Bookmarks: Enter must be pressed to add a bookmark - Fixed
- If a ship is damaged, quitting and logging in again will fix it - Fixed
- Bookmarks created in player built stations do not get a warp to option - Fixed
- Radar. starting the game with Radar set to "OFF" generates error - Fixed
- Brackets of pirates staying behind
