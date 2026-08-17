---
title: "Probe scanning"
url: "https://wiki.eveuniversity.org/Probe_scanning"
pageid: 19057
source: "EVE University Wiki"
categories: ["Exploration"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Probe scanning

Every ship in EVE, with the exception of **shuttles** and **freighters**, can fit a Scan Probe Launcher module. These launch probes increase the number of types of objects that can be detected and the range at which they can be scanned. In addition, probes provide distance and coordinate information.

1. # Using probes
All scan probes can be used for finding **cosmic signatures**. Combat scan probes can find structures, ships, and drones. Wrecks, cargo containers, and cloaked ships cannot be scanned with probes.

(Read **Probing In Simple Steps** for a more detailed guide, with tips and troubleshooting.)
- Look at the system scanner (default shortcut +) to determine if there are any cosmic signatures to be found.
- Launch your probes and scan. Use the filter to limit your results to what you want to find.
- Once you get a result, position probes to cover that result.  This may be as easy as moving them around a little or covering a sphere. Either way, keep in mind results from wide scans can be *extremely* inaccurate.
- With luck and/or skill, you will get a "one dot" result.  If you get circles or more spheres, your initial guess was off and you need to reposition and try again.
- Once you get it down to one result, close the probes in, bring them to the same position as the result, drop scan radius, and re-scan.
- Repeat the process of dropping range, positioning arrows on the resulting circle, and rescanning until you get your result.  If you hit the minimum probe range and still can't get 100%, try repositioning your probes more closely to the signature; holding ALT and sliding the probes closer to the target works well. There are some sites that you may not be able to probe; to get them, try to increase your "probe scan strength". You can use a Sisters launcher & probes, rig your ship, buy hardwired scanning implants, scanning arrays, and/or train higher levels of the relevant skills.

  1. # Rearranging probes
- By default all probes will move as one constellation unless you hold , , or  which modify how probes are moved. Holding  moves a single probe instead of all at once,  makes them resize and control moves them radially around center point, useful for pinpointing those sites which are hard to get 100% on. This allows for some very fast repositioning of probes.
- The probe-cube can be clicked and dragged.  If you grab the top or bottom, they slide on a horizontal plane, if you grab the sides of the cube, they slide on a vertical plane. This is why every so often you grab the cube and it slides away to somewhere weird - you accidentally grabbed the side of the cube instead of the top.
To reset the formation press either of the two preconfigured probe-patterns to reset both scan-range and position. This does not however reset probe constellation position in space.

  1. # Where to find sites
Sites only seem to spawn in a sphere 4 AU around celestials (may only be planets).
If you are scanning large reaches of empty space, you might find mission sites and abandoned drones, but probably not much else.

  1. # Solar System Map
The Solar System Map can be rotated using the Left Mouse Button and panned using the Right Mouse Button as well.
Clicking an object (celestial body, station, probe, signature etc.) changes the pivot point when rotating with the Left Mouse Button. Hint: Double clicking on the probe cube sets the probe cube to be the rotation pivot point, and re-centers the view to probe cube.

  1. # Loading probes
Carry exactly twice as many probes as you use at a time. When you load your launcher initially, only load the number of probes you can have active.  (For example, if you have 8 probes active, carry 16 but only load 8.)  As soon as you've launched your maximum number of probes and are busy placing them, the launcher will automatically load the next stack -- exactly the amount you need for the next system (be aware, activating a cloaking device while the reload timer is ticking down will cancel the reload due to being cloaked).  That way, the launcher will always be ready without you ever having to manually load it.

  1. # Results, and what they mean
- Sphere:  The result is somewhere in the sphere.  One probe only has a hit and approximate range.  You *can* get multiple probes with independent hits, it can be messy.  This is the least accurate hit.
- Circle:  Two probes have approximate distances.  More accurate, and likely to yield better hits with more probes. The target anomaly is located near the circle.
- Two Dots:  Three probes have distances, which narrows it down to between two possible locations.  Likely to be more or less accurate, but beware of deviation. Target anomaly has been narrowed down to being near one of the dots.
- One Dot:  Four or more probes can see the result.  Once scan strength reaches 100%, the result will be **warp**able.

1. # Probe attributes

Probes have three attributes that affect scan results: sensor strength (higher is better), maximum deviation (lower is better) and base scan range.  

  1. # Base Scan Range
Base scan range dictates what scan ranges the probe can use. For core probes, this is always 0.25 AU while combat probes have a base scan range of 0.5 AU. The sensor strength and maximum deviation are both given at the base scan range. This can make combat probes seem much worse than core probes. But to get comparable stats you need to multiply the combat probe stats by two so that you are comparing sensor strength and scan deviation at same scan range and see that the combat probes are actually equal to core probes.

Smaller scan range gives better results but scans a smaller volume. This makes core probes better at scanning hard to scan signatures where the smallest scan range needs to be used. On the other hand combat probes can be used to cover a larger 64 AU scan area for a very rough system scan. When scanning with ranges larger than 0.25 AU but smaller than 64 AU it will not matter which probes are used.

  1. # Maximum Flight Time
Maximum Flight Time limits for how long probes can be kept in space. For Republic Security Services ("RSS") probes this is 16 minutes and 40 seconds, while all other probes have 1 hour, 6 minutes and 40 seconds. If probes are left in space for more than this duration they will automatically return to the cargo bay as long as there is sufficient space for them, if not they will be lost.

  1. # Maximum Deviation
The deviation is the distance between the scan result shown on the map and the actual location of your target.

The actual deviation cannot be calculated at this time because it is unknown how CCP has factored signal strength into the equation. However, the maximum deviation, the worst case scenario, can be calculated.  The stronger your signal strength, the less actual deviation you will have - therefore the deviation of your scan will always be less than the distance shown below. (Knowing your relative signal strength will help you get an idea of how far way that dot might actually be from your target.)

In order to calculate the maximum possible deviation you use the constants provided for the type of probe, the scan size your probes are set to, and your skill levels of  and .

Here is the formula:

> <math> \displaystyle \text{Max Deviation} = \text{Base Maximum Deviation} \times \left( \frac{ \text{Scan Range} } { \text{Base Scan Range} } \right) \times \left( \frac{ 100 - \text{Astrometrics level} \times 5 } {100} \right) \times \left( \frac{ 100 - \text{Astrometric Pinpointing level} \times 5 } {100} \right) </math>

The use of probes requires at least Astrometrics I and Astrometric Pinpointing requires Astrometrics IV.

Below is a table that shows how your Astrometrics skill affects the maximum possible deviation of scanner probes.  Keep in mind that while Sisters probes and/or launchers have no effect on maximum deviation, they do have an effect on signal strength that will affect the deviation that you see in your scans.

Note that as your Astrometrics skill increases, the maximum deviation at each increment of the probes' scan range decreases.  Referring to the table for an example: if you have  Astrometrics I, with your probes set to a 4 AU scan range your maximum deviation is as much as 1.9 AU.  Increasing your Astrometrics skill to level IV reduces the maximum scan deviation at that scan range to 1.6 AU.

Another thing to note is that both combat and core scanner probes experience the same maximum deviations at the same scan ranges.  The reason is that although the core scanner probe has a base maximum deviation of 0.125 AU and the combat scanner probe has a base maximum deviation of 0.25 AU (implying the core probe is more accurate), the two types of probes have base scan ranges of 0.25 AU and 0.5 AU, respectively.  Plugging those numbers into the equation above yields the same maximum deviations at each scan range for both kinds of probe.

| + Maximum deviation at different ranges and Astrometric levels |
| :--- |
| 0.25 AU
| 0.1188 || 0.1125 || 0.1063 || 0.100 || 0.0938 |
| :--- |
| 0.5 AU
| 0.238 || 0.225 || 0.213 || 0.200 || 0.188 |
| :--- |
| 1 AU
| 0.475 || 0.45 || 0.425 || 0.400 || 0.375 |
| :--- |
| 2 AU
| 0.95 || 0.90 || 0.85 || 0.80 || 0.75 |
| :--- |
| 4 AU
| 1.9 || 1.8 || 1.7 || 1.6 || 1.5 |
| :--- |
| 8 AU
| 3.8 || 3.6 || 3.4 || 3.2 || 3.0 |
| :--- |
| 16 AU
| 7.6 || 7.2 || 6.8 || 6.4 || 6.0 |
| :--- |
| 32 AU
| 15.2 || 14.4 || 13.6 || 12.8 || 12.0 |
| :--- |
| 64 AU
| 30.4 || 28.8 || 27.2 || 25.6 || 24.0 |
| :--- |
|  |

1. # Scan results
Scan results are divided into cosmic signatures and cosmic anomalies depending on how they are located. They are also split into wormholes, combat, ore, gas, data and relic sites based on their contents.

  1. # Cosmic anomalies
Cosmic anomalies are PvE sites that can be found throughout EVE. They are found using the system scanner and require no skills or equipment to locate. To locate cosmic anomalies, simply open the probe scanner window where they are visible as warpable sites.

- ****Combat sites**** are ungated pockets with multiple waves of rats to kill. They can drop faction items or escalate to new sites.
  - **Besieged Covert Research Facilities** are special combat sites that are found only in low-sec. They containing multiple cruiser- and battleship-class NPC rats to be killed with a combat ship. In addition, they may contain destructible structures with loot.
- ****Ore sites**** contain **asteroid**s to be mined for minerals or ice products; generally the type of ore matches the regular ore from the asteroid belts in this area of New Eden but there is an important exception referred to by players as **border/A0 ores**.

  1. # Cosmic signatures
Cosmic signatures are scannable locations in space. To locate a cosmic signature it must be scanned with scan probes. You can see in the scan window whether a system contains cosmic signatures, but identifying them and pinpointing them requires scan probes. The type is identified at 25% scan, the name is revealed at 75% scan and the site is warpable at 100% scan.
- ****Combat sites**** are gated deadspace complexes with rats to kill. They can drop valuable faction modules and deadspace modules and can escalate into expeditions.
- **Gas sites** contain gas clouds that can be harvested. For more details see **Gas cloud harvesting**.
- **Relic sites** contain containers that need to be **hacked** with a relic analyzer. In normal space they do not contain any dangerous elements, for more details see **relic and data sites**.
- **Data sites** contain containers that need to be **hacked** with a data analyzer. They range from completely safe to deadly dangerous, for more details see **relic and data sites**.
- ****Wormholes**** are temporary unstable connections between two systems.
- ****Ore sites**** also include 'hidden' deposits which must be scanned to reach.

  1. # Minimum sensor strength
The minimum probe sensor strength is 42 (this is a base strength of 40 for a Core Scanner Probe plus  5% due to Astrometrics I = 42). This is sufficient for scanning cosmic signatures up to Level III. For Level IV signatures you require a Probe strength of at least 72, while for Level V signatures you require a probe strength of at least 104.

  1. # Site respawn mechanics
Much of the information surrounding the respawn mechanics of cosmic signatures is based on theory, with little hard data offered by CCP. Nevertheless, the sites will respawn **immediately** after being fully cleared by a player. It is unknown what range the new site will spawn in (if it's in the same region or not) or whether it will be of the same or similar type as the one cleared. Note that, based on this information, we know that **sites will not respawn after daily downtime**. They will only spawn when sites are cleared somewhere else within the game world.

1. # Ships and equipment

  1. # Ships
Scanning can be done in any ship that has a high slot for a probe launcher. However, there are ships with innate bonuses to scanning.

Each race has a T1 frigate with a 7.5% increase to probe strength per level of racial frigate skill trained. They also gain a +5 bonus to virus strength that helps with **hacking**.

- 
- 
- 
- 

Covops ships are the direct upgrade from T1 scanning frigates. They get an increased 10% to probe strength, 5% probe deviation bonus per level of racial frigate skill trained, +10 bonus to virus strength and can use covert ops cloaking devices.

- 
- 
- 
- 
- 

The **Sisters of EVE** faction ships all have a 37.5% role bonus to scanning and the frigate and cruiser are also able to fit a Covert Ops cloak. They also get bonus to armor resists, energy turrets and drones and +10 virus strength making them capable combat crafts and hackers. They have lower skill requirements than CovOps T2's, but they are insanely expensive compared to other T1 ships and considerably more expensive than T2 ships. 
- Frigate.  (CPU is low, making it hard to fit an Expanded Probe Launcher.)
- Cruiser.
- Battleship. Role Bonus: 50% bonus to Core and Combat Scanner Probe strength. Cannot fit a Covert Ops cloak.

The **Society of Conscious Thought** ships gain same 37.5% scan probe strength as sisters ships. They also gain bonus to all weapons systems making them well rounded ships.

- Frigate. A special T1 frigate at around half the price of an  but provides most of the scanning & Hacking bonuses of the Astero. Including Covert Ops Cloaking ability and +10 virus strength. And with the role bonuses, can easily fit an expanded probe launcher. It is the only **Society of Conscious Thought** ship with +10 virus strength bonus.

- Destroyer.
- Battlecruiser.
- Battleship.

  - Strategic cruisers** can be fitted with the **Covert Reconfiguration** subsystem that gives them probing bonuses and ability to use Covert Ops Cloak.  This might be useful if you're in a roaming gang of strategic cruisers.

- 
- 
- 
- 

  1. # Ship equipment
To do scanning you need a Probe Launcher module and some Probes. All other scanning modules and rigs are just to make scanning easier.

Full list of normally used scanning equipment:

| - | link=|]] | **Core probe launcher** is the backbone of any scanning ship. This easy to fit module launches core scanning probes in space allowing you to perform probe scanning.

Comes in base T1, improved T2 (+5% scan strength) and Sisters faction (+10% scan strength) variants. |
| :--- | :--- | :--- |
| link=|]] | **Expanded probe launcher** is much harder to fit variant of the core probe launcher. The expanded probe launcher offers no benefits over core probe launcher when scanning with core probes. But the expanded probe launcher can use combat scanner probes that allow scanning of ships, structures and drones.

Comes in base T1, improved T2 (+5% scan strength) and Sisters faction (+10% scan strength) variants. |  |
| link=|]] | **Core scanner probes** are the basic ammunition for the Core Probe Launcher. You can reuse them, and the Core Probe Launcher can hold eight at a time. You can technically locate an exploration site with as few as four, but for convenience, consider carrying at least one full reload (8), or even several reloads. 

The probes also comes as Sisters variant with 44 scan probe strength instead of the normal 40. They’re a bit expensive, but vastly more affordable than the Sisters launcher. |  |
| link=|]] | **Combat scanner probes** are used for scanning ships, drones and structures. The combat probes are much bulkier than the core scanner probes and thus can not be used with the core probe launcher, instead you need the expanded probe launcher. While combat probes can be used for scanning signatures it is usually done with normal probes.

The probes also comes as Sisters variant with 22 scan probe strength instead of the normal 20. Note that due to the base scan range being twice of the core probes the combat probes are equally good as core probes unless scan range of 0.25 AU is needed. |  |
| link=|]] | **Scan rangefinding array** increases the scan strength of your probes. This will make it easier to scan signatures by reducing the scan deviation and making weaker signatures scannable. |  |
| link=|]] | **Scan pinpointing array** reduces the scan deviation while scanning. This means that the partial scan result is more likely to be closer to the actual signature. This will allow you to reduce the scan formation more aggressively speeding up the scanning. But this will not allow you to scan harder signatures. |  |
| link=|]] | **Scan acquisition array** speeds up the scan process by making the probes scan faster. Only one scan acquisition array can be fitted. |  |
| link=|]] | **Gravity capacitor upgrade** rig increases the scan strength of your probes. It is usually better to fit two T1 rigs instead of one T2 rig. But if you aim for maximum scan strength and have enough scanning modules to incur stacking penalties it may be better to go with one T2 rig. |  |

  1. # Implants and Attribute enhancers
There are numerous Implants that range from almost disposable to exceedingly expensive.   
- Attribute Enhancers occupy slots 1 to 5. Some of these also affect Skills.
- Skill Enhancers occupy slots 6 to 10.

| + Attribute Enhancing Implants |
| :--- |
| Probe Scan Strength |
| Low-grade Virtue |

| + Skill Hardwiring Implants |
| :--- |
| 6 |
| 7 |
| 8 |

1. # See also
- [Alebrelle Kuatu's Probe Scanning Basics](https://www.youtube.com/watch?v=wErCHjNTsRA)
- [Newb Eden's Exploration Pt1: Scanning Like a Boss!!](https://www.youtube.com/watch?v=hCOulmmn_4Q)
- [Probe scanning deviation breakdown](https://www.reddit.com/r/Eve/comments/1cf383o/probe_scanning_deviation_breakdown) reddit post
