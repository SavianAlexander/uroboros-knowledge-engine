---
title: "Propulsion equipment"
url: "https://wiki.eveuniversity.org/Propulsion_equipment"
pageid: 1103
source: "EVE University Wiki"
categories: ["Fitting"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Propulsion equipment

- Propulsion modules** (sometimes just "**prop mods**") are a group of active **module**s which increase a ship's speed or otherwise make it more mobile, at the cost of **capacitor energy**. Greater mobility on the battlefield allows pilots to dictate the range at which combat takes place, optimizing the effectiveness of their weapons and/or reducing the effectiveness of enemy weapons, to flee from or catch opponents, and even directly to evade enemy weapons fire.

1. # Afterburner and microwarpdrive
Afterburners ("AB") and microwarpdrives ("MWD") are the most common propulsion modules, and appear in almost all ship fittings. These are active modules, which when activated consume capacitor energy to significantly increase a ship's top speed and acceleration, but also increase its mass, making it less maneuverable.

Afterburners boost a ship's maximum speed by around 130–200%, while microwarpdrives increase speed by around 500–700%. Compared with afterburners, then, microwarpdrives offer a much greater speed boost. However, they also use more capacitor energy, reduce the ship's total capacitor capacity when fitted, increase the ship's **signature radius** when active, can be shut down by **warp scramblers**, and are generally harder to fit.

Afterburners and microwarpdrives both have 10-second cycle times, and cannot be deactivated prematurely. However, the cycle time of afterburners can be reduced to a minimum of 7.5 seconds by training the skill . Capital ship-sized afterburners and microwarpdrives have 20-second cycle times instead. These modules do not have cooldowns, and can be left running continuously, provided capacitor energy is available.

The 500% signature radius bloom caused by an active microwarpdrive means that a ship using one will need to fly 500% faster than normal in order to retain the same ability to dodge enemy weapons fire . While the microwarpdrive's 500% speed increase may appear to cancel this out, this is deceptive. As a result of acceleration, turning, and orbiting, a ship with a microwarpdrive will very rarely be flying at speeds approaching the full 500% bonus the drive gives, while they will always be suffering the 500% signature penalty regardless of their speed. Consequently, while microwarpdrives are very good at allowing ships to control their engagement range (and either increase or decrease the distance between themselves and their enemies), they are not very effective at helping evade enemy weapons damage. Meanwhile, while afterburners are less effective at range control, their straight speed increase makes them very effective at helping ships to evade damage.

  - Faction** and deadspace afterburners have improved speed bonuses. Faction and deadspace microwarpdrives, however, offer only marginal speed increases over standard variants. Instead, faction microwarpdrives offer reduced capacitor and signature radius penalties, mitigating the module's issues with capacitor stability and evasion.

Certain Tech 2 and Tech 3 ships—**Interceptors**, **Interdictors**, **Assault Frigates**, **Command Destroyer**s, and Wake Limiter-fit **Strategic Cruisers**—suffer less from microwarpdrive signature penalties. These ships are able to take advantage of microwarpdrive speeds, and use them to evade enemy fire. Additionally, ships designed by **Sansha's Nation** have a unique bonus to afterburner speed, allowing them to achieve speeds comparable to those of microwarpdrives, but with none of the drive's penalties. 

  1. # Sizes and mass effects
There are different sizes of propulsion modules, intended for use on different sizes of ships.

| - style="background-color: var(--background-color-warning-subtle);"
! AB Size
! MWD Size
! Mass increase
! Actual Thrust
! Intended Use |
| :--- |
| 1MN |
| 10MN |
| 100MN |
| 10,000MN |

The max velocity bonus listed in module info is only one factor in the actual velocity increase. The maximum velocity of a ship using a propulsion module is

> <math>\displaystyle V_{\rm max} = V_{\rm base} \times \left( 1 + V_{\rm bonus}  \times \frac{ \text{Thrust} }{ \text{mass} } \right) </math>

In practice, that last thrust/mass term is almost equal to 1 when using properly sized modules on frigates, cruisers, and battleships, and for such hulls the ship's new maximum velocity is about equal to its base velocity multiplied by the bonus of the propulsion module.

However, certain exceptionally light-weight ships (like many **Triglavian** ships) can achieve higher speed bonuses, while heavier-weight ships such as destroyers and battlecruisers will receive lower speed bonuses than their prop modules would state. This formula explains how fitting armor plates reduces the bonus of a prop module (but not the ship's base speed). This formula also dictates that fitting a ship with an undersized afterburner or MWD will provide an ineffectively small boost. (In general, the only time this is ever done is in the act of fitting a battleship-sized 500MN microwarpdrive to a capital ship, as a sort of maneuvering thruster used in single cycles to improve alignment times.)

  1. # Tech and meta levels
Afterburners and microwarpdrives have very different attributes at different **tech and meta levels**. These attribute trends are consistent across all sizes of modules.

  1. ## Choosing afterburners
For afterburners, the pattern is fairly straightforward. Higher-tech afterburners grant larger speed bonuses. Faction and deadspace afterburners have lower capacitor costs, and come in two types: one consuming extra CPU (**Gallente**/**Serpentis**), one consuming extra powergrid (**Minmatar**/**Angel Cartel**). 

| - style="background-color:  var(--background-color-warning-subtle);"
! AB Type
! Meta Level
! Speed Increase
! Activation Cost
! Fitting Cost |
| :--- |
| Tech 1 |
| Monopropellant Enduring |
| Y-S8 Compact |
| Tech 2 |
| Analog Booster |
| Shadow Serpentis / Federation Navy |
| Domination / Republic Fleet |
| Coreli/Corelum/Core C-Type |
| Gistii/Gistum/Gist C-Type |
| Coreli/Corelum/Core B-Type |
| Gistii/Gistum/Gist B-Type |
| Coreli/Corelum/Core A-Type |
| Gistii/Gistum/Gist A-Type |
| Core X-Type |
| Gist X-Type |

(Note: capacitor and fitting cost adjustments are approximate, and will be slightly different at different sizes. X-Type modules only exist in 100MN and 500MN sizes.)

  1. ## Choosing microwarpdrives
For microwarpdrives, the story is more complex. Higher-tech MWDs grant only minimal speed improvements over lower-tech modules. Instead, higher-tech MWDs carry significantly reduced signature radius bloom effects and capacitor penalties.

However, there is an odd exception: the Tech 2 microwarpdrive carries a reduced capacitor penalty, but *not* a reduced signature bloom, only boosts speed by about 1% more than a meta module, and entails increased fitting and activation costs. As a result, Tech 2 MWDs are held in low esteem and should almost never be fitted.

Rather than Tech 2 variants, the three meta variants of MWDs are commonly deployed.
# The "Compact" variant is generally not ideal, but is easier to fit, and can sometimes be justified on that basis.
# The "Enduring" variant looks attractive, as it allows the drive to more easily remain active for long periods of time. In practice, though, the reduced activation cost from an "Enduring" MWD generally does less for a ship than the reduced max capacitor penalty from the "Quad LiF Restrained" variant.
# The "Quad LiF Restrained" MWD variant reduces the overall capacitor capacity penalty, and also blooms the signature radius less.
In short, for most fittings, the "Quad LiF" MWD type is generally preferred.

As with afterburners, faction and deadspace microwarpdrives come in two types: one consuming extra CPU but with reduced activation cost (Gallente/Serpentis), and one consuming extra powergrid  but with reduced signature radius bloom (Minmatar/Angel Cartel).

| - style="background-color:  var(--background-color-warning-subtle);"
! MWD Type
! Meta Level
! Speed Increase
! Activation Cost
! Fitting Cost
! Capacitor Penalty
! Signature Penalty |
| :--- |
| Tech 1 |
| Cold-Gas Enduring |
| Y-T8 Compact |
| Quad LiF Restrained |
| Tech 2 |
| Digital Booster |
| Shadow Serpentis / Federation Navy |
| Domination / Republic Fleet |
| Coreli/Corelum/Core C-Type |
| Gistii/Gistum/Gist C-Type |
| Coreli/Corelum/Core B-Type |
| Gistii/Gistum/Gist B-Type |
| Coreli/Corelum/Core A-Type |
| Gistii/Gistum/Gist A-Type |
| Core X-Type |
| Gist X-Type |

  1. # Oversized afterburner
It is possible to fit ships with oversized afterburners: 10MN on a frigate/destroyer, or 100MN on a cruiser/battlecruiser. The high fitting requirements and capacitor consumption of the larger AB usually makes this difficult. If this is being done, the full maximum velocity formula needs to be used to determine the ship's actual max speed.

Generally the resulting maximum velocity is close to typical microwarpdrive velocity—so a cruiser with a 100MN afterburner travels at something approaching cruiser MWD speed—but without the signature penalty or the vulnerability to warp scramblers. This makes oversized-afterburner ships extremely difficult to hit and damage, if they can achieve and maintain speed; it can also offer advantages in **ESS** space, where microwarpdrives cannot be used. Oversized afterburners synergize well with the bonuses to AB use found on some configurations of **Tech 3 strategic cruisers**, as well as on the **Succubus** and **Phantasm**

The drawback of an oversized AB is greatly increased ship mass, which makes accelerating and turning slower. In many cases, ships with oversized afterburners take up to 30 seconds of straight flight to reach 3/4 of their listed full speed, and a **Stabber** with a 100MN afterburner (for example) has a 30-second align time while the AB is running.

It is theoretically possible to also fit oversized microwarpdrives onto certain ships, but this is extremely difficult and extremely rare.

  1. # Dualprop fitting
A ship may only have one afterburner and/or microwarpdrive running at a time. However, it is possible, and commonly done on certain ships, to fit both an afterburner *and* a microwarpdrive onto one ship, to exploit both the evasive abilities of an AB and the range control of an MWD.

Such a "dualprop" fitting does mean sacrificing an extra mid slot for the second module, but can be worth it if, based on the ship's intended combat style, context, and targets, the afterburner evasion is desirable enough.

Such fits are sometimes described as "6MN", "60MN", or "600MN" (referring to the size of the two propulsion modules added together).

  1. # Overheating
Prop mods can be extremely impactful, but also extremely dangerous, modules to **overheat**. Overheating a prop mod increases its speed multiplier by 50% (multiplicatively), which means greatly improved top speed but more importantly greatly increased acceleration. This can often make the difference between catching a target and them escaping, or being caught versus making a quick change of direction to escape.

However, this power comes at a risk: prop mods generate more rack heat than any other modules, and microwarpdrives in particular have extremely severe head damage values. A 5MN MWD, for instance, can completely burn itself out in as few as *three* overheated cycles, severely damaging any tackle modules being run alongside it along the way. Very unusually though, the heat damage inflicted by prop mods vastly decreases at larger sizes, to the point that a 100MN afterburner can potentially be overheated for over a minute and a half before being in danger of burning out.

These overheat effects become especially noticeable on Combat **Interceptors**, which feature a bonus that increases the overheat speed multiplier to *100%*, and on ships using oversized afterburners, which will both benefit from the added acceleration, and be able to run their afterburners hot for exceedingly long times.

  1. # Related skills
The following skills directly effect afterburners and/or microwarpdrives.
- 5% Bonus to Afterburner and Microwarpdrive speed boost per skill level.
- 5% reduction to Afterburner duration and 10% reduction in Afterburner capacitor use per skill level.
- 10% reduction in afterburner capacitor needs per skill level.
- 5% reduction in MicroWarpdrive capacitor usage per skill level.

1. # Micro Jump Drive
The **Micro Jump Drive** ("MJD") is a propulsion module which, rather than making the ship move faster, teleports the ship forward 100km in the direction it is facing. Upon arrival, the ship maintains the direction and speed it had at the moment of MJD activation. Warp scramblers can be used to disrupt this module.

Micro jump drives can only be fitted on Tech 1 **battlecruisers** and **battleships**; their Tech 2 variants, **command Ships**, **marauders**, and **Black Ops Battleship**s; and **Deep Space Transports**. Marauders have a significantly reduced cooldown for this module.

Micro jump drives can be used offensively to close on a target, or defensively to jump out of a fight.

Micro jump drives are often used in combination with an afterburner or microwarpdrive, offering a secondary engagement or disengagement tool. Their long cooldown precludes their use as a primary mobility module, except when used by Marauders.

  1. # Micro Jump Drive operation
When a MJD is activated, the module spools up for 12 seconds (reduced to a minimum of 9 seconds by the skill ). During this time, the ship can not *voluntarily* change its direction, though it may unpredictably change course if it bumps into an immovable object. The signature radius of the ship is also increased by 150% during the spool-up time. A ship attempting to activate an MJD gains a visible orange-white rippling cone effect in front of it.

The jump is interrupted if the jumping ship is warp scrambled, **cloaked**, or has an active **Bastion Module**, at the moment when spool up time ends. Warp Core Stabilizers will not prevent the jump from being interrupted. Interdiction bubbles and warp *disruptors* have no effect on micro jump drives. Like other prop modules, the MJD cannot be deactivated before its cycle ends.

After the spool-up period the ship jumps 100 km to the direction it is facing. The ship retains its velocity and locked targets through the jump. Other ships will also retain locks on the ship that jumped.

After the jump has been completed (or aborted by scrambler) the MJD enters an 180-second cooldown period before it can be used again. Even if the jump fails, the module will still enter its cooldown period.

  1. # Micro Jump Field Generator
Micro Jump Field Generators ("MJFGs" or "booshes") are similar to Micro Jump Drives, but they let pilots move surrounding ships and objects with them. 

Only **Command Destroyer**s can fit Micro Jump Field Generators; they are sometimes nicknamed "Jump Destroyers" or "booshers" for this reason. MJFGs have the following mechanics:

- A Micro Jump Field Generator moves not only the ship itself but also most objects which are within 6 km of the boosher. Up to 25 ships will be carried along.
  - **Drones**, **fighters**, **bombs**, and **Warp Disrupt Probes** will also be moved, and will not count towards the 25-ship limit.
  - **Capital ships**, (**Jump**), **Freighters**, **Industrial Command Ships**, and deployables will *not* be moved.
- **Warp scramblers** prevent the boosher or its targets from being jumped.
  - Any target that is scrammed will not be jumped
  - If the boosher ship itself is scrammed, the MFJG will fail, and nobody will be jumped, much like a MJD.
  - This can be used defensively by fleet members scramming each other to prevent separation, or scramming the boosher to prevent drive activation.
  - The boosher can also scram a target and then boosh itself and everything *else* away from that target; the scrammed ship won't be booshed and will be left isolated.
- Ships which are in an invulnerable state can't be booshed. Some example states are the undock timer, gate cloak, tether, and the short invulnerability time enjoyed by a ship which has just dropped out of warp.
- MJFGs cannot be used in **Highsec**.
- Activating a MJFG gives the user a **16px|link=** **weapon timer** for 60 seconds (meaning you cannot take a gate or dock after using one). In lowsec, the boosher's **safety settings** need to be red, booshing can give a **16px|link=** **criminal timer**. (Compare to ECM burst and smartbombs. However, it is not known what circumstances would give a criminal timer.)
  - For this reason, **logistics** pilots should also set their safeties to red if a boosher is in a lowsec fleet.
- The spool-up time is a bit shorter (9 seconds before skills) and is reduced by the skills  and  down to a minimum of 6 seconds (5.06s, rounded up by the server tick).
- Objects can only be affected by one boosh in a single server tick (second). However, multiple booshes over consecutive ticks will still take effect.
- While spooling, the Command Destroyer cannot *voluntarily* change direction or speed, and a blue ring of light with a glowing spark in the middle appears in front of it. (However, if the Command Destroyer bumps into a large enough object to change its course, that will affect the direction the jump fires in.)

Micro Jump Field Generators open up many interesting tactics:
- You can use them to split up hostile fleets and isolate targets.
- You can use the MJFG as an escape tool for fleets.
- With multiple command destroyers, you can chain booshers and make slow sniper fleets move around the grid quickly, allowing them to "kite" enemies that would otherwise catch up with them.
- You can suddenly get on top of a target to tackle it: remember that you can boosh a warp disrupt probe.

  1. # Mobile Micro Jump Unit
Mobile Micro Jump Units may be deployed in space, with modest restrictions on proximity to stargates, stations, starbases or Upwell structures. They allow all nearby ships (within 2.5 km) to jump themselves 100 km away in whatever direction they are facing, by right-clicking the Unit and selecting *Jump*. Jumping using a Mobile Micro unit has a 12-second spool-up, not reduced by skills, and produces the same orange-white rippling cone visual as using a Micro Jump Drive.

The unit occupies 50 cargo space, takes one minute to deploy, cannot be picked up once deployed, and lasts for two days if not destroyed.  For ships up to 1 million tonnes (including the **Rorqual**), it can provide a brief window of escape to jump 100km and then try to warp away if under attack.

The Mobile Micro Jump Unit is the only source of micro-jumping available to **Alpha clones**.

  1. # Related skills
- is required to use any micro jump drives and reduces the spool up time duration by 5% per skill level.
- is required to use the Mobile Micro Jump Unit.
