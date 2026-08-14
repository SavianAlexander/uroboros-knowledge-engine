# Improvements and Bug Fixes

- **Date**: 2004-07-06T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-41
- **Tags**: #patch-notes

## Overview
Bug Fixes and Improvements   Gameplay The maximum standing limit has been increased to 300 standings and a notification has been added if you are at the limit. Members of an corporation now have default 10 standing towards their corporation. This was done to allow the use of your

---

**Bug Fixes and Improvements**

**Gameplay**


- The maximum standing limit has been increased to 300 standings and a notification has been added if you are at the limit.
- Members of an corporation now have default 10 standing towards their corporation. This was done to allow the use of your player corp's POSs without specific standing entries.
- Added an option to "never join a gang" if the block pilot option has been selected.
- An error in the gang accept code while changing sessions has been resolved.


**Navigation**


- The docking and undocking sequence code has been strengthened. Players should have less chance of geting stuck while docking or undocking.
- A safety check has been added so waypoints can only be set to planets, constellations or regions. This addresses the "set destination to asteroid field and kill map" bug.
- The autopilot is switched off now when stop button is clicked.
- Improved autopilot handling, where it disabled itself at first gate after CTD or logging off.
- You can no longer cloak if objects are within 10km. Entering this 10km buffer around other objects results in decloaking. Please note that these changes are temporary in order to deal with an exploit.


**Combat**


- Missiles will no longer explode when impacting objects other than what the targetted entity or objects owned by the targetted entity.
- In certain instances, unbelievable amounts of client-side lag would result 15 minutes after an aggressive act was performed. This has been resolved.
- The "cloaked while actually uncloaked" display bug has been resolved..
- The person that did the most damage to an opponent after combat encounter now also receives a kill mail.


**Modules**


- You can view the detailed notes on turret changes by copying and pasting the following URL into your browser address: //myeve.eve-online.com/ingameboard.asp?a=topic&threadID=91916&page=1
- Hybrid Turrets and Laser Turrets have had their capacitor usage tweaked. Medium and Small Turrets from these groups have had a capacitor usage decrease and now have up to two decimals in capacitor usage to modify the damage per capacitor per second.
- All Projectile Ammo's (besides EMP and Phased Plasma) have been increased in damage. Selecting less damaging charges was not as fruitful for projectile users as is for hybrid or lasers users.
- The Tempest and Megathron have received an increase in their power grids.
- AutoCannons / Repeating Artillery fall off range has been combined into the same value to compensate for the lack of damage per second when compared to hybrid and laser turret gain with less capacitor usage.
- Tachyon Beam Lasers now have better optimal and fall-off ranges.
- Medium Beam, Heavy Beam and Mega Beam guns have had a damage increase.
- Dual Light, Focused Medium and Dual Heavy Beams have been given an increased optimal range.
- Blasters' fall-off range has been reduced, but their tracking has been improved.
- Pulse Lasers have been given increases in damage and in optimal range. These turrets should now be a very viable option for Laser users.
- Battleship pirates and commanders have had an increase in defence output.
- Signature Radiuses for frigates, cruisers and some battleships have had a decrease in relation to tracking speed tuning.
- Tracking Speed for turrets has been adjusted. Turrets used against ships of the proper class or larger (ie large turrets against battleships, medium against cruisers and battleships, etc.) will be more accurate than before. However, ships of a smaller class than the size of the turret being fired will have an increased hit difficulty.
- NPC's with stasis webifiers now slow target's velocity at the correct rate.
- All modules that are not size classed in Power requirement have been set to 1. This will ease fitting these modules on Frigates.
- Standard Frequency Crystals no longer drop from NPC's.
- Damage seeping through NPC armor to structure and NPC ship destruction with structure remaining has been resolved.
- The Small Neutralizer I has been returned to its previous statistics.
- The Ibis ship hybrid optimal range bonus and the Impairor laser turret capacitor need bonus have been increased from 5% to 10%.
- Various power manager modules such as Power Diagnostic were affecting the shield boost bonus of Shield Boost Amplifiers and the penality of Capacitor Power Relays. The additional effects no longer occur
- The mass of Amarr frigates has been corrected.
- Deep Space frigate NPC's have had their damage-type immunities removed.
- Medium Armor Repairer II has been decreased in CPU need from 50 to 25. Large Armor Repairer II CPU required has been decreased from 90 to 50.
- Addition: 650mm and 720mm Projectile Artilleries fall off has been corrected.
- Addition: Few rare drop Missile Launchers had incorrect CPU requirement.
- Addition:Shield Booster, Shield Hardener, Armor Repairer, Armor Hardener, ECCM, Tracking Computer, Hull Repairer, Capacitor Booster and Sensor Booster can again be operated while in warp.


**Agents**


- The lack of a cargo container drop in tutorial mission 6 has been resolved.
- NPC pirate set-up in kill missions have been fixed.
- The important implant courier mission has been enabled for level 1 and 2 agents. The reward is a lesser quality implant than the level 3 version of the mission.
- A few named mission npcs now have a small chance of dropping an implant.
- The mission "Failing Pirates comes at a cost" will no longer give the player a slight faction penalty for destroying the target, towards the faction that he's working for.
- The mission drone security status gain has been tweaked for named NPCs, they should give more security status on average when destroyed.
- Security standing gain for Empire faction drones in agent missions has been fixed, i.e. they no longer give any standing.


**NPC**


- When convoys reached their destination, they were assumed to dock but their ships were never removed from space. They will now properly dock at their destination.
- The Arch Angel Ambusher now uses the correct missile types when engaging.
- NPCs have had signature radius, turret value and accuracy changes made.
- Addition: NPC's that used Blasters, AutoCannons and Artilleries have been corrected in fall off.
- Addition: All NPC's are now unjammable.


**Communication**


- Scalability of chat channels have been improved.
- Setting a channel to invite-only would cause an error and often not work. This has been resolved.
- The chat logfile is now written on the fly. All chat messages are written to the file immediately. This resolves the missing chat log issue.
- Chat channels show join/leave messages now. You can configure this feature in the right click menu of each channel.


**Other**


- Strengthened client session change management.
- There was an issue with trading caused by players trading a number of times on the same station. This has been resolved.
- If a character that was in a station with the agents list open by default, the available-to-you status was incorrectly displayed as if you had 0 in standings and incorrect "Show Transactions" and "Show Compositions standings" right-menu options were displayed. This should no longer occur.
- The restriction to corp/character settings if more then one escrow mission was added in a row has been resolved.
- The usage of digit and decimal separator in format ISK function has been changed to assist players who have set decimal to ',' and digit to '.'.
- An over/under market average pop-up warning has been added to market quick buy/sell. You will now be warned if you try to purchase an item far above or sell an item far below the average market price.
- The sound issues with the audio library have been resolved.
- The lack of proper security rating display on the character sheet has been resolved.
- The corp ticker search feature has been repaired.
