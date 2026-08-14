# Bloodlines Features, Improvements and Fixes

- **Date**: 2013-03-21T13:59:48.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/bloodlines-features-improvements-and-fixes-1
- **Tags**: #patch-notes

## Overview
Bloodlines Patch Notes Features Four new player race bloodlines are now available. This addition includes new character options, new artwork and new content including a tutorial mission for each bloodline. A number of fixes and code improvements have been made to reduce/eliminate stuck

---

**Bloodlines**** Patch Notes**

**Features**


- Four new player race [<fontcolor=red>bloodlines</fontcolor=red>](//www.eve-online.com/features/RedMoonRising/detail.asp#bloodlines) are now available. This addition includes new character options, new artwork and new content including a tutorial mission for each bloodline.
- A number of fixes and code improvements have been made to reduce/eliminate stuck issues. These include: - Checking whether a system is stuck/loaded prior to your being allowed to undock or jump into it (if it is, then your autopilot will deactivate and leave you at the gate).
  - Checking to see if the system is loaded when trying to log in just after a reboot (if you logged in space).
  - The map has a "travel advisories" option that will display systems that are known to be currently stuck.In all cases you will receive an explanatory error message.


**Ships**


- Right clicking while piloting a pod no longer causes exceptions.
- Carriers can now access their own ship maintenance and corp hanger arrays when docked.
- Storing a ship in a Maintenance Array will no longer leave the ship in space under certain circumstances.
- The Flycatcher description no longer lists a Precision bonus for Rockets.
- The Ship Maintanance Array of Carriers, Motherships and Titans is now ten times bigger.
- The Nighthawk's description now displays a bonus to Kinetic missile damage only. It incorrectly stated receipt of a bonus to all heavy missiles. Also, its cargo capacity has increased to 700m3.
- The capacitor capacity of the **Nightmare** has been increased to 4750.
- The Nidhoggur's EM armor resistance has been increased to 70%.
- The Absolution's rate of fire bonus has been fixed.
- The Sacrilege's armor has been increased, its shield has been decreased and its missile rate of fire bonus has been changed to medium laser damage.
- The Executioner description is now correct.
- The Breacher have been corrected and give 10% to explosive missile damage and 5% to thermal, em and kinetic instead of the reverse.
- Exhumers now get the 7.5% shield resistance bonus per mining barge level instead of just 5%.
- The Vulture and Nighthawk had incorrect shield, armor and hull values. All command ships have 20% more hit points than their tech 1 counterpart. The Vulture had this bonus twice whereas the Nighthawk had no bonus.
- The Hornet and Wasp had wrong mass attributes. The correct attributes are Hornet 3,500kg and Wasp 100,000kg respectively.
- The Vigilant is listed under the Thorax variations tab.
- The Huginn and Lachesis rate of fire bonuses are now applied correctly.


**Drones and Weapons**


- Drone targetting systems have received a firmware update to improve their target selection processes. They will now pick targets which have been directly involved in aggression with their owner as a result from their owner (or one of his possessions) attacking the target, or the target attacking their owner or one of his possessions.
- Drone MWD usage has been corrected. They will not 'forget' they are equipped with a MWD if a new target is assigned.
- "Move to Drone Bay" option for drones in your cargo hold will work only when you are within range of a ship hangar array.
- Mining drones now stop mining and return correctly when so ordered.
- All tech 2 turret ammo now require R.A.M.-Ammunition Tech instead of R.A.M.-Weapon Tech.


**Modules**


- All Damage Control modules now give bonus to hull resistances.
- Modules that are subject to the stacking penalty now have the positive and negative modifiers stacked seperately.
- Modules that are under the influence of the stacking nerf penality no longer share ranks with counter-modules, i.e. Tracking Disruptor are no longer affected by Tracking Computers.
- Large Shield Transporter II skill requirements have been increased to level 4 Shield Emission System.
- ECM burst is now be affected by electronic warfare, long distance jamming and signal dispersion skills.
- ECCM, Projected ECCM and Sensor Backup Array are now stacking penalized
- Electronic Warfare Battery now use the new chance based ECM system. Their optimal range is 200km and falloff range is 100km.
- Mercoxit Mining Crystals can no longer be fitted on "Modulated Strip Miner II" to reflect the description.
- Covert Ops and Recon Ops modules now have a time reduction bonus when recloaking.
- Drone Control Unit 1 has had its volume modified to be inline with other capital ship modules.
- Capital Remote Armor Repairers had incorrect skill requirements and the ship bonuses were not boosting the modules correctly. This has been resolved.


**Skills and Implants**


- Using the Hacking or Archeology skills to unlock a spawn container works as intended.
- The skill requirement for Small Tractor Beam I has changed from Graviton Physics level 1 to Science level 4.
- The description for Mercoxit Mining Lasers now displays the proper bonus of 60% per exhumer skill level.
- Whelan Machorin's Ballistic Smartlink implant now gives a +4% bonus rather than +1%.


**Player Owned Structures**


- Starbase production tabs no longer display incorrect values.
- Mobile laboratorys can be accessed and work as intended.
- Better formatting for the "New control tower anchored" warning mail has been added.
- Ships will no longer be ejected from a POS when launched from a ship array and the surrounding forcefield requires a password.
- Ships no longer become stuck if you logout after refitting at a maintenance array.
- Mobile Laboratory capacity has been increased from 100m3 to 2000m3.
- The manufacturing and research times for Assembly Lines within Starbases and Outposts have been improved as an incentive to use them over standard station services.


**NPCs**


- Police response/pursuit have significantly improved, primarily the timer controlling CONCORD reactions to a crime now matches the agression/criminal flag timer displayed in the UI.
- NPCs in asteroid belts can no longer be forced into a non-aggressive state.
- Military faction police have reviewed their manuals, and updated their KoS lists. If you have a faction standing of -5 or worse, they will now attack you.
- NPCs have taken training courses in how to use ABs/MWDs correctly, and now use them more effectively.
- Police ships will be less likely to get stuck on the stargates/stations they are guarding.
- Jam timers when under the effects of NPC jamming display properly.
- Fixed a number of npcs that had a missile effect and no missile type assigned, or vice versa.
- Sentry Drones are no longer limited to a 100km attack range.
- The interceptor drones: Guardian Veteran, Angel Webifier, Angel Viper, Blood Disciple, Sansha Berserker and Sansha Demon have been fixed.
- Reports indicate that Sansha's Nation have corrected the design flaw in their tracking disruptors, and these are now working correctly.


**Science & Industry Improvements & Fixes**


- S&I installations will now list where they are located.
- The S&I progress bar will now clear if a job fails to install.
- Delivering a Manufacturing job when you are not in a ship will no longer fail.
- Blueprints will now be returned to impounded items if an office is unrented before a corp job is delivered.
- All S&I jobs are limited to a maximum of 20 **copies** to prevent excessive load being caused when delivering the job (1 copy with 100.000 runs is no problem while 100.000 copies of 1 runs is).
- Options/warning messages have had more descriptions added.
- Personal/Corp blueprint displays have been upgraded.
- Slot queueing now warns about queue issues.
- Quotes now display total job time and the estimated completion date.
- Base production time now displays correctly on BPs with Production Efficiency research.
- Error messages have been corrected or improved regarding incorrect S&I corp roles.
- S&I Assembly lines in 0.4 and below Stations are now configured to build deployables such as Mobile Warp Disruptors.
- It is now possible to cancel jobs. This will not have an effect on the start time of already queued jobs.
- Command Ship Blueprints are no longer missing R.Dbs for ME and PE research.
- Some manufacturing facilities have received time and material multiplier adjustments:


**Market and Market Interface**


- Market Range filter updates properly when undocking.
- Pressing the Market button will close the panel if its open (or maximize it if its minimized).
- The 'Drone Upgrades' market group has been moved from 'Turrets & Bays; Weapon Upgrades' to the 'Drones' market group.
- New General Freight Containers have been seeded on the market throughout the galaxy. These containers fit in Freighters and allow pilots to organize their shipments.
- Capital Remote Armor Repair System I, Capital Energy Transfer Array I and Capital Shield Transporter I Blueprints are now available on the Market.
- Capital Remote Armor Repair System I, Capital Energy Transfer Array I, and Capital Shield Transporter I Modules are available on the Market.


**Agent and Mission Improvements & Fixes**


- Faction standing of 1 is now required to speak with the Event agent located inside the 'newbie stations'. This is to encourage players to complete the tutorial, which will reward players with the prerequiite 1 in standing to their race's faction.
- A number of missions from the pre-Exodus system have been ported to the new system.
- Implemented the missions 'Worlds Collide' for level 1 and 4 non-pirate agents. The level 4 version only applies to agents located in 0.4 security and below.
- The reward in the bonus level of the level 3 version of Angel and Guristas Extravaganza have been improved, but the difficulty of the encounters have been increased.
- The frequency between spawns in some missions with 'wave-spawns' has been decreased.
- The Navy force in 'Portal To War' (2 of 5) takes longer to appear.
- Jakon Tooka appears with a little less predictability.
- Maschteri Markan appears a little more often and an encounter in his hideout has been added.
- The shipyard in the 3rd 'Governor's Aide' mission is now invulnerable. Destroying it before the final entitity had been destroyed prevented mission completion.
- The mission 'The Seven's Prison Facility' will no longer require you to actually destroy the prison. Instead it will only require you to destroy the npcs guarding it as is mentioned in the mission briefing.
- Agent mission default bonus rewards will no longer offer civilian modules or charges.
- The mission 'Illegal Activity' (2 of 3) has been fixed.
- The static complex in Traun now drops the item needed to complete mission #3 in 'Ghost War'.
- The reward drop in mission #4 in 'Business Associates' now gives the 3 ship logs, necessary to begin 'The Forgery' mission sequence.
- The difficulty of 'The Uprising, 4 of 4' has been reduced.
- The mission objective for 'Save a Man's Career' has been modified.
- The objective in mission 5 of 'Human Cattle' has changed slightly and the objectives are completed before you warp into the final room, rather than after you destroy the lone frigate at the beacon in the final room.
- The difficulty of the level 3 'Intercept the Pirate Smugglers' mission has increased slightly.


**Chat Fixes & Improvements**


- Text alignment issues where the Eve System messages would wrap incorrectly no longer ocur.
- An issue where a message containing pasted text would drop the pasted text when enter was pressed no longer occurs.
- Copy/Paste will now select the correct text.
- Double click selection of a word no longer drops the last letter.
- Shift+Enter will allow multiple lines to be entered into chat.
- Linking to ammo now works correctly.
- Copying links will no longer convert '&' into its HTML counterpart.
- A number of errors caused by using unicode characters in chat have been resolved.
- Copy/paste from logs will no longer include colour tags.


**User Interface**


- Drone icon rendering has been improved.
- The Eve System icon has been changed.
- Added various new and missing types to the variations tab to the show info display.
- Cursor focus will no longer switch when using client dropdown menus.
- Closing a window before its loaded no longer causes exceptions.
- The Corp Voting box size has been increased.
- Layout of the location/autopilot information has been improved.
- The format displayed for Accept payment for clone purchases have been improved.
- Keyboard shortcuts (eg ctrl-a) have been added to the Market Search.
- Pinned windows will retain their pinned status after a client restart.
- Lag created by using the right click menu has been decreased.
- 'Turn off damage message displays' option has been added to the Escape menu. This will improve combat when engaged by multiple hostiles.
- Moon/roid belt icons will display when ALT is pressed.
- Targetting arrows no longer pass under the health bars.
- Drone bays are no longer accessible in space via a keyboard shortcut.
- Buddy list online/offline indicator has been fixed (again).
- Removing someone from your buddylist will also remove the online icon from that character's portrait.
- An option to view deadspace complex locations has been added to the galaxy map.
- Ctrl+Space will now cancel a warp+dock request.
- Strip miners are now displayed correctly when in stations.
- The Moon Scan window displays properly.


**IGB Fixes**


- A fix for background removal has been added to the IGB.
- Forms in DIVs will now submit properly.
- Improved form submission, button selection and button clicking in the IGB.


**EVE Mail**


- Using '\n' to add returns to evemail and evemailto links has been resolved.
- Corp mail errors caused by joining a new corp should no longer occur.
- Quitting a corp/alliance no longer leaves you subscribed to the alliance mailbox.


**Miscellaneous**


- GM tools for detecting and banning macro'ers and other evildoers have been added and improved.
- 16 new jumps have been added, and 3 jumps have been shifted as part of the optimizations for high-load systems.The shifted jumps are: - Rens <> Onaga
  - Oursalert <> Alentene
  - Hedion <> Tash Murkon Prime
- The new jumps are: - **Rens area** - Odatrik <> Abudban
    - Onga <> Gyng
    - Avesber <> Abudban
    - Frarn <> Rens
    - Ivar <> Trytedald
    - **Jita area** - Kaaputenen <> Kamio
      - Halaima <> Sarekuwa
      - Uedama <> Juunigaishi
      - Juunigaishi <> Ikao
      - Litiura <> Elonaya
      - **Oursulaert area** - Tar <> Merolles
        - Pakhshi <> Synchelle
        - Oursulaert <> Mies
        - Oursulaert <> Pakhshi
        - **Amarr/Ashab area** - Tash-Murkon Prime <> Bhizheba
          - Romi <> Bhizheba
        - Combat improving code optimizations have beed added.
        - Cargo containers that do not belong to you are now yellow, not red.
        - The Server FAQ button no longer displays when selecting Tranquility upon client startup.
        - Engine trails have been modified.
        - Autopilot will be disabled if it attempts to warp while you are warp scrambled.
        - Trying to jump while still in warp will no longer cause an error window to appear.
        - You can now set the default of Station Containers to locked/unlocked.
        - Loot rights: - When someone explodes and the contents of their ship that are not destroyed are jettisoned, the right to loot the containers used to store these contents is given to the people that someone is aggressionflagged towards. If they are criminal flagged (aggression flagged to everyone) then everyone can loot the container. If that someone is aggression flagged towards corporations, members of those corporations have a right to loot the container. If that someone is aggression flagged towards certain pilots, those pilots have a right to loot the container.
          - **Note:**When loot is stolen, gang members of the victim of the theft used to have the thief criminal flagged towards them. This is no longer true. Only corporation members (if the victim is in a corporation) or the victim themselves get the thief criminal flagged towards them now.
        - Kill rights will now expire after ~30 days.
        - You can now defend yourself when being attacked by someone with a Kill Right on you.
        - Only 1000 items can now be stored in a single location. A location is any location you can store items in. A container is also a location so you can have 1000 containers containing 1000 stacks of items each. Stacks are NOT limited, you can have 1000 stacks of 10 million trit. This is to address database performance issues resulting from a high number of items in the same location.
        - The planet Saisio III has been renamed to Saisio III (Achura), as Achura has always been its more common name of reference.
        - Flickering / Black screening on character selection page no longer occurs. **Fixed via hotfixes since last patch** - Location Agents
        - Sovereignty no longer includes towers online for less than 5 days.
