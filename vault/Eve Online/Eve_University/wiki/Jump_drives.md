---
title: "Jump drives"
url: "https://wiki.eveuniversity.org/Jump_drives"
pageid: 6281
source: "EVE University Wiki"
categories: ["Game mechanics", "Ships"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Jump drives

- Jump Drives** are a means of interstellar travel, and the main alternative to the standard network of stargates. Ships with built-in jump drives can use their drives to instantly travel to a friendly **Cynosural Field** or Pharolux Cyno Beacon in another star system, within a limited range and at the cost of consuming Isotopes as fuel.

All **capital ships**, **Jump Freighters**, and **Black Ops Battleship**s have built-in jump drives. Jump drives allow for rapid movement and deployment of both subcapital and supercapital ships across long ranges, and are commonly used for defensive, offensive, and logistical purposes.

1. # Operation
Jump drives are not modules. They are built into the hull of the ship. All ships that contain a jump drive require the  skill to pilot. The following classes of ships contain jump drives: 

- **Dreadnoughts**
- **Carriers**
- **Supercarriers**
- **Titans**
- **Jump Freighters**
- **Black Ops Battleship**s
- **Capital Industrial Ships**

Unlike stargates, which are free to use, jump drives require fuel. The jump drive comes with a special fuel bay. The fuel required depends on the faction that constructed the jump drive, and can be produced by refining **corresponding ice**. The respective fuel type for each faction is: 

| Faction | Isotope type |
| :--- | :--- |
| Amarr, Blood Raider, Sansha, CONCORD | Helium |
| Caldari, Gurista | Nitrogen |
| Gallente, ORE, Serpentis | Oxygen |
| Minmatar | Hydrogen |

The fuel cost for each jump does not depend on the number of stargate jumps to the destination. It depends on the straight-line distance between the two systems in space, measured in light-years. Each jump drive has a maximum jump range, and consumes a certain amount of fuel per light-year. These qualities are modified by skills:

- The skill  increases the jump range by 20% per level which means at the maximum of level five the range is doubled.
- The skill  reduces the fuel consumption by 10% per level which means that you use half the fuel at the maximum level of five.

Jump freighters also have their required fuel reduced by the  skill, required to fly them. 

The following table shows the range, base fuel consumption, and fuel capacity of all jump drive-capable ships.
{{#css:

1. compare td:nth-last-child(-n+3) {
  text-align: right;
 }
1. compare td:nth-last-child(4),
1. compare td:nth-last-child(5) {
  text-align: center;
 }
/* This line is needed because of the use of rowspan */
1. compare td:first-child {
  text-align: left;
 }
}
}}

| Ship class
! rowspan= 2 | Ship type
! colspan= 2 | Range (ly)
! rowspan= 2 | Fuel per ly(units)
! colspan= 2 | Fuel bay |
| :--- |
| Base | Max Skills | (m3) | (units) |
| :--- | :--- | :--- | :--- |
| Capital | Dreadnought | 3.5 | 7 |
| Carrier | 3 000 | 100 000 |  |
| FAX |  |  |  |
| Command Carrier | 3.75 | 7.5 | 7 500 |
| Lancer | 4 | 8 | 20 000 |
| Super Capital | Supercarrier | 3.0 | 6 |
| Titan | 60 000 | 2 000 000 |  |
| Jump Freighter | Anshar | 5.0 | 10 |
| Nomad | 8 200 |  |  |
| Ark | 8 800 |  |  |
| Rhea | 10 000 |  |  |
| Black Ops Battleship | 4.0 | 8 | 700 |
| Capital Industrial Ship | Rorqual | 5 | 10 |

Finally, activating a ship's jump drive consumes 95% of the energy in its capacitor (reduced by 5% per level of ). Because Jump Drive Operation level five is required for the  skill, it is usually assumed to be at level five. At this level, 71.25% of the capacitor is consumed which rounds up to 75% in everyday communications and is colloquially called "jump cap". Because of the huge amount of cap needed for jumping, capital ships usually have a capacitor booster fitted. But, in special cases you would rather fit cap rechargers and capacitor power relays to reduce the amount of time between jumps.

Activating a jump drive has similar constraints to activating a warp drive: jump drives cannot be activated if the ship is either inside a **warp interdiction bubble** (from an **Interdictor** or **Heavy Interdiction Cruiser**, or if the ship has been **warp disrupted** below a Warp Core Strength of 0. (However, a jump drive can be activated regardless of the jumping alignment.)

1. # Jumpdrive Isotope Usage Formula
The amount of fuel used in a jump can be calculated with the following formula.

> <math> \displaystyle\rm \text{Isotopes used} = D \times F \times ( 1 - 0.1 \times JFC ) \times
{\color{green} ( 1 - 0.1 \times JF )} \times
{\color{red} ( 1 - JDE_1) \times ( 1 - ( JDE_2 \times 0.869 )) \times ( 1 - ( JDE_3 \times 0.571 )) \times ( 1 - ( JDE_4 \times 0.283 ))} </math>

The white part of the formula applies to all **jumpdrive capable ships**. The green part only applies to **Jump Freighters** and the red part only applies to **Jump Freighters** and **Rorqual**s. The red part is **stacking penalized** so the order of the modules is from highest bonus to lowest bonus.

| -
! Variable Name !! Meaning !! Valid Values !! |
| :--- |
| D |
| F |
| JFC |
| JF |
| JDE*x* |

1. # Cynosural Field Types
- Cynosure* (pronounced like "sigh no sure") is a little-used word outside of EVE. It means a guide, or a person or thing that draws attention towards itself. It originates in the ancient Greek name for the North Star, making it a very appropriate term for the cynosural fields of New Eden.

Cynosural Fields come in three varieties: **normal** or so-called **"hard" cynos**, **covert cynos**, and **industrial cynos**. The three types differ in important ways in their equipment requirements, in their fuel use, and in the ships which they can transport. Cynos cannot be lit in **high-sec**, and while they can be lit in **wormhole space** they serve no purpose as jump drives cannot jump to systems in wormhole space. **Mobile Cynosural Inhibitor**s prevent the activation of cynos in a 200km radius but do not remove existing cynos. Solar systems as a whole can be cyno jammed either through the navigation structure **Tenebrex Cyno Jammer** or a **Sansha Incursion**.

  1. # Normal Cynosural Fields

Ships with a jump drive can only jump to cynosural fields or beacons. Cynosural beacons are provided by a player-deployed navigational structure, the **Pharolux Cyno Beacon** (colloquially simply called "beacon" or "cyno beacon"). Cynosural fields are generated or "lit" by the ship module Cynosural Field Generator I. Cynosural fields and their generators are colloquially abbreviated as "cyno". A normal (or "hard") cynosural field can be seen on the overview from any place in the system and is "warpable". Further, it appears on the universe map.

The Cynosural Field Generator module requires the skill  at level one to be fitted. Its base activation time is ten minutes and it has a base consumption of 500 Liquid Ozone per cycle. As the Liquid Ozone consumption is reduced by 10% per level of Cynosural Field Theory, the maximum consumption is actually 450 Liquid Ozone per cycle, and the minimum consumption is thus 250.

If you want to light a cyno you have to be in a fleet (only fleet members can jump to that cyno) and slower than 500 m/s. After you light the cyno your nominal speed becomes zero but you continue to drift and can also be bumped, but the cynosural field stays at the position, where you lit it. Further, you cannot dock in a station or structure and cannot eject, but you can self destruct. Indeed you can light a cyno after you initiated the self destruct sequence. This is used as a trick for extra safe traveling. The cyno needs several seconds until it appears on the universe map. If you light the cyno shortly before you self destruct and immediately jump to it, you can minimize the risk of being caught. But, be aware that if you jump to a cyno in the same moment as the cyno ship dies, you still jump but you land at the destination system's star, not at the former spot of the cyno.

As of the September 2019 release, cynos can only be fitted to **Force Recon**s and **Black Ops Battleship**s. Both Force Recons and Black Ops (except the **Marshal**) have 50% reduced cycle time for cynos (both normal and Covert), but Force Recons add an 80% fuel cost reduction on top of the reduced cycle time (reducing the duration to 5 minutes and only 50 Liquid Ozone). Because of this change, recent cyno vigils have typically been done with hulls that can fit an Industrial Cynosural Field instead.

  1. # Covert Cynosural Fields
Covert Cynosural Fields are a special variant of the "normal" Cynosural Fields discussed above. In a context in which either type might be mentioned, a "normal" cyno is often called a "hard cyno".

Unlike a normal cyno, a Covert Cynosural Field is only visible on the overview if you are on grid and can be generated even in cyno jammed systems. The module to generate a covert cyno is named Covert Cynosural Field Generator and can only be fitted to certain ships. Those are **Black Ops Battleship**, **Blockade Runners**, **Covert Ops Frigates**, **Force Recon Ships**, **Stealth Bombers**, and **Strategic Cruisers** (with the covert subsystem); further, the single hulls **Etana**, **Prospect**, and **Rabisu**. As a rule all ships which can fit a covert cloak (except the **Sisters of EVE** & **Deathless Circle** ships) can fit a covert cyno. 

The Covert Cynosural Field Generator requires  at level V. Its activation time and fuel consumption is only a tenth of the usual cyno. As Cynosural Field Theory has to be at five, it always only needs 25 Liquid Ozone which greatly reduces the cargo space needed. Otherwise, the module still immobilizes the ship generating the field and can only be used if it is slower than 500 m/s. The bonuses of **Force Recon Cruisers** and Black Ops Battleships apply to covert cyno as well, which means they are pinned down for only 30 seconds.

Only **Black Ops Battleship**s can jump and bridge to covert cynos. Black Ops Battleships can only bridge ships which are able to fit a Covert Ops Cloaking Device (it doesn't have to be fitted). Bridges by Black Ops only last 20 seconds. For more details about bridging mechanics see the below **section** about it.

  1. # Industrial Cynosural Fields
An Industrial Cynosural Field Generator I works much like an ordinary cyno, but with some key differences. First, it can only be jumped to by **Jump Freighters**, **Capital Industrial Ships** and **Black Ops Battleship**s. The latter two can also bridge to it. Second, similar to Normal Cynosural Fields, Industrial Cynosural Fields appear on the Overview when lit. It has a base fuel consumption of 800 liquid ozone per cycle, with a minimum consumption of 400 LO/cycle with Cynosural Field Theory V. Industrial cynos can only be fitted to:

- the **Venture**, which has a role bonus cutting the industrial cyno's Liquid Ozone cost in half
- **Haulers**
- **Blockade Runners**
- **Deep Space Transports**

Arriving ships materialize at a random point 5km from the Cynosural Field location. Jump Freighters will typically prefer to dock instantly, which requires the Cynosural Field to be at least 5km within the structure's dock range. However, if the Cynosural Field is located too close to the structure (<5km), then the arriving ship may materialize with the structure, causing it to be ejected at a high velocity and be far from the dock range. Standard warp mechanics will not allow the ship to warp back to the structure until it has slowed sufficiently to align and warp. For more discussion of safe jump freighter piloting, see **Jump Freighters**.

Industrial Cynos are sometimes used for their visual effect during "cyno vigils" to remember eve online players who died in real life. If other pilots are aware of such an occasion, they usually don't attack those vigils out of piety.

1. # Bridging
A Jump Bridge is a way for a **Titan**, **Black Ops Battleship** or **Rorqual** to launch its allies, who cannot use jump drives, across space to where they are required.

A (Covert)/(Industrial) Jump Portal Generator allows the user to create a bridge to another system. The Jump Portal Generator can only be fitted on a Titan, the Covert version only to a Black Ops Battleship, and the Industrial version to the Rorqual. They are high-slot passive modules which enable the bridge function of the ship. The module will visibly activate and cycle while the bridge is active, but cannot be manually activated.

Titans can bridge all subcapital ships. Black Ops Battleships can only bridge ships which are capable of fitting the **Covert Ops Cloaking Device**. (The ships do not need to have the module fitted in order to use the bridge.) This includes the **Sisters of EVE** ships, and **Strategic Cruisers** fitted with the Covert Reconfiguration subsystem. Rorquals can only bridge **Mining Frigate**s, **Expedition Frigates**, **Mining Barges**, **Exhumers**, and the **Porpoise**.

Using the module requires  skill at level one. 

The ship with the generator must first be within jump range of a cyno lit by a member of the fleet.

Once the cyno is lit, the Generator pilot can create a *jump bridge* (the "Bridge" option is right next to the "Jump" option), which behaves something like a temporary stargate for the other ships in their fleet.

Titan jump bridges can only be created to standard Cynosural Fields, or Cynosural Beacons. Covert jump bridges can be created to any form of cyno.

A titan jump bridge stays open for one minute, and immobilizes the ship holding it open. Covert and Industrial jump bridges stays open for 20 seconds.

The act of opening a Titan bridge costs 500 units of Strontium Clathrates, modified by . There is no cost for opening a Black Ops or Rorqual bridge. When ships jump across the bridge, they consume fuel from the bridging ship's fuel bay. If there is no fuel in the fuel bay, the ship will consume fuel stored in the cargohold.

For other ships to be able to jump through, they must be in the same fleet and within 2,500 meters of the ship creating the jump bridge. When the jump bridge is up, the Generator pilot should announce it. The pilot that wants to jump then clicks on the jump bridge ship in space or in the overview. Either method opens a box with the the option "Jump through to [SYSTEM NAME]". If clicked too soon, these two options do not automatically update and require you to click again. Another way is to bring up the radial menu on the jump bridge ship or the pilot in the watch list, which does update if you hold it open. The symbol you click on is at 12:00 o’clock and is a stick-figure person. This symbol highlights and becomes active when the jump bridge is up.

Ships that jump through a jump portal use up isotopes from the bridger's fuel hold based on the jumping ship’s mass. Because of this, it is good practice in fleets to turn your **propulsion equipment** off before taking a bridge to conserve the bridger’s fuel. The isotopes used will be of the same type as the bridger's jump drive. The formula to calculate how much fuel is used is:

> <math> \rm Fuel\ usage = Mass \times \text{Portal Consumption Mass Factor} \times \text{Base cost} \times \text{Skill mod} \times \text{Distance in LY}</math>

| !Titan
!Black Ops |
| :--- |
| Base Cost |
| Portal Consumption Mass Factor |
| Skill Modifier |

 

For example, a Manticore jumping through a Black Ops bridge with :

> <math> 1\,470\,000\,\text{kg} \times 0.000000135 \times 700\,\text{isotopes} \times 0.5 \times 1\,\text{ly} = 69.4575\,\text{isotopes}</math>

A bridge can be activated if the host ship is in a warp disruption bubble, but ships inside the warp disruption bubble cannot take the bridge, only those outside a warp disruption bubble and who are not warp disrupted below a warp core strength of 0.

  1. # Conduit jump
Black ops battleships, carriers, supercarriers, and the Rorqual can conduit jump to their respective cyno. This both jumps them and eligible ships in a 10 km radius to the cyno. Unlike bridging, conduit jumping costs a flat amount of fuel no matter the size or mass of the affected ships - with the quantity of fuel consumed varying with the conduit ship's class - making conduit jumping a more efficient way of moving a smaller fleet around.

Black ops battleships and Rorquals have a fixed limit of 30 ships, limited to covert ops and dedicated mining ships respectively. A Rorqual can only conduit jump if its Industrial Core is inactive.

Meanwhile tech 1 carriers and supercarriers can take 5 to 30 eligible ships with them depending on the level of the  skill. Tech 2 command carriers have a further 100% bonus to their capacity, allowing them to take 10 to 60 eligible ships. Eligible ships are all combat sub-capital ships: **Corvette**, **Frigate**, **Destroyer**, **Cruiser**, **Battlecruiser**, and **Battleship** - including their faction, T2, and T3 counterparts. **Capsules** and **shuttles** are also permitted.

| -
! Ship Class
! Max Range (ly)
! Isotopes per ly
! Transportable Ship Types
!Bridge?
!Conduit? |
| :--- |
| Black Ops Battleship |
| Rorqual |
| Mining Destroyer |
| Mining Barge |
| Porpoise |
| Carrier
Command Carrier

Supercarrier |
| Shuttle |
| Corvette |
| Frigate |
| Destroyer |
| Cruiser |
| Battlecruiser |
| Battleship |
| Titan |

1. # Jump Fatigue and Jump Activation Cooldown
As of the October 2014 Phoebe release, traveling using a Jump Drive, Jump Portal, Jump Bridge, Covert Jump Drive or Covert Jump Portal causes fatigue to capsuleers and a delay is required between successive jumps. This delay is determined by the jump fatigue mechanic. Jump fatigue is presented as a time value, indicating the time it will take to decay to zero, and can accumulate to a maximum of 5 hours. It decays in real time, whether logged in or not. Jump fatigue is recalculated after every jump.

- Jump fatigue has a minimum value of 10 x (1 + (LY just traveled)) minutes
- Otherwise, the existing jump fatigue is multiplied by (1+(LY just traveled))
  - file:JumpFatigue.png**

During each jump (and before jump fatigue is recalculated) a Jump Activation cooldown also appears. While this is active, the ship cannot travel by jump drive, jump bridge or jump portal. 

- The Jump Activation cooldown has a minimum value of (1+(LY just jumped) in minutes
- Otherwise, the Jump Activation cooldown is one tenth of the pilot's Jump Fatigue value (before the jump fatigue is recalculated for this jump)
  - file:JumpActivationCooldown.png**

In practice this means that ships can typically jump around once per hour (more if jumps are shorter) without accumulating Jump Fatigue, but more frequent jumping will rapidly build fatigue. Jump freighters and other industrial ships will be able to maintain more frequent jumps.

- the Jump Activation cooldown is capped at 30 minutes
- Jump Fatigue is capped at 5 hours

For example, if a carrier wants to travel a long distance by making 5 ly jumps:
- Before the first jump, the pilot has Jump Activation (JA) cooldown of 0 minutes and Jump Fatigue (JF) of 0 minutes.
- After the first jump, the pilot has JA cooldown of 6 minutes and JF of 60 minutes.
- After waiting 6 minutes for the JA to decay, the pilot has JA cooldown of 0 minutes and JF of 54 minutes.
- After the second jump, the pilot has JA cooldown of 6 minutes and JF of 5 hours (the maximum).
- After waiting 6 minutes for the JA to decay, the pilot has JA cooldown of 0 minutes and JF of 4h 54m.
- After the third jump, the pilot has JA cooldown of 30 minutes (the maximum) and JF of 5 hours (the maximum).
- After waiting for 30 minutes for the JA to decay, the pilot has JA cooldown of 0 minutes and JF of 4h 30m.

These mechanics mean that ships can use their jump drives in quick succession twice, before going on a much longer delay before a third jump. This has huge implications for both defensive and offensive deployment of capital ships, and is a major factor in the so-called capital or supercapital "umbrella"s projected by larger lowsec and nullsec alliances: Any system within capital/supercapital jump drive range of an alliance's staging system can have capital ships jump drive in, and then a few minutes later jump drive out; but any system beyond one jump's range is essentially a one-way trip, as two jumps in quick succession are needed to reach the destination, and making a second jump forces a long delay before the third jump. The result is that any systems covered by the umbrella are extremely easily defended using capital/supercapital support (as a capital response fleet can jump in to rescue an ally, wait six minutes, and quickly jump back home and dock), while any ships beyond one jump's range are much more vulnerable to attack (as the 30-minute delay after the second jump means that any capitals which do make two jumps will be in space and vulnerable for a much longer span of time).

Two groups of ships have special considerations:

- **Black Ops Battleship**s and the covert cloaking ships they bridge gain a 75% reduction to effective distance jumped when calculating fatigue.

The following ships gain a 90% reduction to effective distance traveled when calculating fatigue:

- **Capsules**
- **Shuttles**
- **Haulers**
- **Blockade Runners**
- **Deep Space Transports**
- **Freighters**
- **Jump Freighters**
- **Capital Industrial Ships**
- Industrial Command Ships i.e. the **Porpoise** and **Orca**

1. # External links
- [Jump Activation and Jump Fatigue](https://support.eveonline.com/hc/en-us/articles/212726865-Jump-Activation-Cooldown-and-Jump-Fatigue)  (EVE Help Center)
- [Dev Blog Jump Fatigue Changes March 2018](https://www.eveonline.com/news/view/sovereignty-warfare-and-jump-fatigue-changes-coming-in-the-march-release)
- [Jump Fatigue and Jump Activation Cooldown calculator](https://fatigue.nakamura-labs.com/)

1. # Notes and references
