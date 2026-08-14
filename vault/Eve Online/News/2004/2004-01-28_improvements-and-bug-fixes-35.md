# Improvements and Bug Fixes

- **Date**: 2004-01-28T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-35
- **Tags**: #patch-notes

## Overview
Bug Fixes and Improvements Game Design NPC Pirate distribution has been altered. All pilots are warned to explore with great care, and encouraged to use the maximum warp-in range possible when exploring. Pirate difficulty is significantly more random, the first group you see in a system is

---

**Bug Fixes and Improvements**

**Game Design**


- NPC Pirate distribution has been altered. All pilots are warned to explore with great care, and encouraged to use the maximum warp-in range possible when exploring. Pirate difficulty is significantly more random, the first group you see in a system is most likely not going to be the toughest that will show up there. Low security empire space has been made more difficult, pirates in Non-Sovereign space (F10 map: Color Stars by: Sovereignty) will pay more attention to systems with more valuable ore, and the most difficult pirates will be found in space controlled by NPC Pirate Factions.
- The problem with NPC pirates always spawning next to players in deep space has been fixed, players should beware since they can warp in to belts or respawn at random locations.
- Security Status gains for NPC Pirate hunting have been increased. In Castor your sec status is altered based on the 'worst' pirate you destroyed in any 10 minute period. Your sec status will not raise past a maximum amount for each difficulty of pirate. (Also: See the new 'security status' tab in the Char Sheet).
- Guristas Silencer had too high bounty on him, his bounty is now correct.
- CONCORD and Empire Police & Military units will no longer be appearing in 0.4 security space.
- Volume of Nuclear M and Carbonized Lead M projectile ammo has been fixed.
- Rare drop hull modules (Inertia Stabilizers, Overdrive Injector System, Nanofiber Internal Structure & Reinforced Bulkheads) had lost their bonuses but now have been edited to give bonuses compared to the module types.
- Capacitor Recharger rare drop modules now give correct bonus values, they weren't giving any bonus compared to the original module.
- All Gunnery skills have been set back to perception as primary learning attribute and willpower as secondary.
- Volume of all missiles lowered and capacity of launchers tuned to compensate. No net change in launcher capacities.
- Names for Missile Launchers have been changed, the numbers in their names have been removed and the named Missile Launchers that NPC's drop now have their name referenced to the Launcher group they belong to. Example: H-50 Heavy Launcher I is now Heavy Missile Launcher I.
- Spaceship Command Skill bonus has been lowered from 5% to 2% agility bonus.
- Medium and Heavy Capacitor Booster Modules have had their power grid requirement increased and CPU requirement reduced.
- Base price on Medium Projectile Turret skill has been fixed, it will now cost the same as before on the NPC market.
- Energy draining weapons (Energy Neutralizer and Nosferatu, including meta types) have been made more suitable for frigate use. New Medium and Heavy versions have been added and will be introduced for cruisers and battleships.
- Blueprints for Tech Level I equipment that were missing should now be available.


**Agents/Missions**


- Tweaked the mining missions asking for ore so that they now take the new ore distribution system into account.
- Improved the NPCkill missions so that they should no longer occur at stargates in systems with more than 0.3 security rating.
- Fixed the issue with certain commodities appearing at the wrong location after completing a mission.
- Fixed the mission "Shopping spree" so that the briefing tells the player the correct time limit.
- The mission "foundation stone needed" now has a warning telling the player that the item which must be moved is 180 cargo units, meaning a small frigate cannot complete the mission. Military corp agents should no longer receive this mission as well.
- The spawn timer on the defunct drone modules and temple stones has been decreased. The missions which ask for these items have also been reduced in frequency.
- The implant missions are now more frequently dished out by most agents. Take note however, not all factions hand out implants.
- BP offer expiration now at 7 days instead of 2.
- Balanced prices on agent location services, and upped the range by one for level 2+ agents.
- Added confirm dialog for huge transport missions.
- The research agents were asking for too many homeless per research mission. This has been tuned down a bit.
- Players doing the tutorial missions are now referred to a new level 1 agent when completing the final mission.
- The eighth tutorial mission no longer asks the player to bring back loot to finish the mission.
- The scenario missions have had their reward and partial failure timer upped.


**Gameplay**


- You can no longer fit modules to your ship that need more power than the total power your ship can give.
- There was a remaining case where npc missiles would destroy a player's pod immediately after the preceding missiles destroyed the player's ship. Npc missiles should no longer be able to pod players.
- Missiles that collide when the ship that launched them is in the process of warping away now do no damage due to the loss of contact with the ship that launched them.
- The current charge of either Shields or Capacitor no longer changes when the maximum possible charge changes (bringing modules online/offline), unless the new maximum is lower than the current in which case it is lowered to the new maximum.
- Missiles cannot be launched any more unless the player has their required skills. Previously players with skills could fill a fitted launcher with missiles for players who did not have the skills.
- The emails from CONCORD to a player when their ship was destroyed should now correctly list what types of ship each of the involved parties were flying at the time.
- FOF missiles no longer continue firing at targets that have recently exploded.
- You can no longer board another ship directly while your current ship is still cloaked.
- Escrow panel should now load for those previously getting exceptions from it ("Couldn't convert time").
- Escrow panel should no longer through an exception on submission of a contract. This has never prevented mission submission, but the user was getting no visual feedback of success, especially if exceptions were turned off.


**In Flight**


- Ship bracket coloring has been changed. In order of priority: Gang member (blue), Same Corporation (green) or corporation warfare (orange), Corporation set standing (yellow/blue), Player set standing (yellow/blue), Outlaw (red).
- Ships should no longer show as derelict, however bracket coloring is not yet reliably applied to ships that would otherwise show as derelict.
- Autoscanner has been updated. All columns except status can be resized. The Threat marker has been split up.
- Ranges no longer show negative values.
- Stations are sorted in NavMenu. The station name has been shortened.
- Secure cargo containers have correct target lock icons now.
- HUD Markers fade out if they are further away
- Any Bookmarks you have for your current solar system now show in the Current Location (Nav) menu under "My Places:".
- Cargo container update bug has been fixed.


**NeoCom**


- Added "Security Status" tab in Character Info window.
- You can no longer reply mails to NPCs.
- Improved handling for large channels, such as corp chat or help channel.
- Chat shows only time in time stamp mode now.
- Added support for saving chat channel passwords
- Added folders in Buddies and Agents.
- Added evemailto support in ingame browser, it can contain: list of names, subject and message...
- Dragging credits to and from wallet is no longer possible. A way to 'cash in' currently withdrawn credits will be provided.


**Other**


- Combat drones further optimized in several aspects.
- Added combo box for known usernames on login screen.
