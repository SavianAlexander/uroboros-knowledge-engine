# Improvements and Bug Fixes

- **Date**: 2004-03-19T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-38
- **Tags**: #patch-notes

## Overview
New Features, Bug Fixes and Improvements Combat Missiles can no longer be targeted. Some players were able to do this by working around the client restrictions. Occassionally, some npcs were also targeting missiles. A confusing message mentioning splash damage when a direct hit was infl

---

**New Features, Bug Fixes and Improvements**

**Combat**


- Missiles can no longer be targeted. Some players were able to do this by working around the client restrictions. Occassionally, some npcs were also targeting missiles.
- A confusing message mentioning splash damage when a direct hit was inflicted has been fixed.


**Modules**


- Using a remote sensor dampener on someone is now considered an act of aggression.
- Online / offline toggling of modules in space has been enabled. Bringing a module online in space now has an activation cost. Activatation of a module now consumes 66% of your capacitor charge and requires a 95% reserve.
- When a pilot boards a ship, the ship's computer will activate the modules left online when the previous pilot departed.
- Previously, a player could 'show info' on a charge item (frequency crystal, ammunition, etc.) and see what module groups it could be loaded/fitted into. Now, a player should look at the 'show info' for a module to see what charge groups can be fitted/loaded into it.
- Previously, it was possible to load an unassembled module on a ship. Now, if a ship has an unassembled module fitted to it, the module will be moved into the cargo hold. If there is insufficient space in the cargo hold and the ship is in space, the module will be jettisoned. Otherwise, the module will be destroyed. This is a bug fix.
- The fitting problems where your ship's modules would sometimes go offline when you boarded it and you would be told you didn't have enough cpu to bring them online when you tried should now be fixed. Skills were sometimes applying their bonuses at level 1 instead of the actual level. Now they should apply at their correct level, this should fix a much wider range of issues than the one described above.


**Skills**


- Level 3 Heavy Missiles skill is now a prerequisite for the Torpedoes skill, Cruise Missiles skill, and the operation of Heavy Missiles.
- Level 3 Standard Missile skill is now a prerequisite for the Heavy Missiles skill and their operation.
- Mining Laser II has had an activation skill requirement increase.


**Agents**


- The "accept courier mission" bug has been fixed. The correct message should pop up now when the player has insufficient space in his cargo hold, instead of breaking the mission.
- The travel route to the first agent the player is referred to has been shortened. This was done by adding in some jumps in high secure space.
- Fixed the tutorial delivery mission. The spiced wine was not at the station sometimes.
- Improvements to the agent lobby list and agent list entries have been made
- Research agents no longer offer you research missions after you stop researching with them.


**Inflight / NPCs**


- Warp distance of rookie frigates with the base capacitor has been increased up to 70 AU.
- Unprotected convoy travel distances should now stay the same regardless of the effective sentry gun weapon ranges.
- It is no longer possible to board a ship that has negative structure (damage > hp).
- Ejecting from a ship with high structure damage so that only your skills were holding it together (removal of your skill bonuses results in damage being higher than the default type hp) will result in the ship exploding after you eject if you are in space.
- Change in the deployment of NPC corporation sentry guns based on the security level of the solarsystem. Six guns will be deployed in a cross formation where the security level is 0.5 or higher. Eight guns will be deployed in a cube formation where the security level is 0.8 or higher.
- The tutorial drone orbiting speed has been decreased for easier civilian gun tracking.
- The Armor Repairer graphics have been removed. After fixing the bug where activating multiple Armor Repairers would CTD, it was found that effect still created lag in large battles.
- Shield hardeners should not appear on your ship unexpectedly anymore.
- "Warp Gang" has been added next to the "Warp to" option if the pilot is the leader of the a gang.
- The Guristas Usurper will not longer be dropping Amarrian combat upgrade modules, they will be dropping Caldarian from now on.


**Other**


- Added level 3,4 and 5 public scenarios.
- Insurance payments made on Elite Frigates that were destroyed will now use the base price of materials when a payment is made.
- It is no longer possible to anchor anything in space where the system security level is greater than 0.8 .
- EVE splash screen is back
- Docking issue, where the players ship tends to bump into the station before docking (when remotely docking) is fixed.
- Some routes (using the autopilot) were not working correctly due to the current map cache being out of date. We have hotfixed this by adding in a few jumps which will be removed in the next patch (after this one) when the map cache is updated. In plain english this means that we fixed the "map shows a route through a stargate that doesnt exist" issue.
- Fixed the market price history graph
- Solved a problem with the quick buy/sell requester. Entering of fractional values was broken.
- Removed "ping" sound when the shipui is reloaded after a jump.
