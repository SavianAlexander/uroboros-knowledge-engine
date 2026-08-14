# Improvements and Bug Fixes

- **Date**: 2003-06-13T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-29
- **Tags**: #patch-notes

## Overview
Improvements, 1058 - 1077 In Space Autopilot is no longer disabled when you get targeted If a player loses security status within range of certain sentry guns then they will attack that player at the earliest opportunity When a player ejects from his ship, the ship's position sh

---

**Improvements, 1058 - 1077**

**In Space**


- Autopilot is no longer disabled when you get targeted
- If a player loses security status within range of certain sentry guns then they will attack that player at the earliest opportunity
- When a player ejects from his ship, the ship's position should now be persisted. This fixes the case where a player would eject and then come back later to find his ship was apparently elsewhere - some place he'd been earlier
- Player hit (or missed) by missiles or drones should now see combat messages for it
- When mines, missiles or drones damage things, the player should now get combat damage messages for it
- Sentry guns are now deployed near stargates and will defend the stargate if it is attacked as well as anyone who belongs to the faction of the stargate's corporation who is attacked within range
- You should now see a message when someone is warp scrambled nearby
- Various map fixes. Statistics filters now work properly ( players killed, jumps in the last 24hrs etc ).
- Newbie characters doing the in-space tutorial will now have around fifteen minutes to reconnect and continue it should they get disconnected for any reason in the middle of it (used to be around one minute)


**Communication**


- Chtsetcreator can now be used to change channel ownership
- Modified "local channel" concept, so now all the stations within the solarsystem are in the same channel as the solarsystem. Should make local a bit more usable


**Ship Management**


- Microwarpdrive now has more penality on armor and shield
- Arbitrator, Bellicose, Maller, Omen, Rupture and Thorax have gotten increase by 1 medium slot. There were not enough counter measures for these cruisers with only 2 medium slots
- Fixes the an ammo reload problem
- Named stasis web modules now have more range than before
- Named hybrid railgun weapons have had their tracking speed lowered to their true values
- Some loot modules were granting way to big a bonus when stacked - these bonuses have been lowered
- Gyrostabilizers/Heat Sinks/Magnetic Field Stabilizers have had they Damage Multiplier and Rof Bonus reduced
- Fixed the problem with reloading where you could only load a module in-space from an ammo stack that you were not already reloading from. The excess (not being used in a pending reload) is split off into a new stack


**Corporation Management**


- A new role has been added for corporations. Previously everyone could view the contents of member hangars via "Member hangars" button in corp hangars, now a member must have the security officer role in order to view the contents of member hangars
- Corporations now have 5 security groups in addition to previous roles, each security level gives access to a security folder that is designated to that group and is accessable via the corp hangar. There are also two new folders in the corp hangar, the Market folder, accessable for accountant, and Factory folder, accessable for Factory Manager.
- Possible to retrieve impounded content from corp hangars that are no longer rented. Get CEO/Director to click "Corp Hangar" in lobby to see how


**NPC´s**


- Replacement and new sentry guns around NPC corp owned stations and stargates should now be the correct racial types. The existing incorrect gun types should be updated in a server update
- Battleships from CONCORD, Empire Police and Empire Military will now be patrolling some areas from time to time
- CONCORD, Empire Police and Empire Military units will now use stasis web on players that they are after
- Rare drop modules (from NPC's) were giving too high values - The values have now been adjusted
- Fixed the problem where everyone nearby gets a share of the bounty awarded to the person who effectively killed a pirate NPC
- CONCORD and DED NPC's now have their corporation name with the NPC name so players will now know to what corporation/faction they belong to
- Description text for CONCORD and DED NPC's has been fixed, they were showing information about random ships in game
- After a period of leniency, pirates will now venture further out of the asteroid belts in order to deal with interlopers who mine along the edges trying to avoid them
- CONCORD police now have a high chance of warp scrambling their targets
- Fixed a case where pirates would break to some degree because they tried to activate a module and were not within the required range


**Agents & Missions**


- The agent missions marked as important, which give you a new agent as a reward used to only be available once per agent even if you failed them. This has been changed, you will now have a chance of getting them again if you fail the mission


**Game Music & Sound**


- Problem with audiolib leaking if audio was off has been fixed


**Other**


- Double-click in the title bar of windows minimize the windows


**Bug Fixes, 1058 - 1077**


- Error when moving a character into a station
- Ext: Possible insurance exploit
- Error when using ECCM - Gravimetric module while being targeted by police
- Courrier missions: Cargo hold capacity is not correctly displayed for plastic wrap containers
- Error when closing member info on your own character
- Suggestion: The flashing effect that appears on a minimized chat channel tab should be a feature that the user can turn off, particularly for the local and corp channels which can't be closed
- Chat window always resizes to default lower left corner!
- Ext: dynamicly generated images and the ingame browser lead to crash [mini dump included]
- Unable to fit any charges to weapons
- Partial move when loadin ammo in space
- Corp member with no roles/security level can still view contents of other members hangars
- Corporation hangar does not update correctly if security level/roles is changed 2x
- Suggestion: When right clicking on a blueprint, there should be a Quick Build option
- Factory UI does not refresh when a blueprint is installed
- Ext: fitted modules remain active after unfitting
- Ext: pirate loot not updating with changes
- Error when editing the roles of a member
- Ext: Fuel Conservation bug
- Voting - Proposing a Multiple Choice Vote yields an error
- Ext: unable to complete tutorial
- GMs not able to transfer items from corporation hangars to a player hangar from offices that have expired
- Access control of corporation hangars
- "KeyError: char.name" popup when trying to clear security rating
- Metallurgy skill bonuses are not correctly applied
- Ext: phase switching I targeting nexus not functioning
- Key error in agent missions
- Error in chat system
- Ext: non Movable Plastic Wrap in Mission
- Ext: EXPLOIT - goods from agent
- Ext: Weapon Upgrade Skill
- Ext: CHAOS - Faulty agent mission
- Skills are taking a few seconds to reach the completion imminent stage when training from a skill pack to level 1
- A graphical corruption associated with the auto pilot button
- Ext: Pirates disappearing and respawning kms away during battle
- Repeatedly clicking on "put online / offline" yields an error
- Ext: Request: People & Places: Option to have
- No shares created when vote is finished
- Some notification needed for what skill and how many points you have lost upon death
- Ext: Player-Created Trade Goods Buy Orders Suggestion
- Game hard crash when in background
- Jumping to the same newbie system you were in, results in you appearing next to the station
- Error when trying to install for corp with wrong roles
- Ext: 'Frozen' Market orders on TQ
- Ext: fitted modules remain active after unfitting
- The map screen takes an extraordinarily long time to load without any warning to the user
- Put services available at a station in the info window for that station
- Ext: Show Info not working
- Station Services - Not refreshing
- NeoCom: Emails received from other users are always listed as having No Subject in the header
- Confusing in-station and in-flight cargo interface difference
- Starmap: Show all displays an "artifact" in topleft corner - but only when zoomed in to show region names
- Starmap: Blinking artifact when zooming in on starmap (when names-tags are added)
- Bookmarks: There is no way to sort a user's bookmarks (i.e. alphabetically, by type, etc.)
- Map: Neighboring region names will remain on the map, even when the user has chosen to only see the selected region
- Attributes, of other players during show info
- When my ship gets destroyed, my pods speed always reads "STOPPED"
- Wallet: Journal displays error
- Some systems are not loading up correctly, no stargate brackets and ballpark spam
- Able to put items into non-assembled containers
- The max number of characters allowed in character creation should be raised to 24, as the DB allows that many characters
- Ext: Autopilot functions
- Clones: prices all messed up
- Get errors when opening the trade window
- Ext: Exception loading ammo
- No police showed up as I was attacking a newbie in a newbie system
- Error when trying to open the browser
- Ext: Resource identifier shown when using auto pilot to jump gates
- Ext: The '~' symbol is still not working
- Minor exception with switching to ships hangar while merged in station UI
- Ext: Map Browser (F11) problems
- User error trapper needed
- Ext: Bookmark renamed
- Error when opening people and places
- Opening the stock market affects the station service UI
- Move Home option leaves the players ship in space
- Better sorting of my inbox - request
- Corporation recruitment acknowledgement is always sent by the CEO
- cloning facility does not seem to show up on available cloning "binds"
- Ext: Selected property does not work
- Voting: error popping up after closing "add option" window
- Agent location info cluttery in UI
- Ext: Confirmed serious issue with Slasher mesh !!!
- Ext: Vanishing dialogs/windows
- Ext: Completion iminent bug/exploit
- Switching to another skill at level 0 gave me an error
- Error when attempting to sell item
- Ext: gender error in text of CEO resignation message
- Ext: repair menu decription error
- AgentMgr error from TQ
- Error in channel operations
