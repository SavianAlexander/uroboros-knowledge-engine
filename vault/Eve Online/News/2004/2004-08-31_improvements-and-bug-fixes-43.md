# Improvements and Bug Fixes

- **Date**: 2004-08-31T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-43
- **Tags**: #patch-notes

## Overview
Bug Fixes and Improvements   Gameplay Ships now leave station at a consistant speed when undocking, regardless of size. Setting speed no longer disengages orbit or any other mode. Combat drones no longer attack asteroids, but are able to attack deployable objects. Combat

---

**Bug Fixes and Improvements**

**Gameplay**


- Ships now leave station at a consistant speed when undocking, regardless of size.
- Setting speed no longer disengages orbit or any other mode.
- Combat drones no longer attack asteroids, but are able to attack deployable objects.
- Combat drones now ignore ranged defenses which do not cause them damage.
- Sentry guns no longer respond to being smartbombed, as smartbombs cannot be activated to hit them or the structures they protect.
- You can no longer manually remove charges from active modules or while your ship is cloaked.
- Ships that have negative armor hp are now no longer allowed to undock and get an error message instead. This should prevent people that get a ship heavily damaged from unfitting the modules which were keeping its armor hp at reasonable levels and then undocking, resulting in a less than satisfying result.
- Another cause for the ship-on-ship display issue has been found and resolved. Previously, if a ship decloaked twice, it created an instance where multiple ships would be "collected" and displayed.
- Fixed warp-to-bookmark error.


**Ships and Modules**


- Incorrect descriptions for the 200mm Railgun IIs and 350mm Railgun IIs have been corrected.
- Incorrect descriptions for the Crow, Maller and Thorax have been corrected. A correction has also been made to the Interceptor description.
- The Caracal missile velocity bonus now works properly.
- The Guardian-Vexor has been given the same secondary bonus as the original Vexor.
- The structure hit points of Torpedoes have been increased.
- Defender missiles have been increased in damage to be able to counter the hitpoint increase of the Torpedoes.
- Large Smart Bomb IIs have been modified. They are now what they should be regarding size and tech level.
- Small Smart Bomb IIs have had their damage increased from 65 to 70.
- Smartbombs now only do damage to drones, ships, missiles and pods. They will deactivate if they attempt to do damage to something within 5000m of stations or jumpgates.
- The skill description for large blasters has been corrected.
- Shield Amplifiers have been increased in resistance bonus and decreased in CPU need for fitting. This puts them into the same category for shields as energized platings serve for armor.
- Shield Transfer Arrays and Energy Transfer Arrays have been tweaked in range, fitting requirements and transfer amount per cap.
- Tracking Link now has an attribute which determines the maximum range that the module can be activated on targets.
- Remote Armor Repair System modules are now available and are being sold as blueprints by NPC Corporations. These new modules act as Shield and Energy Transfer Arrays and also repair armor damage of targeted ships.
- Remote Armor Repair Skill is now being sold on the market, the skill is needed for using the new Remote Armor Repair System modules.
- Multi-Tasking Skill is now being sold on the market, it works as an advanced Targeting skill which allows more activate targets (maximum targets is also based on current ship, skills can not allow more targets than the ship can support).
- Alot of Tech I Blueprints that were missing from the market should now be available.
- Alot of missing market groups for Tech I and Tech II modules have been added (this does not include named modules dropped by NPC's or given by Agents).


**Agents**


- Modifications & fixes to various agent missions have been made.
- The pirate encounter "aggressiveness" parameter should work as intended.
- Issue fixed with where an expired offer would not note the mission name in the standing transaction log.
- Issue fixed with the info window of a tutorial agent who was showing the "11th tutorial".
- Issue fixed with multiple order missions who were causing an unusually high amount of item resolution failures.


**Npc's**


- The issue where killing NPC pirates was not giving the correct security gain has been resolved.


**Other**


- Previously, if a player logged out of EVE while in combat and their ship was subsequently destroyed before the log off timer expired, their capsule wouldn't appear. This is a feature that was never intended and has been resolved. Now, the capsule will appear as it should.
- The issue with research points not being shown by agent show info has been resolved.
- The effects of Diplomacy, Connections, and Criminal Connections are now taken into account in reprocessing.
- Scalability issue fixed in the chat system with large chat channels.
- Players now get a proper error message when applying to an NPC corporation.
- A error that appeared when accepting an offer from a player corporation is fixed.
- Code optimizations have been made to resolve large amounts of lag created by large numbers of players in the same system.
- Sorting of items in the repair service UI is now in alphabetical order.
- The assignment of D3D light IDs has now been cleaned up. EVE can now deal with cards that offer an unlimited amount of active lights, like software T&L does.
- Lag created by criminal flagging has been resolved.
- A reminder has been added to the final stage of accepting an offered blueprint stating the research is now no longer in progress and a new research project must be started.
- Stronger logic added to ensure that if you get a research mission assigned and you didn't have a research project going, the mission will not be silently assigned to you.
- Changed the billboard manager so bounty portraits are no longer rendered by the client.
- A display error with items disappearing from the corporation hangar after a trade has been resolved.
- Better caching of aggression and wars has been implimented. This is to address the issue with low bandwidth connections getting lag before aggression would start.
- Added HTTP_EVE_CHARID to the IGB headers to retrieve the characterID of a person browsing a secure site.


¤ **Patch 1722 to 1724** addresses **Bug Fixes**


---


**Bug Fixes**


- Using Blueprints from Corp Hangar in factories and lab slots works again.
- There should be much less "ghost ships" that stuck into your ship
- Removed wallet journal export again. It was not supposed to be in the patch.
- fixed missile damage
