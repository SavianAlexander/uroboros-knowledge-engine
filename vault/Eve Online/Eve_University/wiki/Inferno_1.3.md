---
title: "Inferno 1.3"
url: "https://wiki.eveuniversity.org/Inferno_1.3"
pageid: 5803
source: "EVE University Wiki"
categories: ["Expansions"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Inferno 1.3

# Version 1.3.4
- Released: Monday, November 5, 2012
1. # Fixes
- The In-game pop-up message for the daily downtime was incorrect but has been fixed. It used to say that an hour was reserved for the daily downtime, but after the fix it correctly states that only a half-hour is reserved for the daily downtime (note that we rarely need to use that full half-hour)
- Various backend fixes.

# Version 1.3.3
- Released: Wednesday, October 24, 2012
1. # Fixes
- A cap on Victory Points in **Factional Warfare** systems has been implemented. At this time the cap is 100 VPs past whatever threshold is needed to make a system vulnerable.
- Fixed a bug that has been occasionally causing system capture status in **Factional Warfare** to not update after downtime.
- Fixed a bug that was causing the client to hang when loading Characters.

# Version 1.3.2
- Released: Tuesday, October 23, 2012
1. # Changes
  1. # **Factional Warfare**
- Added Loyalty Point rewards for defending sites in your own faction territory. Amount of Loyalty Points gained is proportional to the vulnerable status of the system – the more vulnerable, the closer the rewards are with attacking sites.
- Attacking players capturing complexes in vulnerable Factional Warfare solar systems don’t receive Loyalty Points anymore.
- Added a donation tax to the Factional Warfare Infrastructure-Hub that is proportional to its respective faction war zone control. The more upgraded space a particular faction owns, the more Factional Warfare Loyalty Points will be wasted maintaining the donation tax instead of being normally spent.
- NPCs in Factional Warfare sites now contest the capture timer just like players would. This only happens for players attacking a site, defending players can still capture it without interference.
- Bleed-out from enemy players capturing sites on the same solar system than FW Infrastructure-Hub has been decreased from 50 to 10%.
- Loyalty Point store price reduction from War Zone Control Tier system has been moved to a raw gain bonus for all Factional Warfare related activities (PvP kills, site capturing and mission running).

<u>The old system was</u>:
- **Tier1**: LP store offers 4 times more expensive, LP gains unchanged
- **Tier2**: LP store offers 2 times more expensive, LP gains increased by 5%
- **Tier3**: LP store offers unchanged next to pre-Inferno levels, LP gains increased by 10%
- **Tier4**: LP store offers 2 times less expensive, LP gains increased by 15%
- **Tier5**: LP store offers 4 times less expensive, LP gains increased by 20%

<u>The new system is</u>:
- **Tier1**: LP gains reduced by 50%
- **Tier2**: LP gains unchanged next to pre-Inferno levels
- **Tier3**: LP gains increased by 75%
- **Tier4**: LP gains increased by 150%
- **Tier5**: LP gains increased by 225%

- Increased Loyalty Point costs for upgrading FW Infrastructure-Hubs.

<u>Old upgrade costs were</u>:
- **Level1**: 10,000 LPs
- **Level2**: 25,000 LPs
- **Level3**: 45,000 LPs
- **Level4**: 70,000 LPs
- **Level5**: 100,000 LPs
- **Buffer**: 150,000 LPs

<u>New upgrade costs are</u>:
- **Level1**: 40,000 LPs
- **Level2**: 60,000 LPs
- **Level3**: 90,000 LPs
- **Level4**: 140,000 LPs
- **Level5**: 200,000 LPs
- **Buffer**: 300,000 LPs

Further information about above outlined changes can be found in [this](http://community.eveonline.com/devblog.asp?a=blog&nbid=73491) devblog.
1. # Fixes
  1. # Graphics
- Resolved an issue that would remove the lines in the 3D starmap when switching between the solar system and star map.
  1. # Localization
- Incorrect translations for “bounty” and “volume” have been corrected in the German client.
- Various linguistic changes have been made throughout the Russian and German client.

# Version 1.3.1
- Released: Thursday, October 18, 2012
1. # Fixes
  1. # Graphics General
- Resolved an issue with **Planetary Industry** mode displaying a black screen when you are in your Captains Quarters with HDR enabled.
  1. # Localization
- The inventory window in Japanese and German clients will now correctly show the size of item stacks when in details or list view.
  1. # Market
- **DUST 514** items previously seeded for test purposes are removed from the market groups so they no longer appear in the EVE client.

# Version 1.3
- Released: Tuesday, October 16, 2012
1. # Changes
  1. # EVE Chat
- Settings and options in chat windows have been consolidated into two menus. Further information about the improved chat system is available in [this](http://community.eveonline.com/devblog.asp?a=blog&nbid=73468) devblog.
  1. # Market
- The market has been seeded with infantry equipment however current trade restrictions prohibit the sale of such items to capsuleers.
  1. # Planetary Districts
- New locations called "Districts" have been added to temperate planets in high security and factional warfare systems and are visible from space.
- Districts can be warped to via the planet context menu.
- A district satellite is visible while in orbit above a district in space.
- District satellites will appear globally on the overview while there is a ship on grid with it, including cloaked ships.
- A new group is available in the overview settings called Satellites, which can be used to show / hide them from your overview.
  1. # **Factional Warfare**
- Planetary districts are future **DUST 514** battle zones, and impact Factional Warfare System Capture Status in a solar system.
- Each district owned by a particular Factional Warfare faction affects the number of Victory Points needed to move a Factional Warfare system into a vulnerable state.
- If a district owner is the same faction than the one controlling the Factional Warfare system, the number of Victory Points needed to put the solar system into vulnerable mode is increased
- If a district owner is the opposing faction than the one controlling the Factional Warfare system, the number of Victory Points needed to put the solar system into vulnerable mode is decreased
- Each temperate planet in Factional Warfare space contributes by 12.5% to the System Capture Status Victory Point pool, for a maximum of 50% Victory Points in Factional Warfare solar systems with four temperate planets.
- Until **DUST 514** is fully implemented on **Tranquility**, planetary districts have been set to belong to the NPC faction that traditionally owned the Factional Warfare solar system before players interference. Further information is available in [this](https://forums.eveonline.com/default.aspx?g=posts&m=2048369&#post2048369) forum post.
- An icon has been added below the System Capture Status bar to represent this new information.

''Example
- Raa is a 0.3 solar system located in Factional Warfare space.
- Raa has 3 temperate planets, each having a certain number of districts. Each planet affects the System Capture Status by 12.5%, for a total of 37.5%.
- Districts have been set to the NPC faction that historically and traditionally owned the solar system before player interference, in this case the Amarr Empire.
- With such changes, it means the system will require 37.5% more Victory Points to capture if owned by the Amarr Empire FW militia, or 37.5% less Victory Points to capture if owned by the Minmatar Republic militia.
- This change may move a FW solar system in or out of a vulnerable state after the patch depending on how many temperate planets are present during deployment time.''

1. # Fixes
  1. # Character Creation and New Player Experience
- An issue with the Caldari Achura females bra straps always being visible has now been fixed.
- A texture issue with female coats has been fixed.
- A colouring issue with the male vest jacket has been fixed.
- A tucking issue with the male Sterling shirts has been fixed.
- An issue with missing sections on characters in stations has been fixed.
  1. # Player Owned Structures, Outposts and Stations
- Calendars will now show the correct fuel values remaining for POS towers in empire space.
  1. # Miscellaneous
- Fixed an issue where an enemy ships lock on your faction Infrastructure Hub in Factional Warfare would not be broken when defending the system.
  1. # Graphics General
- Renai tailors have renovated their esquire line of jackets ensuring that the shoulders are firmly stuck to the sleeve and their owner. The female esquire jacket should no longer display a gap between the upper arm and the jacket.
- Mesh clipping on the womens Acquire ´Structure´ Skirt has been reduced.
- Occasional white flashes on cargo jettison with some graphics cards were fixed.
- Enabling anti aliasing in the game menus has now an effect in the Character creator.
- Fixed an issue with graphical corruption of the Caldari station wreck asset.
- The planet wide 'oil spill' effect has been cleaned up on Dantbeinn II - the local environment is in a much better state now!
- Resolved an issue where the medium ship LOD was not released from memory.

1. # General
  1. # Uncategorized
- Removed visible gaps from some clothing items were removed.
- A selection of small geometry holes in Captains Quarters character clothing got fixed.
- Sleeper drones now have more than one missile damage area.
- Bombs detonation visual effect matches now server side hit information.
