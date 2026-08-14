# Improvements and Bug Fixes

- **Date**: 2013-03-21T14:10:18.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-49
- **Tags**: #patch-notes

## Overview
UI fixes and changes Introduction movie text-strip shader has been made smaller. The font rendering engine has been changed and minor adjustments made to the font to make it more readable. An issue with assigning corporation roles via the role management interface in the corporation w

---

**UI fixes and changes**


- Introduction movie text-strip shader has been made smaller.
- The font rendering engine has been changed and minor adjustments made to the font to make it more readable.
- An issue with assigning corporation roles via the role management interface in the corporation window has been fixed.
- An issue with saving of usernames and password if either consisted of numbers only has been fixed.
- Flagged jettison and loot containers will now get a red icon instead the standard white one.
- Buddy list showing wrong online/offline status has been fixed.
- Now cancelling a docking request that requires warping, also cancels the warp.
- Minimized "Show info" windows do not pop up anymore, when the data in them is updated.
- Spelling error in alliance war declaration mails has been fixed.
- Odd clipping of text in the "Edit member" window has been fixed.
- You can now use enter to confirm search in assets.
- Asteroid belt triangle icons are now showing up in space again.
- Market price history graph has been fixed.
- A bug with starting and stopping auto-repeated modules has been fixed.
- Wrong error message when forming a gang then instantly making some one else leader has been fixed.
- Overview state filter settings now also apply to pilots' cargo containers
- The market menu entries have been removed from the drones right-click menu in the drone overview..
- Cargo container names now update in the overview.
- The cursor does no longer blink in the notepad when it doesn't have focus.
- Corporation /Accounts/Deliveries now allows autopilot destination to be set from it.
- Wallet journal page 2 does no longer miss entries.
- "Put station services on top of other windows when clicked" option no longer disappears when "Load station environment" is clicked.
- Role management window no longer stops redrawing.
- A case where an incorrect name appeared in the targeting square has been fixed.
- Ctrl+Tab now works to remove and reshow the UI
- Deleting folders in the notepad is fixed
- Corporation description no longer showsinstead of a new line.
- An error that occurred when a gang leader tried to tag a player capturable station has been resolved.
- Emote no longer puts star after the players name. The star has been put in front of the name again.
- *Few issues with character portraits have been fixed.*
- *Unicode changes could cause stuck issues if items were named with unicode characters. Now you can only use cp1252 in item names.*
- *Channel password window does not stack with other windows anymore.*
- *Character description in character creation does no longer get stuck on-screen.*


**Effect system fixes**


- Jumpgate sound effect has been fixed
- Disabling and re-enabling effects using CTRL-SHIFT-ALT T and E now disables turret and other effects correctly, but correctly displays effects that are not supposed to be disabled, like cloaking and stargate effects. - This is wrong. See next item
- *Effect for stargates when people jump in is back.*
- Cloaking sounds and animation are fixed and don't get interrupted during jump.
- Effect bug with mining drones is resolved.


**Science and industry**


- Access control for manufacturing and research has been fixed. To install a corporation job you now need the factory manager role and at least view access to the blueprint and materials.
- Advanced Laboratory Operation skill now works.
- Number of production runs on a copy job is no longer truncated on display.
- Installing a drone blueprint into a drone assembly is now possible.
- When trying to install a Tech level 1 large ship blueprint into an advanced large ship assembly array you no longer get an error.
- Selecting multiple jobs in progress doesn't show deliver button anymore.
- A few cases where installing manufacturing job failed have been fixed.
- Remote installations over node boundaries now work correctly.
- Motherships moved to their own group and carriers have been added to assembly lines in stations in 0.4 and below.
- *You can now see more details for blueprints in the S&I interface.*
- *It is now possible to see what an assembly line is capable of producing.*
- *R.A.M. and R.Db blueprints are being seeded.*


**Ships, modules and skills**


- Drone Navigation Skill now no longer gives bonus to orbit velocity.
- Repackaged volumes of the three new tech II ship groups, elite versions of destroyers, battlecruisers and mining barges has been fixed.
- Fixed penalties on advanced turret ammo. The Hail was actually giving a bonus and small ammo wasn't giving more penalty than large.
- Advanced pulse laser ammo blueprint fixed so it's more in line with other tech 2 ammo.
- Damage control can now stay active and can be activated in warp.
- *Small Tractor Beam blueprint set to 15 million ISK(10x more than the material cost of one module)*
- The smaller EWar drones should now orbit at more reasonable speeds.
- Tracking on Wasps has been fixed.
- *Covert Ops and Recon Ops now have a time reduction bonus to recloaking.*
- *Mercoxit mining crystal can no longer be fitted on "Modulated Strip Miner II " as the description says.*
- *Mining upgrades skill now gives correct bonus.*
- *Magnetic Plating I no longer require Vizian R.Db to research.*
- *Rapier target painter bonus is now working.*
- *Gleam S now requires level 2 hydromagnetic physics to manufacture.*
- *Tech 2 turret ammo wasn't giving more penalty to the smaller turrets than the large ones. Now it is.*
- *Mackinaw now has the right description on it's bonuses*
- *Ice Harvesters now give the correct bonus.*
- *Reactivation delay for few modules is now saved between system jumps so they can not be reactivated until the timer is over. Modules in question are cloaking device, **siege module** and doomsday device.*
- *Most of the tech 2 ammo had bugged manufacturing time, copy time and or research time was bugged and has been reworked. It is now more in line with tech 2 modules and ships.*


**Agent missions and deadspace complexes**


- Added the 4 mission sequence The Uprising, for pirate level 2 and 3 agents.
- Courier agent missions were giving out untransportable items, this has been fixed.
- The mission sequence "illegal activity" will now only be dished out by the Amarr-Caldari faction block.
- The faction ships for ISK offers aren't as ridiculously expensive anymore. - This was already in build 3796
- Added agent offers which dish out Empire charters needed to build starbases in Empire space.
- Zor now has a very slight chance of dropping Zor's Custom Navigation Hyper-Link. - This was already in build 3796
- Thirteen deadspace training complexes have been added - two in Amsen and one in every other home system.
- Mazed Karadom (an agent of Amarr origin) was added to the Carnival agent site in Barkrik.
- Karhoum Ykta, the Sansha Envoy, has been relocated into his phantasm.
- Zaknar Cente, of The Syndicate, has been relocated into his Tristan.
- The agents Erudin Hanka and Hann Najus have been placed into their appropriate station.
- The sequences "In the midst of deadspace" and "Technological secrets" have had their difficulty decreased.
- Added an extra boss spawn in exchange for a few generic battleship spawns in the 8th and final mission of the Audesder Incident COSMOS/Cold War sequence.
- *Spider Drone II's will now web you and possibly warp scramble.*
- *Some of the new missions which came in RMR have been tuned down in difficulty.*
- *The Rogue Drone Harrassment mission description has been edited to be intuitive. People were getting stuck here as they didn't notice the acceleration gate leading to the next deadspace room.*
- *The Enhanced Decoding Device which is part of the King of the Hill COSMOS mission sequence no longer requires Mythos parts to manufacture.*
- *The NPCs in the COSMOS mission Governor's Aide (3 of 4) will no longer respawn. (Do not confuse respawn with 'additional wave'.)*
- *The mission Illegal Activity will no longer be dished out by Gallente Federation or Minmatar Republic agents.*
- *Fixed the mission "intercept the saboteurs" so that it no longer sends Guristas and Sansha's Nation agent runners to kill Blood Raiders.*
- *Locator agents are fixed.*


**Miscellaneous**


- Autopatcher has been changed to work with our new patch servers and to be compatible with the unicode changes.
- Various load balancing changes have been made in an attempt to decrease lag in peak times.
- A long standing deadlock issue has been addressed. This will hopefully decrease the frequency of stuck issues quite a lot.
- Market history and order lists have been optimizied to transfer less data.
- The ability to anchor/online reactor arrays in a 0.3 system has been fixed.
- *Control tower reinforced timer when owner holds sovereignty is fixed. The tower should now consume all the strontium clathrates.* *This fix was rolled back, because of a bug in it. A proper fix will be applied as soon as it passes testing.*
- *It is no longer possible to anchor or online starbase structures when the control tower has less then 50% shields.*
