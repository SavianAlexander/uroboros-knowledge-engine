---
title: "Passive shield tanking"
url: "https://wiki.eveuniversity.org/Passive_shield_tanking"
pageid: 6805
source: "EVE University Wiki"
categories: ["Candidates for merging", "Fitting", "Fittings"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Passive shield tanking

- Passive shield tanking** (often shortened to simply *passive tanking*) is a method of tanking that relies on the ability of shields to recharge without the need for active modules. Instead, passive shield tanks rely on modules that increase this recharge rate, as well as the absolute amount of shield hit points a ship has.

The goal of a passive shield tank is enable a ship's shield to regenerate as quickly as it takes damage. Passive shield tanks work best in situations where damage is either fairly constant, or slowly increasing over a long period of time. It can also work in situations where the pilot is able to remove the ship from combat periodically to let their shields recharge. As such, passive shield tanking is most appropriate for use in PvE situations, where incoming damage is fairly predictable.

In particular, passive shield tanks can be effective on ships built for kiting or long-range combat tactics, both of which keep shield damage relatively low. As above, it can also be used when employing hit-and-run tactics as well.

1. # Shield recharge rate

The shield regeneration rate increases by more than double as the shield takes damage. Since this change is a percentage, a ship that starts with a higher average regeneration rate will get a bigger boost in its optimum rate. In addition, since the shield regeneration *time* is constant, a larger shield will regenerate more hit points per second. 

For example, these are all Caldari ships. Many Caldari ships prefer shield tanks.

| Ship Type
! scope="col" style="width: 9em" | Shield Capacity (hp)
! scope="col" style="width: 9em;" | Shield Regeneration Time (sec)
! scope="col" style="width: 9em;" | Average Regeneration Rate (C/T) |
| :--- |
|  (frigate) |
|  (destroyer) |
|  (cruiser) |
|  (battlecruiser) |
|  (battleship) |

	

Without any modules, and assuming the pilots had the same skills, the  would rebuild its shield almost three times faster than the Kestrel. The Raven would rebuild about twice as fast as the Corax, but slower than the Drake. All other things being equal, the Drake, with its large shield capacity and very fast recharge time, would make the best candidate for a passive shield tank.

These cruisers and battlecruisers provide a representative sample comparison of ships by faction.

| Faction
! scope="col" | Ship Type
! scope="col" style="width: 9em;" | Shield Capacity (hp)
! scope="col" style="width: 9em;" | Shield Regeneration Time (sec)
! scope="col" style="width: 9em;" | Average Regeneration Rate (C/T) |
| :--- |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |

	

The Caldari and Minmatar tend to have the larger shield capacities and higher shield recharge rates. Thus it is not surprising that ships of these factions are more likely to be shield tanked.

1. # Combat situations
Because a passive tank depends on the shield's recharging, it works best in situations where the damage is constant or builds slowly over time. It works least well in situation where the shield will take a large amount of damage in a very short time. Passive tanking can be used, then in situations where the pilot can "kite" the enemies to control how much damage comes in – or in situations where the pilot is using long range weapons and depending on speed to keep away from enemy fire.

In fleet situations the assigned combat role may be a factor. If the ship is to be tackling other ships, for example, its mid power slots may be needed for e-war modules, and it may be exposed to high, brief peaks of damage - so an armor tank will likely be preferable.

1. # Modules and rigs
The following influence the passive shield tank.

| Unit
! scope="col" | Slot
! scope="col" | Capacitor Drain
! scope="col" | Effect
! scope="col" | Notes |
| :--- |
| wheat|Shield Extender}} |
| wheat|Power Diagnostic System}} |
| wheat|Shield Power Relay}} |
| wheat|Shield Flux Coil}} |
| wheat|Shield Recharger}} |
| wheat|Damage Control}} |
| wheat|Shield Resistance Amplifier}} |
| wheat|Shield Hardener}} |
| wheat|Core Defense Field Purger}} |
| wheat|Core Defense Field Extender}} |
| wheat|Shield Reinforcer}} |

	

  1. # Initial fit
The usual starting point is to try to fill several low slots with Shield Power Relay modules, several mid slots with Shield Extender modules, and to fit all three rig slots with Defense Field Purger rigs. Of course, this will need to be modified to fit slot availability, resists and other considerations, but it is a good place to start.

With that in mind, although Shield Power Relays reduce capacitor recharge rate, they have no stacking penalties, and they are the most powerful modules in terms of increasing shield regeneration.

Shield Extenders increase the capacity of the shield and, because recharge *time* is a constant, this in turn increases the recharge rate. These modules have a Signature Radius penalty associated with them, and they impact the power grid, but they have no stacking penalties, and their benefits outweigh these costs. In addition, it is often possible to "upsize" Shield Extenders&mdash;putting Large Shield Extenders on a Cruiser, or Medium Extenders on a Frigate, for example. This increased buffer will allow the ship to survive for longer even if incoming DPS is higher than the recharge.

Finally, Defense Field Purger rigs are almost always more effective than Defense Field Extender rigs in a passive shield fit. The Extender increases shield capacity (thereby increasing its relative recharge rate), but the Purger directly decreases total shield recharge time by enough to make a difference (albeit having a larger penalty to Signature Radius).

  1. # Possible alterations
- Most ships have "damage holes", a type of damage from which they are not well defended. A specific damage type shield hardener may need to be equipped to cover such holes. Hardener modules for other types of damage may be added to account for the primary damage types expected in the encounter. Keep in mind the stacking penalties that arise if a second hardener module is used to alter the same type of damage.
- If the pilot's skills are not sufficient to install T2 modules, substitutions may be in order. You will have to experiment with T1 modules ... or you may find it better to just wait until your skills improve.
- Once your tanking modules are set, check to see if your ship's capacitor is stable. If it isn't, and the amount is significant, consider swapping one or two Shield Power Relays for Shield Flux Coils. If you have to swap more than two Shield Relays for Flux Coils, consider putting back all but one of the Shield Power Relays and adding a Capacitor Power Relay.

  1. # Example

Consider the **Hurricane**, a Minmatar Battlecruiser. 
- Base shield capacity: 4250 hp
- Base recharge time: 1400 sec
- Average regeneration rate = 4250 / 1400 = 3.0 hp/s
- Base peak regen rate = 2.5 &times; 3.0 = 7.5 hp/s

- Note that the Hurricane's shields are weakest for EM, followed by Thermal, damage.

Why put a passive tank on a Hurricane? As an L3 Security Mission runner:
- It has good shield capacity and a high recharge rate
- It has six low slots – 3 for Shield Power Relays and 3 for offensive modules
- For mission running the mid slots can be dedicated to propulsion and shields
- Bonuses to medium projectile turrets and six turret hardpoints support artillery for PvE
- Increases in signature radius matter less in PvE

  1. # Shield Power Relays

Shield power relays increase the recharge time directly. They have no stacking penalty, but they do reduce the recharge rate of the capacitor. 

- Shield Power Relay II
- Recharge time bonus: -24%
- No shield support skills
- (*Penalty: Capacitor Recharge Rate -35%*)

The first module reduces the Recharge Time by 24%, from 1400 sec to 1400 - 336 = 1064 sec
This gives a new Average Recharge Rate of 4250/1064 = 4.0 hp/sec
And a new Peak Recharge Rate of 2.5 x 4.0 = 10.0 hp/s

Repeating the calculation:

| Modules
! scope="col" style="text-align: center;" | 1
! scope="col" style="text-align: center;" | 2
! scope="col" style="text-align: center;" | 3
! scope="col" style="text-align: center;" | 4
! scope="col" style="text-align: center;" | 5
! scope="col" style="text-align: center;" | 6 |
| :--- |
| Recharge Time |
| Peak Regeneration Rate (rounded) |

	

While this illustrates the power of the module, fitting six of them to a ship would be unrealistic. Three modules is a common fit, with the other slots used for other purposes. Thus, with no other skills or fittings, three Shield Power Relays would increase the *Peak* Recharge Rate to 17.3 hitpoints per second. 

For comparison, a medium Phased Plasma projectile does about 18 hp base shield damage plus 24 hp type damage; a medium Lead Hybrid charge does about 10 hp base shield damage plus 16 hp type damage.

  1. # Shield Extenders

Shield extenders add hitpoints to the Capacity of the shield. The do not have stacking penalties, but they do increase the Signature Radius of the ship.

- Large Shield Extender II
- Shield Capacity Bonus: 2600 hp
- No shield support skills
- (*Penalty: Signature Radius 25 m*)

 Base recharge time: 1400 sec
 Shield Capacity: 4250 + 2600 = 6850 hp
 Average regeneration Rate = 6850 / 1400 =  4.9 hp/s
 Peak Recharge Rate = 2.5 x 4.9 = 12.3 hp/s

The original base Peak Recharge Rate was 7.6 hp/s. So adding a large shield extender increases the recharge rate by 4.7 hp/s; an increase of 62%.

  1. # Core Defense Purger rigs

These rigs produce a percentage increase in Shield Recharge Rate. They have no stacking penalty, but they do increase the Signature Radius of the ship.

- Medium Core Defense Field Purger I
- Recharge Rate Bonus: -20%
- No shield support skills
- (*Penalty: Signature Radius 10%*)

Since these are usually the last items to be fitted, this example will build on a fit that includes one Large Shield Extender II and three Power Shield Relay IIs.

The bare ship had:
- Base shield capacity: 4250 hp
- Base recharge time: 1400 sec
- Average regeneration rate = 4250 / 1400 = 3.0 hp/s
- Base peak regeneration rate = 2.5 x 3.1 = 7.6 hp/s

After one Large Shield Extender II (see above): 
- Shield capacity:

Three Power Shield Relay II (see above):
- Modules reduce recharge time @ -24%
- Shield capacity: 6850 hp
- Peak Recharge Rate = Shield Capacity/Recharge Time x 2.5

| Modules | 1 | 2 | 3 |
| :--- | :--- | :--- | :--- |
| Recharge Time | 1064 | 808.6 | Green|614.3}} |
| Peak Regeneration Rate | 16.1 | 21.2 | 27.9 |

The Core Defense Purger Rigs impact on Recharge Rate in the same way that the Power Shield Relays do ... by reducing the Recharge Time by a percentage.

Three Core Defense Purger Rigs:
- Rigs reduce recharge time @ -20%
- Shield capacity:  hp
- Starting Recharge Time:  sec
- Peak Recharge Rate = Shield Capacity/Recharge Time x 2.5

| Rigs | 1 | 2 | 3 |
| :--- | :--- | :--- | :--- |
| Recharge Time | 491.4 | 393.1 | 314.4 |
| Peak Regeneration Rate | 34.8 | 43.6 | 54.4 |

	

So with this fit in place, an no pilot shield skills, the Peak Shield Regeneration Rate will be 54.4 hp/sec.

1. # Skills
> *5% bonus to shield capacity per skill level*

> *5% reduction in shield recharge time per skill level*

Any pilot considering a passive shield tank would want to train these to at least Level IV. At that level, their effect would be considerable.

  - Shield Management @ Level IV**
- 20% increase in Shield Capacity

This would increase the Base Shield Capacity to: 4250 + 0.20 x 4250 = 5100 hitpoints

- It would also increase the benefit of the Large Shield Extender II by 20%: 2600 + 0.20 x 2600 = 3120*

Making the total shield capacity: 5100 + 3120 =  hitpoints

  - Shield Operation @ Level IV**
- 20% decrease in Shield Recharge Time

This would decrease the Base Shield Recharge Time: 1400 - 1400 x 0.20 = 1120

And that value would be used in the three Shield Relay computations followed by the 3 Core Purger Rig computations

- Relay @ -24%

> 851.2, 646.9, 491.6

- Purger @ -20%
> 393.2, 314.5, 251.6

giving a final Recharge Time of:  seconds

These two values compute the final Peak Recharge Rate.

 Recharge Time: 251.6 sec
 Average Recharge Time = 8220/251.6 = 32.7
 Peak Recharge Rate:  32.7 x 2.5 = 81.7 hp/sec

1. # Final fit
Thus, a Minmatar Hurricane fitted for this particular skilled, passive tank would have a Peak Shield Regeneration rate of approximately 82 hp/sec. Again, for comparison, a medium Phased Plasma projectile does about 18 hp base shield damage plus 24 hp type damage; a medium Lead Hybrid charge does about 10 hp base shield damage plus 16 hp type damage.
A complete fit might look like this:

- This is a highly skilled fitting. Weapons and modules can be scaled back to meet pilot skills. Watch dps and shield recharge rate and try to balance the decline.
- The mid slot hardeners should be swapped to match the damage type appropriate to the enemies the pilot expects to encounter.
- With one shield hardener running, the **capacitor is stable**. A second hardener will run the capacitor down in about fifteen minutes. Since this fit is intended for L2/L3 Security Missions, that should not be a problem. If it becomes a concern, consider replacing one of the low slot gyrostabilizers with a Capacitor Flux Coil.
- Low slot modules can be replaced by Auxiliary Power Controls, Capacitor Flux Coils, and/or Power Diagnostic Systems as needed.
