# Improvements and Bug Fixes

- **Date**: 2004-06-16T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-40
- **Tags**: #patch-notes

## Overview
Bug Fixes and Improvements   General Fixes the case that when you enter a new solarsystem, you don't get the aggression info of the system until the first aggression has been performed. Fixes to accepting gang invitation while session change is in progress. Fixed a stackt

---

**Bug Fixes and Improvements**

**General**


- Fixes the case that when you enter a new solarsystem, you don't get the aggression info of the system until the first aggression has been performed.
- Fixes to accepting gang invitation while session change is in progress.
- Fixed a stacktrace error that may occur when viewing the info of a NPC corporation.
- Fixed bracket coloring being shown incorrectly based on standing. Should now show enemies and friends correctly.
- Payment submission issues should be resolved.
- An issue with the chat window displaying incorrectly after a user typed a large amount of text, or pasted a large amount of text into the chat window, has been fixed.
- When the autohide option was on and toggled off using the right click menu after the NeoCom has hidden, the NeoCom would stay hidden until next relogin. This has been resolved.
- A Spanish version of the tutorial has been added.
- Direct standing is now set to 0.0 by default.
- You can now search for a corp ticker.
- NPC->PCCorp standings are now averaged rather than dynamically updated.
- If a character has a skill that is incorrectly flagged as "in training", the incorrect "training" of that skill can now be cancelled.
- If a player logged into EVE in a station and selected a ship, the fitted modules would be showing offline when they were actually online. This was a graphic error that has been resolved.
- The audio library has been updated.
- GMs can now join all channels,even channels that require a password to join. They also automatically receive channel operator status.
- The assets window does not reload on all item moves if the assets window is open.
- Drone repair has been fixed.


**Combat**


- You cannot launch Defender or FoF missiles while your ships targeting systems are blocked.(Such as when coming out of cloak. This does not refer to being target jammed)
- A new criminal flagging system has been added into the game with multiple variables. You can now be criminally flagged towards a faction, corporation or a character. You can attack anyone who is criminally flagged towards you without having to fear a loss of security status, or police interference.
- If a character is criminally flagged, the flag stays active for 15 minutes *after* the criminal activity. The timer does not expire after jumping between solar systems. If the player commits another criminal act while the flag is active, the timer restarts.
- Aiding someone (Shield/Energy transfer modules) will result in criminal flagging. For example, if a character aids another character who is criminally flagged, the aiding character becomes criminally flagged to the same pilot. If a character aids an outlaw (-5 or less in security status), the character becomes criminally flagged to everyone the outlaw is flagged to. Finally, and if a character aids a member of corporation A, who are at war with corporation B, the character will be criminally flagged towards corporation B.
- When a character join a gang where a pilot is member of a corporation A that is at war with corporation B, the character in the gang is considered to be aiding those corporation A, and may be freely attacked by the opposing corporation B. Note that the character is not a part of the war per-se, as the character can not freely attack members of corporation B, but the character can be attacked by members of corporation B without consequence.
- Because of this new gang-corporation-war feature, there will now be a confirmation message when joining a gang that has a member at war with another corporation, informing you of the consequences of joining the gang.
- Until now there has been one message that pops up when an offensive module is activated, no matter the purpose. This generic message has been replaced with specific messages.
- Targeting mathematics have been optimized.
- The inertial phase of missile flight has been reduced.
- A new feature has been added to the in-space UI. The option to have your weapons auto-reload is now available in the weapons context menu.
- The period for which your targeting systems are blocked after cloaking now applies to non-targeted offensive modules. For example, using smart bombs when coming out of cloaking is blocked for the same time period as offensive modules.
- The issue where targets at extreme range could not be unlocked with the UI menu has been resolved.
- Corporation defense sentry guns will switch targets periodically.


**Navigation**


- Path finding routines have been improved.
- A stop button has been added to the in-space UI. This button will perform the same operation as selecting "Stop menu" from the ship context menu.
- Filtering of Bookmarks in F11 map has been fixed. It should show the correct bookmarks for each system selected in the menu.


**Modules and charges balancing**


- Due to a revision of accuracy, blasters have had their fall off reduced by 20%.
- Due to a revision of accuracy, large projectile artillery guns (280mm, 720mm & 140mm) have had a fall of reduction of -50%. Smaller projectile artillery guns (250mm, 650mm & 1200mm) have been reduced in fall off by -25% for the same reason.
- Frequency Crystals have had an increase in EM damage they cause, small crystals have been increased by 1 EM damage, medium crystals by 2 EM and large crystals by 4 EM damage.
- The fitting power needed for Tachyon Beam Lasers have been reduced.
- The fitting power required for Large Armor Repairers have been increased, this is to make ships focus on their racial based defence styles.
- The fitting power required for siege launcher has been increased.
- The Assault Launcher has been changed into a cruiser based anti-frigate missile launcher.
- All missile launchers are now specialized with regards to what missiles they can load. All launchers may load defender missiles as a default. Here is the list of the ammo that may be loaded into each type of launcher in addition to the defenders; Rocket Launcher = Rockets, Standard Launcher = Light Missiles, Heavy Launcher = Heavy Missiles, Assault Launcher = Light Missiles, Cruise Launcher = Cruise Missiles, Siege Launcher = Cruise Missiles and Torpedos
- MicroWarpDrives now give a penality to Signature Radius of ship, meaning that when the module is active, it will be easier to hit for turrets and faster to lock target upon.
- Low end Turrets within size classes have been boosted in Tracking Speed compared to the high-end turrets, for example the Light Electron Blaster has better Tracking Speed than Light Neutron Blaster.
- Turret Tracking Speed has been tuned down with the new Accuracy for Meta Modules to same level as the Turrets they are created from, all other Meta bonuses will stay as they were.
- Turret Accuracy has been altered so that bigger class guns will be having trouble hitting smaller vessels than that they were designed for, the fall off range of turrets that enables turrets to hit outside their optimal range has also been boosted, meaning that players will hit better than before outside their optimal range. We advise players to test the new accuracy with diffirent turrets before going into combat (Chaos Test Server is higly recommended for such testing).
- Torpedoes have been decreased in maximum velocity as their damage increases to a dangerous level with skills and ship bonuses.
- Light Missiles have been increased in damage.
- The minerals needed to manufacture missiles has been decreased by a whole lot, every missile type will be cheaper to manufacture.


**Ship balancing**


- The Dominix has been given an increase in its base drone capacity to 7500. The drone capacity bonus has been removed in favor of the capability to control 1 extra drone per level of the gallente battleship skill.
- Raven has been given an increase in CPU output and a slight decrease in Power output.
- Caldari ships have been given an increase in armor thermal resistance by +10% but a reduction in armor kinetic resistance by -10%. The Elite Caldari Frigates also have these changes to shield resistances.
- Gallente ships have been given an increase in armor kinetic resistance by +10% but a reduction in armor thermal resistance by -10%. The Elite Gallente Frigates shield resistances also reflect this change.
- The Kestrel Target Range ship bonus has been replaced with Missile Launcher Rate Of Fire and Missile Damage for Kinetic Missiles.
- The Caldari Ships: Blackbird, Caracal, Crow, Griffin, and Heron have lost the Hybrid Optimal Range bonus in exchange for a Damage Bonus with Kinetic Missiles.
- Ships with bonuses to Optimal Range on turrets have been increased from 5% to 10%.
- Amarr ships with capacitor usage reduction bonus for energy turrets have been increased from 5% to 10%.
- The Apocalypse, Armageddon and Megathron have been given an increase in power output for either defence capabilities with armor repairers. The Tempest and Typhoon have also been increased in power output, giving the option to choose either armor tanking or the ability to fit siege and cruise launchers.
- The Signature Radius bonus for the Interceptor Frigates has been lowered to 5% per level with the new Accuracy.


**In-Space**


- When a ship has been destroyed, CONCORD will also notify the character of the items lost.
- Drone accounting has been fixed. The number of active drones or drones being launched is tracked against the owner's skill. It should not be possible to launch more drones than allowed by the controlling skill.
- Depleting an asteroid with several mining lasers would sometimes results in errors and loss of some ore. This has been resolved.
- A problem with modules going silently offline has been resolved.


**NPC's**


- Bounties for NPC Pirates have been increased to counter longer time needed to kill them when using their defence capabilities.
- NPC Pirates will now be able to show their appearance at stargates in 0.0 to 0.3 security solar systems traveling between stargates with in solar systems.
- NPC Pirate Factions have set loose to their commanders to search for players within asteroid fields all around the world. These NPC's will some be fitted with Ultra-Violent weapons, take caution when encountering one of them.
- NPC Pirate Factions have officially started mining operations in asteroid fields, be careful when finding one as they will be heavily guarding their haulers.
- Guristas NPC Pirates are now keener on using Kinetic Missiles.
- NPC's have gotten their resistance types adjusted to get same effectness as hardeners, amplifiers and platings give player ships. The damage types the they are the most weak to are the most favored damage types by the race that they infest in Empire Space solar systems.
- NPC Pirates have been reduced in damage ouput to balance their new defensive capabilities.
- NPC Pirates now use Shield Boost and Armor Repair effects to defend themselves.
- Infestations NPC Pirates (besides the new Elite Frigate Pirates) have lost their warp scrambling effect and most of them stasis webifying effect as well. These effects will now be handled by new Elite Frigate Pirates operating in deep space, guarding bigger ships. **Note: This does not apply to mission pirates!**
- NPC Frigate Pirates in deep space have been replaced with new Pirates flying Elite Frigates similar to the Interceptor type, these Pirates will be handling stasis webifying and warp scrambling effects for their Corp mates in bigger ships.
- NPC Pirates in Asteroid Fields have been decreased in maximum size they can reach, this will be mostly seen by the reduced number of escourt vessels that are guarding bigger ships.
- NPC Battleship Pirates will now be more frequent in deep space.
- The NPC Asteroid Pirate distribution has been reconfigured to balance better value vs. risk of systems, some areas have gotten a little tougher (0.5 now has up to highest level frigate pirate for example). We advise players to explore a couple asteroid belts within systems by using the Warp-To-60KM function before starting their NPC hunting.


**Market**


- Notification will now be given when a player tries to sell an item on the market but fails to meet the required volume.


**Skills**


- All skills required for operating specific missile types have had their bonuses changed to missile damage bonus.


**Agents**


- The timer on some missions was ending prematurely (before the advertised time). This has been resolved.
- Some missions had issues related to destination and broken briefings etc. These have been resolved
- Minor fixes regarding the canceling research projects, and accepting blueprints have been made.
- Story Line Missions have been added.
- Agent standing issues have been resolved. It should now be possible to speak with high level agents. Also issues with aggression updates refreshing and overwrites have been resolved.
- Agent mission ships will react to players warping in at distances greater then 50km.
- A few multi-encounter mission have been added into the generic mission pool.
- One of the important kill missions will now reward the player with an implant. Before this change it was much harder recieving an implant from a kill agent than a courier or mining type of agent.
- Loot drops have been added to some mission npcs which didn't drop anything. This includes the "bounty hunter rookie".
- The mission "Eliminate A Pirate Nuisance" had it's briefing fixed, as it used to claim the mission involved only 1 npc pirate, while infact it involved 2.
- The amount of homeless / slaves / science graduates etc that players can recieve via missions has been reduced.


**Other**


- Sorting your Inbox by unread messages has been re-added as an option. The sender list also displays the number of total messages from a sender.
- Assets can be filtered by current region, constellation, or solar system.
- The End User License Agreement (EULA) has been updated to include clauses regarding account trading and character transfers.
- The corporation standing check for conquerable stations has been optimized.
- Sorting of transactions in wallet has been resolved.
