# Improvements and Bug Fixes

- **Date**: 2003-05-17T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-26
- **Tags**: #patch-notes

## Overview
Improvements, 1002 - 1031 Skills Players can now cancel a skill training without starting a new one; useful if you want to start a training with other of your chars. Agents & Missions Agent level 2 missions have been added into the game. You can recieve a level 2 agent either by bei

---

**Improvements, 1002 - 1031**

**Skills**


- Players can now cancel a skill training without starting a new one; useful if you want to start a training with other of your chars.


**Agents & Missions**


- Agent level 2 missions have been added into the game. You can recieve a level 2 agent either by being lucky and finding one that is available at a station by docking into it, or completing a special mission from a level 1 agent.
- Agents now add themselves to your address book when you get them.
- Improved agent deployment/default config function to ensure correct random distribution of services and service props.
- Added agent service frequency support.
- Added agent info to corp pages, so now you can see what corps have what agents, and some rudimentary info like what station the agent resides in and what level he is.
- Added QualityBased support, so two agents with the same level are no longer identical.
- Added extended info for agents in show info
- Added location query to agent selection criteria, making 45 jumps away a thing of the past for properly configured missions.
- Added agent "hi message" on char creation, bookmark, and blink for new agents.


**Market**


- Market now favours matching sell orders that are closer to a ranged buy order's home station.
- People who place sell orders below the average, now get a warning when trying to do so.


**NPC´s**


- Pirates that go to stargates will no longer warp scramble players and are now weaker than before. Don't forget that pirates will only go to stargates in 0.0 - 0.4 security, but never if there is only one stargate in the solar system.
- Scenario NPCs will no longer attack players in a polaris ship
- Stargate pirate infestations will only ever be present in 0.5 security level or below solarsystems.
- If there is only one stargate in a solarsystem, it will not be infested by pirates in order to prevent people from getting trapped.
- Convoy loot value has been decreased, and convoys now have real weapons to fire at players.
- Some pirates have had their missile shooting removed, and frequency of missile shooting was decreased for all pirates.
- With a larger variety of items having been added to the NPC market and convoys dropping whatever is there, they were dropping ships and other stuff that shouldn't be. A filter has been added to what they drop from the NPC market as loot.
- Pirates are getting tired of being picked on by pilots who are told to intercept and kill them by their agents and have taken a more aggressive stance.
- Added missile launching capability to NPC ships.
- Missile launching set up for few pirates
- Speed for NPC's has been tuned down, they will now get speed boost if they don't reach their orbit range that is less than the range they are currently chasing the target at
- Bounty for pirates has been trippled
- NPC station defense sentry guns will now start attacking recent offenders who are present when they are respawned.
- Fixed wrong ship models for Sanha's faction military


**Gangs**


- Added a warp to gang member option, which allows a gang member to warp to a fellow gang member if they are in the same system, regardless of visibility.


**Communication**


- Bookmarks have been merged with address book
- Features belonging to Misc Panels in NeoCom have been moved over to station panel
- It is now possible to merge ships and items in station panel
- Address book has been renamed: People and Places. It has also aquired a search tool that player may use to search for characters, corporations, stations, asteroid belts, solarsystems, constellations and regions
- Misc fixes to browser bookmarks and the trusted/ignored sites dialogs.
- JIT session change - propagation suppressed for most chat commands, should reduce "bottleneck" effect of large chat channels, increasing scalability.


**Navigation**


- Destroyed objects are now removed immediately from the radar instead of hanging around clouding it up.


**Ship Management**


- Power consumption for heavy missile launchers has been reduced
- People can no longer activate modules while warping. This prevents the cases where people start a mine on their way to the station (getting some extra ore despite the fact the asteroid is way distant by then).
- When a player ship is destroyed, its drone bay contents will now also be considered for dropping in the cargo container. All of the ships contents, drones, cargo, modules now has the same chance of destruction.


**Combat**


- Warp scambler/disruptor ranges improved
- Sometimes the damage state of an object wouldn't get sent from the server to the clients (sentry guns would respawn with strange shield/armor bars). This should now be fixed.
- Certain types of objects which disappeared (asteroids for inst.) would not clean up w.r.t the players who were targeting it. This meant that the target slots were lost to the players until they left space/restarted client.
- Sentry guns have had a free firmware upgrade and will no longer pod players.
- Tweaked drop tables for frequency crystals. Some of the more valuable ones had too high a percent chance of dropping. Oops!
- Energy weapons, which have a built in frequency crystal, now display the damages of that crystal in the client when their info is viewed with "show info".
- Fixed where firing a missile/whatever (after using the reload context menu option to restock a launcher) would result in the rest of the ammunition to become hidden and the launcher to look as if it was empty.


**Game Sound**


- Unused looped sounds are no longer filling up channels
- Crash that occurred when all sound channels were taken has been fixed


**Other**


- Much of the client memory leak has been plugged.
- Major memory leak fix on client, proxy, and to a lesser extent on the server.
- Weird graphic glitch, where thrusters became blocky, has been fixed.


**Bug Fixes, 1002 - 1031**


- Skills level exploit
- stuck in station bug
- Repairshop: shows damage and offers repairs - but not consistantly
- Ship won't exit station, error occurs
- Exception when right-click train on new skill
- Damage of ship not showing up in repair station
- Some repairshop damage discrepencies
- Incorrect info in market email after market transaction
- Container: Executioner has capacity 135 but the description says 225
- Error with autopilot / jumping to another system
- Error and window - wont load when opening the info window for agents
- Deposits of 0 to the corporation wallet are registered in the transaction journal
- Game hangs in 'Entering space....'
- Buying a blueprint from the market charges you double
- Logged out with pirates present, logged in with missiles orbiting
- Drones are not scooping correctly
- Tutorial: got stuck in in-space tutorial
- Factories - Uninstall button not working
- Market transaction info window pops up twice
- Sometimes items are stackable, sometimes not
- Game Graphics: Huge neck on the amarr?
- Activating a gun as soon as you have locked an object causes an exception
- Petition: Volunteer petition screen refresh problem
- Videocards: The warping animation is corrupt when using the Matrox Parhelia
- The progress bar shown while the map screen loads does not accurately reflect the progress of the loading process
- Error when activating a mining laser on a roid
- Corp hanger ship trading bug
- Autopilot indicator problems 2
- Error with training with an implant
- ship trade: corperate hanger
- Multiple Bounties, Negative Cash, Big Problems
- Assembled ships in the corporation hangar still have the "assemble" option
- Ship UI readout not updating correctly
- Red squares over brackets and ships in space
- If "Show radar" is deselected, it still appears as selected in menu
- Error when starting conversation with a player
- News can only be seen by select characters
- Market: buying multiple blueprints
- Problems when buying blueprints in bulk
- Error when trying to access a certain mission in the mission journal
- ATI Radeon - Menu : Tabs in menu do not display correctly when selected
- ATI Radeon 9700 Pro - Serious Frame rate Problem
- [Vivendi] - ATI Issue: Quit confirmation box: The Yes and No buttons are bright white and almost illegible.
- Problems when buying blueprints in bulk
- No "friendly message" when trying to connect to a server that is down
- Hard crash when someone logs into your account while you are using it
- Tutorial: Selling the 750 units of Tritanium and buying the Civilian Shield Booster do not cause the Wallet Journal to update properly.
- System Error: popped up when logging in
- Error when putting money into hangar from wallet - money vanishes into thin air
- Polaris ships currently are attacked by npcs
- Error when clicking on "done" after the first agent tutorial mission
- NPC's: need some changes to NPC command behavior on attacking and defending
- Description text needed for ores
- Gang: When a player is kicked from a Gang, they retain the Gang Chat window, and will receive exception errors if they attempt to use or close it.
- When docking a buy order to another window the tab that created has no title.
- A brief scene where the player's ship is located inside the sun is shown when docking
- Current destination info overlaps over the edge of the black area
- Error when attacking an empty ship
- Can't repair ships armor
- The 'Inferno Torpedo' is described as being unguided, and yet it tracks targets in the same manner as guided missiles.
- Medical: If the user cancels the 'Choose Station' window, they will not be able to reopen it via the 'Change' button.
- Avoiding Angels bug
- Celestial Object Distance does not update properly
- Agent training mission bug fixed
- Agent Tutorial Mission 3 fix
- Use characters name in tutorial text
- NPC's: need some changes to NPC command behavior on attacking and defending
- Fittings: Ammo will remain behind after the gun is moved away
- Gang: When a player is kicked from a Gang, they retain the Gang Chat window, and will receive exception errors if they attempt to use or close it.
- Feature Request: Region and Race chat channels independent of corp
- Expired 1st mission still passed as non expired
- Station, Belt, Gate Icons Inaccurate
- Map: Using the mouse-wheel to zoom in will result in a blank map at the closest zoom level.
- "You are here" sprite moves out of main market starmap window
- Ship Control Interface: Some changes
- Bookmarks: When a bookmark for an arbitrary area in space (designated by specific X,Y,Z coordinates) is sent to another player, the coordinates change to reflect the other player's location.
- Corporation: If the user makes and then resigns from a corporation (within the same session), their corporation window will not appear correctly.
