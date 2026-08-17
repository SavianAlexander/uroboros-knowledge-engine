---
title: "Repairing security status"
url: "https://wiki.eveuniversity.org/Repairing_security_status"
pageid: 2287
source: "EVE University Wiki"
categories: ["Getting Started", "Guides"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Repairing security status

Although the majority of security status losses occur due to hostile acts, such as piracy or griefing, a player can sometimes lose a few points from accidental activities. Repairing this security status loss can be a tedious process but with a few alterations to the method, the time taken can be shortened. If a player is in a hurry, going straight to turning in Clone Soldier tags to Concord/DED can be very fast but expensive. See: **Security Tags** for more info. 

  - Note:** This content has a lot of misinformation in other locations, this has been updated per Vanguard, Dec 2024.

1. # Kill NPCs
Security status gains are achieved by **killing NPCs** from the various pirate corporations (Guristas, Sanshas, Serpentis, Angel Cartel, etc). Note that Faction rats such as Amarr or Gallente will only give faction standing changes, not security status.

  1. # Security gain mechanics
A security status gain occurs for the HIGHEST value outlaw NPC killed within a 5 minute time period.  These updates sometimes only happen every 10 minutes on the Security Status screen.  Changing systems does not help speed this up.

Each rat is worth a certain security percentage. In general, the harder the rat is to kill, the higher the bounty, and the higher the percentage. A good sense of what type of increase is the bounty associated with the rat.  Note, these sample numbers are with max .

| + Bounty per percentage sec status |
| :--- |
| Bounty (ISK) | Percentage Sec status |
| :--- | :--- |
| 11,813 | 0.0072% |
| 37,500 | 0.0575% |
| 74,063 | 0.0762% |
| 95,000 | 0.0780% |
| 142,000 | 0.0906% |
| 225,000 | 0.1050% |
| 345,000 | 0.1290% |
| 500,000 | 0.1920% |
| 650,000 | 0.2040% |
| 800,000 | 0.2160% |
| 950,000 | 0.2280% |
| 1,100,000 | 0.2400% |
| 1,250,000 | 0.2520% |
| 1,400,000 | 0.2540% |
| 1,550,000 | 0.2760% |
| 1,700,000 | 0.2880% |
| 1,850,000 | 0.3000% |

These updates are shown in game under Character Sheet, Interactions, Security Status.  They only show two decimal places initially, but can be hovered over to get 4 decimal places.  This screen will not automatically update it, it must be closed and reopened.

To figure out what the new security status will be:
> <Math> \displaystyle New\ Status = Old\ Status + ( ( 10 - Old\ Status ) \times Security\ Increase ) </math>

Example:
{{Example|
<math> \displaystyle \begin{align}
Old\ Status & = -0.2140 \\
Sec\ Incr  & = 0.0762\%\ ($74,063 \text{ bounty}) \\
\\
New\ Status & = (-0.2140) + \left( 10 - (-0.2140) \times \frac {0.0762} {100} \right) \\
& = -0.2062
\end{align} </math>
}}

  1. # Skills for increasing security status gains
Security standing can be maximized by training the  skill - each level trained provides a 5% bonus to effective security rating increases. Other **social skills** also affect security status in various ways.

  1. # The quick method
  - (The quickest method is to purchase and turn in **security tags** at a CONCORD facility. Barring that, as it can be expensive, may choose to pursue the options below.)**

Depending on the current skill level, three methods are available to pick from which will provide for a rapid increase in security status. In either case, the basic principle is the same: kill the highest value rat available, and leave the rest.  Kill more rats after 5 minutes and start the process over again.

Note that for each of the three methods below can be mixed and matched as the local conditions dictate. Don't feel to only stick to one method if another opportunity makes itself available.

  1. ## Method 1: Mission rats
This is most likely the slowest but easiest method.  A low level character capable of doing L1-L3 security **mission**s will want to pick up a number of security missions within 3-5 systems of each other. DO NOT PICK FACTION MISSIONS (Check [EVE-Survival](https://eve-survival.org) if unsure). Note that not all rats from missions and/or deadspace give a security status gain, only ones involving NPC non-empire rats.  

Pop into the mission space - kill a high value rat as part of the mission pocket and then move on. After 5 minutes have elapsed, do the same for the next mission. 

The nice part of this method is that if a player gets a couple of good missions in different systems, it can be milked each mission across 5-7 days. This is due to the mission reset that occurs each day so long as the mission remains uncompleted. So can essentially 'mine' the mission for security status for a few hours each day until the mission timer runs out or decide to complete the mission.

  1. ## Method 2: Belt rats
This is the fastest method for most players.  Being comfortable operating in low-sec or null-sec and having a ship capable of taking on rats in these areas, then **belt rat**ting will be faster than mission ratting. Find a rat in the first system and kill it. After 5 minutes, find a new set of rats, and kill the highest level rat again. Keep it up until the security status gains are achived or get bored and go do other things.

While doable in high-sec, in general, the value of belt rats in high-sec are so low as to not be worth it unless a rare rat spawns.

The lower the security of the system, the better the rats, the more increases possible.  Null sec actually goes negative, and these also increase the value and percentage of sec status.  This was tested in a -1.0 system, the lowest available, which also has the chance of spawning **faction and officer** rats that have much higher bounties and loot drops!

Another option is 'belt rat pruning'.  After finding a big rat spawn, kill the big rat, and then go to the next belt.  The previous big rat will respawn in a certain amount of time as long as the population of the system is similar.  If a belt has crappy rats, like cruisers and frigates, kill one, that starts the timer again for the 5 minutes.  Kill all the rats to despawn the site, allowing the system to repopulate it with different types of rats next time.

  - Skyhook**s also spawn rats, but these rats are usually further away from the landing spot, so are slower to run.  **Stargates** also can spawn creatures.  And finally the **Desolate Asteroid Belt** also collects rats.

Combing these methods, the optimal scenario is to find a friendly citadel in an extremely low security system, with at least 8 belts.  
- Example: [RZ8A-P](https://evemaps.dotlan.net/system/RZ8A-P) at -0.96 sec status with 15 belts + 9 skyhooks at planets + 4 gates + 1 desolate, so 28 total places to check.
- Warp to a belt, kill a small rat. Starts the 5 minute timer.
- If the belt has a big rat, kill the biggest big rat.  Set for 5 minutes, can prune in the meantime.
- If the belt is all small rats, warp to the next belt till finding a big rat.
- Once in prune mode, warp through the previous sets belts, killing small spawns.

The **algos** for newbies, blaster ships like **hecate**s with **void**, and **bomber**s are particularly good at this style, though tethering/docking between belts might be necessary for lower skill point players.

  1. ## Method 3: Anomaly rats
Doing **combat sites** or scanning down **anomalies** is the most common method, as players often do null sec ratting to make money. Killing rats in these missions gives a slow build up over time, where every 5 minutes, a minor increase on the largest rat killed during that time.

There are up-sides and down sides to anomaly ratting. One of the down sides is that anyone can obviously warp into the middle and finish it off while security mining other sites. The upside, especially in high-sec, is that other people will often leave an anomaly pocket alone if they see that there are wrecks in the area -- it is not guaranteed but certainly, a pocket will persist until all the rats in that pocket have been eliminated.

  1. ## Notes
# Skip any **empire faction** missions - these do not give security status increases.
# Not all rats give a security status increase. 
1. # Sentry guns for example have a bounty on them but do not give status increase even though other rats around them may.
1. # Named NPC targets typically do not give bonuses (e.g. Mercenary Lieutenant)
# Trading up missions doesn't always work - get 2 or 3 decent missions, might want to stick with those even if they don't test PvE abilities. This is because it could end up getting 5 or 6 missions in a row (such as **Gone Berserk** or **Rogue Drone Harassment**) that do not give any security status increase even though they look as if they should.

1. # How long does it take
This chart shows a sample of the time it might take to reach different levels.  It's based off a 1.25 mil bounty battleship every 5 or 10 minutes, depending on column.  This gives rough ideas how long it would take to recover from a -10.0 to -1.99, the bare minimum to enter all high sec safely.

| + How long does it take |
| :--- |
| Sec Status | 5 minutes kills | 10 minute kills. |
| :--- | :--- | :--- |
| -10.0 -> -8.99 | 1:45 | 3:30 |
| -8.98 -> -7.99 | 1:50 | 3:40 |
| -7.98 -> -6.99 | 1:50 | 3:40 |
| -6.98 -> -5.99 | 2:00 | 4:10 |
| -5.98 -> -4.99 | 2:05 | 4:10 |
| -4.98 -> -3.99 | 2:20 | 4:40 |
| -3.98 -> -2.99 | 2:30 | 5:00 |
| -2.98 -> -1.99 | 2:40 | 5:20 |
| -1.98 -> -0.99 | 2:50 | 5:40 |
| -0.98 -> 0.01 | 3:10 | 6:20 |
| 0.02 -> 1.01 | 3:35 | 7:10 |
| 1.02 -> 2.01 | 3:55 | 7:50 |
| 2.02 -> 3.01 | 4:25 | 8:50 |
| 3.02 -> 4.01 | 5:40 | 19:00 |
| 4.02 -> 5.00 | 6:05 | 12:10 |

To add these together, can easily get some useful numbers.
- Going from -10 and want to get to sub -5 to enter 0.5 space, add together them and get somewhere between 9:35 hours and 19:10 hours
- Going from -10 to -1.99 to enter all high sec safely, between 17:05 hours and 34:10 hours.
- Going from -10 to 0.01, for non-flashy yellow, between 23:40 and 46:10 hours.
- And from -10 all the way to the max of 5.0, between 46:10 to 92:20 hours.
- Most ratters end up going from 0 to 5.0 and should take them between 23:05 hours and 46:10 hours.

The google sheet formula is: ***=oldsec+((10-oldsec)*(percent))*** and then just list them down.  If killing only cruisers, these times can more than double.

  1. # Missions to avoid
Certain Missions look as if they should give a security status increase but they don't. The following missions should be declined.

# Any mission that is an empire faction mission (see [EVE-Survival](https://eve-survival.org) if unsure)
# **Gone Berserk**
# **What Comes Around Goes Around**
# **Silence The Informant**
# **Rogue Drone Harassment**
# **Cut-Throat Competition**

1. # Tags
  - Exchanging tags for security status** is easy but expensive.  (see also: **Security tags** and [WantToTrade: Tags for Security Status](https://www.eveonline.com/news/view/wanttotrade-tags-for-security-status), a dev blog on the subject).

1. # External links
- [Tags for sec calculator](https://www.fuzzwork.co.uk/sectags/) - Use to compute how much it would cost to repair it.
- [Null Sec Ratting Guide](https://www.wckg.net/PVE/null-sec-ratting) - Has Algos fitting for null sec ratting, including a belt ratting guide.
