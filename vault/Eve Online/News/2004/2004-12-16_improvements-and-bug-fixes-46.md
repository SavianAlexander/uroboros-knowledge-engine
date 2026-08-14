# Improvements and Bug Fixes

- **Date**: 2004-12-16T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-46
- **Tags**: #patch-notes

## Overview
Drones, Modules and Ships You should now be able to scoop up drones left behind from other players. Active smartbombs should no longer send an error message when dragging them between slots while activating them. Smartbomb area of effect is now in proportion to the displayed effect ra

---

**Drones, Modules and Ships**


- You should now be able to scoop up drones left behind from other players.
- Active smartbombs should no longer send an error message when dragging them between slots while activating them.
- Smartbomb area of effect is now in proportion to the displayed effect radius. Smart bombs were left behind a moving ship and retained the orientation of the ship that deployed them.
- Strip mining lasers will now autorepeat.
- Passive targeting now has client-side support and should work properly.
- Defender Missiles should not slow your ship when fired.
- Fixed certain combat modules that did not display a range bubble in the tactical display (Warp scramblers, Neutralizers etc.)
- An issue where module fitting would cause the module to use its unmodified power cost, rather than the cost reduced by skills and other modifiers.
- Autorepeat is now ON by default.
- Ships undocking from a Starbase Ship Maintenance Array now align themselves with the forcefield harmonics and are no longer ejected far outside the forcefield.
- Using an Afterburner or a MicroWarpDrive that has a thrust bigger than the mass of your ship will not work as well as before. A ship fitted with too large a module will take longer to climb to maximum velocity and maneuverability will decrease.
- Afterburners have been given a speed boost increase when the module is activated, the boost is now up to three times more than before. Afterburner capacitor need for activation and power requirement for fitting has been increased as a balancing factor. Afterburners are also limited to one pr. ship like Microwarpdrives are.
- Modulated Deep Core Miner II's and Strip Miner II's are now available from research agents.
- The ranges of various scanner modules have been increased. For example, cargo scanners now have a 50KM range and can be used in Deadspace and Belt pirate hunting to check loot cans for phatness. Survey scanners have range equal to most miners. Ship scanners range has been increased to 50Km, thus increasing their ability to analyze enemy ship fittings.
- Rounding errors caused by numerous attempts to warp with less than full capacitor were preventing a player from warping at all. This has been resolved.


**Agents and Missions**


- The ratio of Deadspace missions versus normal missions given by agents has been adjusted.
- Some agents were hardcoded at level 1, this has been fixed.
- Level 3 agents will no longer send players to level 1 storyline agents.
- Agent standing bonus given after mission completion has been adjusted, some were giving the same for all missions.
- It is no longer possible to complete a mission in space. You must talk to the agent to complete the mission.
- Some pirate storyline mission destinations were over 50 jumps. These have been reduced.
- Agent offer dialogs have been modified to reduce confusion. It is now possible to view the offer information before accepting or declining.
- It shouldn't be possible to accept an offer from an agent you don't have standings to talk to.
- If a courier mission involves a Conquerable Station, a warning popup will be sent to anyone accepting the mission.
- Agent rewards calculations have been adjusted. Some missions will have increased rewards in ISK and Loyalty Points while others might have less.
- Some Agent Offers have been adjusted based on Loyalty Point accumulation. This is most notable with Faction ship offers and Implant offers.
- Some agent offers now include mining crystals.
- Ancient Acceleration Gates should limit access according to ship class restrictions. A new pop-up message will display valid ship classes when activating the gate.


**Corporations, Alliances and Gangs**


- Notifications for issuing changes to votes or sanctioned actions will now be sent to shareholders, including those that are not corporation members.
- The role Security Officer no longer has the ability to see the contents of the Deliveries window or to take items from it. There are also more checks being made client side to ensure that the player opening the Delivery window has the roles to do so.
- Error messaging when creating corporations should now be more concise.
- Alliances can now set relationship standings to other alliances.
- The voting option after a CEO resignation is now functioning properly.
- A corporation can now see what it has in Delivery waiting for pickup. It is next to the impounded items view in the corporation window accounting / assets view.
- Multiple evemails were sent on war declaration against an alliance. The first was a war declaration, followed by 2 retractions. 24 hours later, the wars went live as normal. The retraction notifications have been removed.
- A Corporation in Alliance can resign from the alliance without being the Executor.
- War type detection and start-up cost calculation have been fixed.
- The role "Trader" has been added to allow selling and buying from corp wallet without having full access to the wallet like "Accountant".
- Gang war join confirmations for both the inviter and the invited should now check for and warn of alliance wars.
- When a gang member disconnects, if he is the second to last member of the gang, the gang now disbands.


**Market**


- Fixed a rare case which usually ended with rendering a market region useless for the duration of the uptime.
- Market Escrow 'Total' & 'What's Left' amounts are now shown in the Wallet.
- Fixed the transaction tax, it was not levied for any sales.
- Market history graph should no longer chop of left price numbers.
- Changing back to simple buy menu from the advanced menu stated no one was selling the items any more on the market. The simple menu now displays correctly.
- In some cases, modification of market sell orders were bugged, the duration of the order was reset.
- The 'advanced place order' option now has a detailed market info button.
- Transaction tax is now correctly influenced by the Accounting skill.


**Stations and Structures**


- The Retrieve Password on Station container mail now includes the password.
- Conquerable station now have the correct number of offices available.
- The control tower going offline while there was a structure unanchoring will not leave the starbase in a bugged state.
- Silo's should not attain an invulnerable state under any circumstances.
- Double clicking an item in Reprocessing should bring up quote again.
- Station containers with log entries are no longer trashable. Log entries need to be removed before trashing the container.
- The option to assemble a packaged ship located in your station via the asset window has been retained.
- Some structures were able to evaluate more than once per cycle in moon mining. In some cases this caused extra consumed materials to be removed and reactors to function at double speed. This should no longer occur.
- Corp hangar array capacity has been increased from 100k m3 to 200k m3.
- Intensive Refining Array (dedicated refining platform) are available for purchase from NPC corporations. Statistics include a 3 hour processing time, increased anchor and un-anchor times, and 200k m3 capacity with 75% yield with full skills.
- Standard refining array yield changed from 25% to 35%.
- Refining Arrays now have 100% yield for ice refining with full skills.
- Empire racial ice improved slightly for isotopes, but decreased for Heavy Water and Liquid Ozone.
- Other Racial ice isotope yield improved significantly, equal to sub-empire standards. Heavy Water and Liquid Ozone yield higher than empire.
- Control Tower capacity decreased to 50k. An associated change to volume of ice products has been made for slightly easier transport.
- Conquerable station shield capacity and shield recharge rate increased to roughly equal Control Tower statistics.
- Starbases now send kill mails to the owner if it shoots another pilot or gets destroyed.


**Bookmarks**


- Creating bookmarks in space through People & Places does not show Region, Constellation or Solarsystem of the bookmark.
- Bookmarks created on a cargo container now have a "warp to" range option.
- It is no longer possible to move bookmarks into your cargo while cloaked. This is because you cannot add anything to your cargo while cloaked.
- Newly created bookmarks in space should display properly in People & Places.


**User Interface**


- The Overview is now able to filter out entries based on states under Overview Settings -> Filters -> States and unchecking the state you want filtered out.
- The Overview can optionally use small color tags instead of icons. This is configured via Overview Settings -> Appearance -> Use small colortags.
- Overview now shows 2 settings for positive standing similar to the negative standing display.
- The Fast Action circular menu now has an option to select "click and drag" movement with the left or middle mouse button. The option can be set via the ESC menu.
- Alt-Left-Clicking on an item is now "Look at". Alt-Left-Clicking the HUD or empty space resets camera.
- A looping graphical effect should stop if the culprit module is set to offline.
- Emulated scissoring has been added to the UI. This should fix the following defects; various texts displaying outside a window, modules display outside hangars and column highlighting is visible outside its window.
- "Put station services on top of other windows when clicked" is now an option via the ESC menu.
- The assets window will show detailed stack amount.
- Autohide of the Neocom works properly.
- Scrolling within the Address book works properly.
- Ctrl-click to target no longer interferes with the Fast Action menu.
- The Scanner Panel - Survey Probe expiration counters updates properly if panel is minimized and restored.
- Ingame browser elements (forms, evemail-links) inside tables work correctly.
- Customization of color tagging in Overview is now possible through the Overview Settings.
- The size of the default info/warning notify popup has been increased.
- You can now sort emails by "Unread".
- You can now change order of the Overview columns in the Overview settings under Columns.
- Overview is no longer minimized by default when undocking.
- The Type selector in Overview settings no longer jumps to top on each selection.
- Range scanner correctly scans 360°.
- Mobile Warp Disruptors display in the Overview.


**Insurance**


- Basic insurance of the Retribution has been resolved.
- Accountant role is no longer required to insure your ship in a station which your corporation holds an office.
- Double clicking in space would approach wrong destination because of double click timer. This should no longer occur.
- Ships should now fly straight after orbiting instead of stopping.


**NPCs and Contraband**


- Deadspace Overseers and other Deadspace Complex objectives now have their own group in the overview.
- Rogue drones brackets are now red like NPC pirates.
- Undocking now checks if you have contraband in your ship which is illegal in the solarsystem you are entering and pops up a warning if present. It can be suppressed **at your own risk**.
- Contraband fines appear in journal entries with the correct description.
- Customs police recursively scan cargo, including inside ships carried in your cargo now.
- It is no longer possible to create a courier mission containing any contraband.
- High end Contraband Offers and their rewards have been adjusted and are now enabled.
- Spawn container refilling has been resolved.
- Frequency of loot drop in deadspace has been increased.
- Maximum possible velocity of NPCs in deadspace has been decreased to compensate to the velocity of players using afterburners.
- CONCORD now has their own Customs surveillance force.
- Entity target selection problems have been resolved. Under certain circumstances, they were miscalculating and not selecting a new target after the target they were engaging became ineligible for continued attack. This applies to NPCs and Drones.
- Deadspace entities will now maintain proper distances from the object they are guarding.


**Miscellaneous**


- A deadlock issue which caused the client to crash has been resolved.
- Mining Barges turrets display correctly when in hangar.
- Implants such as "Hardwiring - Eifyr and Co. 'Rogue' CY-1" now add the correct bonuses.
- Various server side load optimizations have been made.
- "Read news" popup function on billboards now functions properly.
- Maximum characters in item icons now displays an "M", for values of a million or more.
- 32bit BMP (screenshot format) have been changed to PNG to support more programs.
- Zoom view on your ship should no longer reset after each jump/session change.
- Secure Cargo containers have a "Set Configuration Password" option available.
- Session change messages now display time remaining.
- Targeting countdown time and icon appears when targeting asteroids.
- R.A.M. damage occurs as intended during manufacturing.
- "OnLSC waiting until join channels completed" should no longer occur.
- It is no longer possible to open containers when they are in deliveries. This was not an intended feature.
- Explosions were missing on drones / rogue drones. They now go "boom", or perhaps more like "kaplow"?
- The character sheet display should no longer glitch when starting a new skill.
- ‘Refining Yield Penalty’ has been renamed to ‘Refining Yield’.


**Known Issues**


- Colorflags for personal standing agains NPCs are not functional in this build.
