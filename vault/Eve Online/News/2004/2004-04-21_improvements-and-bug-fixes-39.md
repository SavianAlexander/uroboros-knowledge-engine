# Improvements and Bug Fixes

- **Date**: 2004-04-21T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-39
- **Tags**: #patch-notes

## Overview
New Features, Bug Fixes and Improvements Gameplay Fixed an exploit where players were able to add items to and remove items from any cargo containers they owned, regardless of distance, as long as the container window was open. Fixed an exploit where players could mine with just mining

---

**New Features, Bug Fixes and Improvements**

**Gameplay**


- Fixed an exploit where players were able to add items to and remove items from any cargo containers they owned, regardless of distance, as long as the container window was open.
- Fixed an exploit where players could mine with just mining drones in hidden belts and not be detected by NPCs.
- Veteran players will no longer be given the option to restart the in-space and station tutorials.


**Navigation**


- The highway systems have been "decentralized". A ring of systems at each hub will replace the old singe system nodes. The biggest effects are 0.8 and 0.9 systems adjacent to current single node systems will have an increase in traffic and travel distances will increase by a small number of jumps. Read more about this [here](//myeve.eve-online.com/devblog.asp?a=blog&bid=142).
- You can Gang Warp to a bookmark location now.
- A Set Destination option has been added to agent user entries.


**Combat**


- An issue with the on/offline state of modules and weapons has been fixed.
- A half-cloaked graphic "artifact" that was left behind at the location of a cloaking player should no longer appear.
- Concord should properly respond to crimes.
- Fixed where missiles destroyed by damage rather than by being collided with were doing splash damage to everything in range. This would generally be triggered where two missiles collided or someone used a smartbomb.


**Modules**


- A crash bug for many modules has been fixed. Also, the sound for energy destabiziation should work correctly when looped.


**Agents**


- Various updates to agent missions have been added.
- Fixed warping distance to tutorial when restarting. Previously, the distance could be too far for a new player to comfortably navigate to or too short a distance to warp.
- Fixed division by zero error when 0 or near-0 Research Point field draws occured.
- You can now only do the tutorial for your own starting agent. Other agents will not accept you.
- The training missions have been fixed.
- The corp info agent list has been fixed.
- Research field status information has been added to research agents.
- Agents will no longer send players into areas of space with sec ratings above (1+(player sec rating/20)) or his own system's rating, whichever is higher.
- The "my agents" map has been improved, and positive faction standing makes connections activate.
- The mission pirate farming exploit has been fixed.
- Slightly beefed up the difficulty of various level 3 and 2 missions (although mainly level 3).
- The blueprint copys that agents were sometimes dishing out as rewards have had their material efficiency and productivity level raised a bit to make them less "worthless".
- The mission "Show No Mercy" has had its average encounter difficulty upped.
- Added Set Destination as a feature for the masses on agent user entries.


**In space**


- General aggression checks now use rounding on a players security status before checking if they are an outlaw. So, -4.95 and below is considered to be outlaw.
- Fixed sentry gun placement to 50km.
- Sentry guns now use rounding in standing comparison. One example case -4.95 and lower down to -5.0 is now considered -5.0, or outlaw status if we are dealing with security status.
- New characters should no longer start in space with offline modules.


**Other**


- The "hide landmarks" toggle button displays properly.
- The "bug report" button in the help window has been removed.
- A server faq button has been added in login window.
- A second test server named "Entropy" has been added to the login window. This server is used for reproducing bugs and testing release candidates.
- Market orders with a non-positive integer price will no longer be accepted.
- "Select All" button in the Cargo Bay display has been fixed.
- NPCs no longer display "member of corp since", and CEO info for player corps has been added.
- Fixed booster offset of Scorpion ship.
- New compiled.code format stores optimal bootstrap order of its files, so that we now reduce client startup file by 10 seconds on my machine
