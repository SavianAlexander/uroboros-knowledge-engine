# New Features, Config Changes and Bug Fixes

- **Date**: 2003-08-14T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/new-features-config-changes-and-bug-fixes-8
- **Tags**: #patch-notes

## Overview
New Features / Configuration Changes and Bug Fixes   In Space Security officers in empire space have gotten upgraded ships and will be quicker at dealing with outlaws when they enter secure empire space. Cargo Containers dropped of NPC's and players have gotten increased in h

---

**New Features / Configuration Changes and Bug Fixes**

**In Space**


- Security officers in empire space have gotten upgraded ships and will be quicker at dealing with outlaws when they enter secure empire space.
- Cargo Containers dropped of NPC's and players have gotten increased in hitpoints from 110 to 500 so that they don't get destroyed with smartbombs or missiles so easily after the fight is over. This could have been a reason for some of the "agent npc kill mission loot not dropping" reports.
- If you have recently participated in combat (if you attack someone or fight back if attacked) then you will from now on not be allowed to dock or jump for a period of time. This temporary ban is there to prevent people from using the stargates or stations as a cheap way of avoiding defeat.
- Fixed the code that ensured that effects that were not supposed to be activated during warp finished before the warp started. This fixes a few bugs like one where people warp away after target jamming someone else.
- Fixed the bug where player ships would be taking damage up to 100 times less then they should take if the player was near death. The cause was because of damage seeping to the modules fitted to the ship.
- Sentry gun configuration has been fixed and they no longer share settings.
- Fixed where unlocking your only target while in the process of targeting a second object would leave a set of cycling active target brackets over the first object.
- You can now always deactivate an active module. Previously you could only deactivate modules on autorepeat. This should fix starting a module on autorepeat, then changing it to manual while it was active and not being able to stop it.
- You can now anchor more than one sentry gun at once.
- Empire owned sentry guns are now none-jammable.
- Mines can now be attacked and destroyed freely without any aggression based repercussions.
- If the maximum capacity of the shield or capacitor is 0 for some reason and a player logs in and does something to change it so it has something to recharge to again, the client should display the changes now.
- The shield/capacitor bug where when a charge is used, the level would drop dramatically more than it should have, should now be fixed. The server wasn't handling dynamic changes to the capacity/recharge rates correctly.
- Sentry guns in empire space have gotten a boost in defence as well in damage.


**Modules / Ammo**


- If bringing a module online and finding it already was, the module was turned offline due to generic error handling. Now, this is ignored and the module is left online in this case.
- When engaging warp, the deactivating modules that have a long duration are immediately deactivated/flushed rather so that the warp is not stalled waiting for them to finish that activation period.
- Fixed the cargo scan and ship scan effects which were broken and could not be deactivated if accidently put on autorepeat.
- Fixed a possible cause of the modules being found unexpectedly offline when logging a character in, while in a station.
- Invulnerability field has it's resistance boost decreased to 25%.
- Added Shield Hardener to list of modules that can be used while warping.
- Use of ECM modules is now an offensive action.
- Use of Tracking Disrupter modules is now an offensive action.
- Use of Energy Destabilizer modules is now an offensive action.
- Use of Energy Vampire modules is now an offensive action.
- Use of Remote Sensor Damper modules is now an offensive action.
- Due to exploits with activating modules during warp, the only modules that will remain active or can be activated during a warp are now the shield boosters.
- Fixed a bug in the module UI where pressing the mouse button down and moving the pointer out of the original or into another module icon would result in one or more module icons being left offset from its original position.
- A few shield hardeners (Ballestic Field for example) had incorrect information stating they would increase a wrong resistance type, this is fixed.
- Miner II can now be sold on the market.
- Some power/shield/capacitor rare-drop modules were marked as tech level II modules but were in fact tech level I. They now have correct tech level marker.


**Skills**


- The following skills are now available on the market: Astrogeology, Metallurgy, Research and Laboratory Operation.
- The Metallurgy, Research and Laboratory Operation skills have gotten increased in skill requirement and skill learning time.
- The Astrogeology skill has had learning requirement increased - players will need to learn both mining and science to level 4 to be able to start training it.
- Gallente battleship skill wasn't giving a bonus for gallente battleships after level 1 in the skill. This is fixed and the bonuses will now stack per level.
- Sharpshooter skill description got changed so that players know that it affects the optimal range of the turrets.


**Agents**


- The "faction loss" bug with agents should now be completely fixed. It was only partially fixed in an earlier patch. Sorry about that.
- Fixed some issues with the email an agent sends to notify the player about himself having incorrect info.
- New agent tutorial missions are in. They are more numerous than the old ones and more intuitive.


**Other Changes**


- Name changes in rare drop item groups that had a "Basic" and a "Tech Level I", they have been changed so that rare drop items from "Tech Level I" now have a tech level I marker instead of tech level II. This also applies for all items in gameplay already.
- Giant secure containers have been added to the market.
- When making a blueprint copy you will now be able to set a "cap" on the amount of items which can be made from the copy. So in effect the blueprint copies will have a limited use. This will not affect the blueprint copies which are in the game already.
- Missing blueprints on the market are no longer missing, here is a list of blueprints that are now in-game: //myeve.eve-online.com/ingameboard.asp?a=topic&threadID=22580
- There is now a French and German version of the tutorial in the game. Simply click on the icon of the French or German flag on the tutorial browser window to see the text in the said language.
- Improved the chat flow control to help defend against lag attacks.
- Fixed cargo and drone bay loading for rounding errors.
- Landmarks are now visible in map and have a description in the info windown. Some are illustrated.
- When viewing the detailed market information for an item, and having table view selected. The correct amount of jumps to destination of the order is now shown, used to be zero jumps for all orders.
