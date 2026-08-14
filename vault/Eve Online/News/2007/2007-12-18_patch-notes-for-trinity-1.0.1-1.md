# Patch Notes for Trinity 1.0.1

- **Date**: 2007-12-18T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-trinity-1.0.1-1
- **Tags**: #patch-notes

## Overview
Trinity 1.0.1 Patch Notes, released 18 December 2007 Linux and Mac Client General stability fixes for both Mac and Linux clients have been added. An issue where closing the Mac EVE client would cause a lockup has been fixed. The Mac client will now use the current OS resolution as a

---

## Trinity 1.0.1 Patch Notes, released 18 December 2007


**Linux and Mac Client**


- General stability fixes for both Mac and Linux clients have been added.
- An issue where closing the Mac EVE client would cause a lockup has been fixed.
- The Mac client will now use the current OS resolution as a default rather than the hard coded settings.
- Windows should no longer turn inside out.
- Mac client users can now use Ctrl+C and Ctrl+V to copy and paste both in-game and desktop.
- EVE Voice should now work under Mac OS Leopard. Now ransomers can hear their victims sing "Dancing Queen".
- Some missing Unicode clipboard formats have been added.


**NPE & Tutorials**


- The drones tutorial no longer blanks out when the starmap is open nor will it lock up in certain circumstances.
- The tutorial window will no longer disappear if the screen size is decreased.
- Containers in tutorial dungeons have been fixed to be usable by characters going through the tutorial.
- Under certain rare circumstances, new characters would be thrown in the trash when entering the game in-station. This has been resolved in a hotfix earlier.


**Skills and Implants**


- The Nanite Operation skill has been fixed.
- A rare case where a jump clone would lose its implants after a jump has been resolved in a hotfix earlier.


**Drones**


- Drones no longer instantly recharge their shields when recalled to the drone bay.


**NPCs**


- NPCs have been ordered to cease their attacks on secure containers in space. This issue was hotfixed earlier.
- NPC bounties will now be processed correctly at downtime.


**Missions**


- Activities performed by drones now count towards determining whether a mission is complete - specifically, using mining drones would prevent mining missions from completing properly.
- The issues with the mission Pot and Kettle - Seek and Destroy (4 of 5) have been resolved.
- Objectives for the mission In the Shadow of War (1 of 5) have been clarified.
- Security agents are no longer giving out mining missions. No more milk runs!


**Science and Industry**


- Combat Recon ships can be manufactured once again.


**Starbases**


- A number of hotfixes have been applied since Trinity's deployment to resolve numerous issues with starbases and their shields.
- Launching a jump bridge array no longer locks the Premium Graphics Content client up.
- The name change of the reactor arrays that occured in the Trinity release broke all existing connected Starbase structures. This was resolved as part of a hotfix.
- The cause of the starbase shield reset at downtime has been found and resolved as part of a hotfix.
- An error that was preventing the Cynosural System Jammer from operating correctly has been resolved as part of a hotfix.
- Damaged control towers will no longer cause problems with the loading of a Starbase while the solarsystem is loading. This was resolved in a hotfix earlier.
- A situation where modules requiring a specific sovereignty level would break a starbase on system load has been resolved as part of a hotfix.
- An issue with jump bridges not working for non-corporation members has been identified and resolved.


**Corporations & Alliances**


- Corporation mails are no longer sent to all members with a title.
- A major issue with the corporation registry has been fixed.


**Killmails**


- An exception that would prevent kill details from showing up has been fixed.
- A bug where NPC data would overwrite a player's entry in the kill database has been fixed.


**Star Map**


- Star Map is no longer grayed out when no region names have been selected in Labels.
- An issue preventing the Star Map from displaying properly after viewing solar system map has been resolved.


**Other**


- Numerous server-side errors have been resolved. These will have no visible in game effect, but server-side performance has improved.
- Extraneous bulkdata should no longer be downloaded when logging into EVE. This should decrease login time.
- The login screen should no longer be spammed with error messages.
- Account names and installation folders with Unicode characters are now fully supported.
- An exception thrown by the In-Game Browser has been fixed.
- Nanite repair paste can now be stored in all hangar divisions, not just the first.
- The new gas cloud resources can now be seen on the market.
- Overview behavior while minimized has been optimized.
- The displayed log entries for derived standing changes were incorrect. This issue has been fixed moving forward. The dervied standings themselves were correctly calculated.
- The locked targets display origin point will no longer be hidden under the Neocom in certain circumstances.
- The undocking point for certain stations has been moved so that undocking ships remaining within the docking perimeter.
- An error with loyalty point processing has been fixed.
- The region names approved for the recently open "drone regions" have been added to the starmap.
- Leaving voice on in a channel now shows properly on other player's clients.
- Selected items are again added into the contract selection when a contract is started through a right click on one of the selected items.
- A number of server log issues have been resolved. The server log should no longer be spammed with error entries.
- A large number of sound issues have been resolved.
- Sounds that error out and do not replay until a client reboot have been resolved.
- Non-English characters in certain circumstances would create petition issues. This has been resolved.


**Settings**


- The graphics cache setting has been added to the classic client.
- An error in the "Restart after changing graphics settings" window has been fixed.
- The "Sun is occluded by ships" option now applies to items on the login screen.


**Graphics**


- LOD processing for shadows has been improved.
- The drone interface window will no longer disappear when drones are launched.
- An issue causing the character selection screen would shift to blue has been resolved.
- Rendering of blueprint icons has been fixed.
- A problem where ship icons would be re-rendered an unnecessary number of times has been resolved.
- Certain cloaked ships now display properly on the cloaked player's client.
- The Minmatar have repaired the plasma routing on their military and mining stations.
- A glowing problem with the Tribal Issue Tempest has been fixed.
- The Light Electron Blaster II now has the correct model in the premium client.
- Lasers no longer have strange interactions with glass surfaces when bloom is enabled.
- NPCs now leave thruster trails.
- Capture Portrait works correctly again.
- Several issues with display and animation of mining lasers and strip miners have been fixed.
- The cloaking effect in the Premium Graphics Content client has been changed. The effect has less Strobing™ and more Throbbing™.
- Sentry Drone models are no longer Missing In Action.
- Gallente ship models have been touched up with darker colors and shinier metal surfaces.
- Bloom state leakage should no longer occur, especially on the log-in screen.
- GMs are able to make adjust wallet balances as needed. This was fixed in a hotfix earlier.
- The API access to data has been optimized in a special release.


**Patching**


- A warning indicating that a DirectX file was not installed because of user privileges has been added.
- The content patch from classic to premium should now check to ensure sufficient hard drive space before installing.
- The premium content upgrade will now warn that it is about to close EVE before it starts the process.


**Exploit Fixes**


- Contracts for ships with modules fitted will no longer cause a ship to be unable to undock.
- Customs officials have resumed issuing fines and confiscating illegal cargo.


**Please note:** No Windows system files were harmed during the creation or deployment of this patch.

**Trinity 1.0.1-1 Server-side changes deployed 9 January 2008**


- An issue causing the random unlinking of jump arrays after downtimes has been resolved.
- The issue causing situations where starbases would starting up with only 50% shields has been resolved.
- In rare situations, an issue would cause starbases to not work properly after system startup. This has been resolved.
- Some pre-Trinity release Rorquals were not upgraded to 4 production lines. This has been resolved.
- Some R&D agent missions were not working properly due to a server-side error. This error has been resolved.


**Trinity 1.0.1-2 Server-side changes deployed 15 January 2008**


- Fixed an exploit that could cause a node to crash.
- Fixed an exploit that would allow people to view the contents of a courier mission package prior to accepting.


**Trinity 1.0.1-3 Server-side changes deployed 16 January 2008**


- Forum upgrades


**Trinity 1.0.1-4 Client-side changes deployed 17 January 2008**


- This client-side change was revoked.


**Trinity 1.0.1-5 Server-side changes deployed 24 January 2008**


- Control tower shields will no longer drop to 50% after downtime.
- It is no longer possible to either create 0-run BPCs through blueprint copying nor to invent from 0-run BPCs.
- Fixes to derived standings logs.


**Trinity 1.0.1-5.1 Server-side change deployed 30 January 2008**


- Moving Nanite Repair Paste into any Capital Ship Corporate hangar division EXCEPT division 1 caused the Paste to simply vanish. This issue has been resolved.


**Trinity 1.0.1-5.2 Server-side change deployed 6 February 2008**


- Ships have been unfitted based in changes done in the Trinity expansion in December. For more details please see this [news item](//myeve.eve-online.com/news.asp?a=single&nid=1746&tid=1).
