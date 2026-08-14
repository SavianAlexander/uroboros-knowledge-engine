# New Features, Config Changes and Bug Fixes

- **Date**: 2003-07-10T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/new-features-config-changes-and-bug-fixes-6
- **Tags**: #patch-notes

## Overview
New Features / Configuration Changes and Bug Fixes In Space Fixed the problem where security status or bounty for killing NPC pirates would go to the wrong people. There was a jettison bug that resulted in only one player being able to jettison a container in a system every 5 minutes. T

---

**New Features / Configuration Changes and Bug Fixes**

**In Space**


- Fixed the problem where security status or bounty for killing NPC pirates would go to the wrong people.
- There was a jettison bug that resulted in only one player being able to jettison a container in a system every 5 minutes. This has been fixed. Now the timer (which has been reduced to 3 minutes) only affects the player that jettisoned the container and not the entire system.
- Billboards are now stationed beside stargates in empire space.
- Billboards now use missiles as part of their arsenal.
- Anytime you lose a target, the active target was rechosen whether or not the target that was lost was the active one. The active target is now only rechosen if it is actually lost.
- When a target was locked, it would be set to the active target. Now, a target is only made active if it is the only target locked. If the active target is lost it is up to the user to pick a new one.
- There was a bug with bookmarks which rendered them unusable. Deleting the prefs.ini file used to fix this. The bug however has been fixed with this patch so deleting the prefs.ini is no longer neccessary. There are still some issues with deleting bookmarks however, which will be adressed soon.
- Region jumps are now colored purple, not green, in world map, to distinguish them from secure jumps, which are now colored green.
- Jump count in waypoint labels in World Map is now correct ( was +1 ).


**Modules / Ammo**


- Fixed the add negative quantity errors which were happening. This was because of reduction in the amount of ammo that could fit into weapons - trying to add more even though the weapon was overloaded would give these errors.
- Fixed errors with cargo and ship scanning where it would error when the target was carrying nothing at all.
- Fixed a problem with the target brackets where sometimes after an object had been targeted, the pulsing "target pending" state would not be cleared.
- Fixed a problem with the target brackets where sometimes after a target had been unlocked, the square targeted state bracket would not be removed from the object.
- Missiles have more hitpoints now, bigger and more expensive missiles will be harder to tackle. Defender missiles have been tuned to the new hitpoint values as well.


**Ships**


- Minmatar cruiser: Stabber had incorrect thermal resistance for it's armor, this is fixed.
- When switching ships in station, any repairs just made to the ship the character is exiting will now be remembered.
- When disconnecting in station, any repairs just made to the active ship will now be remembered.
- Armageddon's powercore was decreased from 15.000 to 12.500, it was not suposed to have as much powercore as the Apocalypse.
- Scorpion battleships now cost less high value minerals to manufacture.
- Typhoon had too high recharge rate for its capacitor, it's now 870 seconds instead of 3000.


**Agents**


- There was a bug with agents lowering the standing of players. Agents have a cap to how much standing they will give to a player, which is based on their level. If a player had more standing than the agents cap, it lowered down to the cap. This has been fixed. Note: there are still missions out there that will lower standing, even security status, this is by design. If you are using an agent in a pirate corporation he may give you these missions from time to time.
- A few pirate faction missions were implemented. More will be implemented later. These missions give a higher than average reward but also have a faction or security level penalty.


**Station Services**


- Fixed the slots what were only available to NPC corp members. Now all 32 slots should be available to all.
- We increased rental period from 3 to 5 days, will only affect rentals after the change (old rentals are still 3 days).
- Station resource rental should function as expected now.
- There was a bug where the user installed a blueprint for manufacturing that they did not have minerals for so that they could see how many minerals they require to use the blueprint. The blueprint was not ejected after it was installed for such an operation. This has been fixed.


**Other Changes**


- The save password option has been taken out of the client.
- Fixed the Caldari Cruiser skill to give the max range bonus it should have been giving.
