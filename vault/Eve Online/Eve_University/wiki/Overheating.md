---
title: "Overheating"
url: "https://wiki.eveuniversity.org/Overheating"
pageid: 490
source: "EVE University Wiki"
categories: ["Game mechanics", "Ships", "Weapons"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Overheating

- Overheating** (or **overloading**) is an important ship combat mechanic in EVE Online. Most active modules can be overheated, and overheating a module wrings better performance from it, at the cost of gradually-accumulating heat damage to the module.

Incautious overheating can burn a module out completely, making it useless until it is repaired. However, if used with care or in an emergency, the benefit gained from an overheated module could be the difference between losing your ship and killing your enemy. Good pilots know when the risk is worth the possible reward.

The timing of overheating and the management of the resulting heat damage are important parts of small-gang and solo PvP combat. Overheating remains useful in most larger PvP fleets. It has some niche uses in PvE combat.

1. # Controls

You can begin overheating a specific module by -clicking it or clicking the green light at the top of the module button. You can turn it off the same way. Alternatively you can right click the module and choose to overheat it. You can also use a keyboard shortcut: by default,  +  overheats the module controlled by the  key, though this can be changed in the shortcuts options.

A module that's already active and receives an overheat command won't begin overheating until it starts its next cycle. A module that's already overheating that's commanded to stop won't cease overheating until the end of its current cycle. The green light at the top of the module button will flash when overheating is off but about to turn on at the next cycle change, or is on and about to turn off at the next cycle change.

You can also "pre-heat" a module, by turning overheating on while the module isn't running. This ensures that it begins its first cycle overheated. A module primed to overheat will stay primed after warping, but not after jumping or docking.

Not all modules can be overheated. For example, neither cloaks nor command bursts can be overheated, and no passive modules can be overheated.

In some circumstances, you may need to overheat many modules as fast as possible. You can choose to overheat an entire rack (all the high slots, all the mid slots, or all the low slots) via the small buttons to the left of each rack.

In the right-click menu available on the capacitor circle itself, there is an option called "Lock Module Overheat State". When enabled, this blocks all overheating changes on all modules: modules which aren't overheating can't be heated, and modules which are already overheating can't have their heat turned off. This can be used to prevent accidental overheating, although it is a very inflexible tool.

1. # Benefits and uses

Any overheated module increases its performance in some way.

  1. # Key uses

A complete table of heat bonuses follows below, but some of the most important effects to know are:

- Heating a ****propulsion module**** provides an additional 50% speed bonus. Since speed and positioning are key to many kinds of PvP combat and to some kinds of PvE combat, this can prove crucial.
- Heating ****tackle modules**** boosts their range.
  - It is often worth pre-heating your point/scram/web when in warp towards an engagement, especially if you are likely to be the initial tackle, as greater tackling range at the beginning of a fight can make the difference between catching or losing a target.
  - Similarly, it is also often worth overheating tackle at the end of a fight, if your targets are trying to leave.
- Heating ****tank modules**** increases their effect.
  - Shield boosters and armour repairers gain both increased repair per cycle, *and* faster cycle times. This makes them some of the most powerful modules to overheat. Note that the faster cycle means a heaver capacitor burden.
  - Ancillary shield boosters and armour repairers should *always* be used overheated, as they have a limited number of effective cycles (meaning that you want to make the most of every cycle, and there is only minimal damage they can inflict).
  - Active resistance hardeners can be overheated to increase the damage resistance they provide. This means that overheating can also benefit some types of buffer tanks and passive shield tanks.
  - *Remote* shield boosters and armor repairers gain reduced cycle times. For remote armor repairers, this reduces the delay before the first cycle lands; for remote shield boosters, this reduces the delay between the first and second cycles.
- Heating **all **turrets** and **missile launchers**** increases their potential DPS, but not always in the same way.
  - Short-ranged turrets (pulse lasers, blasters, autocannon, disintegrators) get a bonus to their raw damage-per-shot.
  - Long-ranged turrets (beam lasers, railguns, artillery, vorton projectors) get a bonus to their rate of fire. Note that an increased rate of fire also means an increased capacitor burden from beam lasers and railguns.
  - All kinds of missile launcher get a bonus to rate of fire.

At its simplest, overheating is a tool for high-stakes moments in combat, and a pilot in serious danger of losing their ship in either PvP or PvE is almost never wrong to overheat relevant modules. Some of the effects noted here, though, such as the tackle module range bonuses, are slightly subtler, and experienced pilots develop a sense of when to use them.

  1. # All heat benefits

| Module Type | Overheat Effect | Percent Bonus |
| :--- | :--- | :--- |
| AfterburnerMicrowarpdrive | Speed Bonus | 50% |
| Warp DisruptorWarp Scrambler | Range Bonus | 20% |
| Stasis Webifier | Range Bonus | 30% |
| Stasis Grappler | Optimal Range Bonus | 300% |
| ECM JammerBurst JammerTracking DisruptorGuidance DisruptorRemote Sensor DampenerTarget Painter | Strength Bonus | 20% |
| Energy NeutralizerEnergy Nosferatu | Duration Bonus | -15% |
| Armor HardenerShield Hardener | Strength Bonus | 20% |
| Armor Repairer | Duration BonusStrength Bonus | -15%10% |
| Shield Booster | Duration BonusStrength Bonus | -15%10% |
| Hull Repairer | Duration Bonus | -15% |
| Remote Armor RepairerRemote Shield BoosterRemote Cap Transmitter | Duration Bonus | -15% |
| Remote Sensor BoosterRemote Tracking Computer | Strength Bonus | 15% |
| Short Range Turrets | Damage Bonus | 15% |
| Long Range Turrets | Duration Bonus | -15% |
| Missile Launchers | Duration Bonus | -15% |
| Tracking ComputerGuidance ComputerOmnidirectional Tracking LinkSensor Booster | Strength Bonus | 15% |
| Cap Booster | Duration Bonus | -20% |

1. # Heat damage

The downside of overheating is **heat damage**. Heat damage is *not* related to normal damage: overheating does not cause damage to your shield, armour, or hull hit points. Heat damage has no link to the Thermal damage type.

Rather, heat damage is dealt to the hitpoints of individual modules. If you "show info" on a module, and check its "Attributes" tab, you will see it has "Structure Hitpoints". Most modules have 40 hitpoints. Heat damage is dealt to these hitpoints.

The amount of heat damage on a module is visible as a red fringe that creeps around the circular module icon counterclockwise, from the 12 o'clock position. When a group of weapons are represented by one button, the heat damage indication on the button shows the state of the most damaged module in the group, not an average across the group.

Having some heat damage does not affect modules' functions or power in any way. However, when a module has lost all of its hitpoints—when the red fringe has completely circled the module icon and reached 12 o'clock again—the module will stop working and go offline (players often call this "burning out"). Note that if any single one of a grouped set of turrets or missile launchers burns completely out, the button for the whole group will become useless; it will be possible to continue using the other weapons, but only by ungrouping them (and if necessary regrouping them without including the burned-out module).

  1. # Damage mechanics

The mathematics of heat damage is discussed in a later section for those interested. What all pilots should know about the mechanics heat damage is as follows.

Heat damage is not dealt reliably and automatically by every heated module cycle. Instead, it is dealt through a chance-based mechanic. Each heated cycle of any module always raises the *heat level* of the module's rack, by a reliably predictable amount: a heated cycle from a high slot module increases the high slot rack heat level, a heated cycle from a mid slot module heats up the mid slot rack, and so on. The following factors affect rack heat generation:

- Having more modules running overheated in the same rack generates more rack heat.
- Larger ships generate rack heat more slowly than smaller ships.
- Propulsion modules generate a lot of rack heat.
- Most T2 non-propulsion modules generate quite a lot of rack heat.
- All T1 non-propulsion modules and a few T2 modules generate a little heat.
- Faster-cycling modules tend to generate less heat per cycle.

Each heated cycle of any module has a *chance* to deal heat damage to the heated module, or to other modules in the rack. The chance of heat damage at the end of a cycle increases with the level of rack heat; how hot a high, medium, or low rack is affects how much of a chance of heat damage there is. The increase in the chance of heat damage caused by higher rack heat is not a steady, linear increase: high levels of rack heat generate a *much* higher chance of heat damage than low levels of rack heat. Rack heat is displayed in the three dials directly above the circle of the capacitor indicator. The leftmost dial displays low slot heat, the middle dial displays mid slot heat, and the rightmost dial displays high slot heat.

Heat damage chances are also affected by proximity in the rack. A module is most likely to deal heat damage to itself; then to modules adjacent to it, then to other modules in the rack with the chance of heat damage decreasing with greater distance in the rack.

Rack heat dissipates when modules in a rack are not being overheated. Heat dissipates quickly when the rack is very hot, and slowly when the rack is relatively cool. Pilots should note that when a ship is docked up, heat in its racks does *not* instantly disappear. It continues to dissipate at the normal rate. As a result, if a ship is docked to repair heat damage and immediately undocked, its racks may still have heat left in them even if its modules have been repaired.

  1. # Preventing heat damage

It is possible to overheat intelligently, in ways that limit the amount of heat damage caused.

In judging the risk of heat damage, **rack heat is more important than the extent of damage already sustained**, and **the rack heat indicators can matter more than heat damage on a module button**. If a rack is completely cool, it is usually safe to overheat for a cycle or two even with quite damaged modules: sometimes modules take no damage at all from a single cycle of heat when the rack starts out entirely cool. If, by contrast, a rack is very hot, it is quite risky to overheat even a module with little heat damage, as at high rack heat levels, damage will stack up very quickly.

Since the proximity of modules to each other affects their risk of heat damage, **spreading out and separating active modules in a rack can mitigate heat damage**. By placing the active modules in a rack as far away from each other as possible, the heat damage from each module can be spread out rather than concentrating on particular parts of the rack. Passive modules or less-important active modules can be placed in the slots between. Furthermore, contrary to popular belief, heat damage does **not** "wrap around" the ends of racks.

In the high slots of a combat ship, it is common to spread out the main weapon system modules as much as possible, putting secondary weapons, utility tools such as energy neutralizers, or **command burst modules** between the often-heated weapons. It is still possible to group the guns or launchers as normal. Pilots can move the module buttons around in space to keep them assigned to sensible keys in a logical arrangement, while retaining the "true" arrangement of modules in the fitting itself.

Offline modules and empty module slots are especially effective, **and equally effective**, at reducing heat damage.

Players sometimes call these fitting practices "heatsinking", since the passive or less-commonly-used active modules placed between high-heat modules act as heat sinks. This idiom has no relation to the Heat Sink module, a low slot DPS-enhancing module for energy weapons; the Heat Sink module and its variations are no more effective as *actual* heat sinks than any other module.

  1. # Repairing heat damage

  1. ## Nanite Repair Paste

An item called "Nanite Repair Paste" can be used to repair heat damage while in space. To do this, make sure you have some paste in your cargo hold, and then right-click on the damaged module button, and select "repair". Paste repairs take some time, enough time that they are generally applied between fights rather than during fights. Hovering over the repairing module's button will bring up a tooltip displaying the remaining repair time.

Repairs can be cancelled (right-click the module button and select the option to do this) and are cancelled automatically if your ship jumps through a gate, filaments, or travels via a jump to a cyno. The amount of repair carried out before cancellation will remain, and only the equivalent amount of paste will be used up. Paste cannot be used to repair a module which is fully burned out.

A module cannot be used while it is being repaired. No module can be overheated while any other module is being repaired using paste. It *is*, however, possible to repair a module's heat damage while it is reloading charges. This can be useful with modules with very long reload times, such as Rapid Light Missile Launchers and ancillary shield boosters / armour repairers.

  1. ## Tether

When tethered on a friendly **Upwell structure**, heat damage to a ship's modules is slowly repaired, for free. Tethering can repair burned-out modules.

  1. ## Docked repairs

Heat damage can also be repaired, instantly, when docked up. In NPC stations this comes with a cost; in player-owned structures owned by friendly players and with appropriate settings, it can be done for free. Repairs while docked will repair fully burned-out modules too.

Pilots should (again) note that docking up does not instantly clear rack heat itself. A ship can be docked and have its heat damage quickly repaired, but if it is immediately undocked its racks might still be hot. This will not cause more damage by itself, but must be borne in mind if the ship is about to overheat its modules again straight away.

1. # Overheating bonuses

  1. # Skills

The skill that lets pilots overheat is . Thermodynamics reduces the heat damage caused by overheating by 5% per skill level, for a 25% reduction at level V. This is a starting skill for characters created between September 2015 and September 2019. Older and newer characters must train the requisites and this skill on their own.

There are also two skills which make paste repairs more efficient:

- - provides a 5% reduction in Nanite Repair Paste consumption per level.
- - provides a 20% increase in damaged module repair amount per second.

  1. # Bonused ships

  - Tactical Destroyers** and **Strategic Cruisers** have bonuses improving their ability to overheat, allowing them to sustain overheats for longer. These bonuses are tied to the skills required to fly them:

- (Racial) Tactical Destroyer - Provides 5% reduction to heat damage from overheating per level.
- (Racial) Strategic Cruiser - Provides 5% reduction to heat damage from overheating, and 10% increase in damaged module repair amount per second, per level.
- (Racial) Core Systems - Provides 5% reduction to heat damage from overheating per level when the associated electronic warfare subsystem is fitted.

A Tactical Destroyer or Strategic Cruiser flown by a pilot with Thermodynamics V and the appropriate Tactical Destroyer or Strategic Cruiser skill at V, will sustain 44.75% reduced damage from overheating. A Strategic Cruiser fitted with the electronic warfare Core subsystem and flown by a pilot with Thermodynamics V, and the appropriate Strategic Cruiser and Core Systems skills at V, will sustain 57.8% reduced damage from overheating.

  - Combat Interceptors** and **Deep Space Transports** have flat role bonuses that double the benefit of overheating certain modules:

- Combat Interceptors - Provides 100% bonus to the benefits of overheating Afterburners and Microwarpdrives.
- Deep Space Transports - Provides 100% bonus to the benefits of overheating Afterburners, Microwarpdrives, Local Repair Modules, and Resistance Modules.

  1. # Red Giant wormholes

Wormhole space systems with the **Red Giant effect** increase both the risk and the reward associated with overheating. Every Red Giant wormhole increases heat damage by a percentage, and increases the bonuses gained from overheating by twice that percentage.

| 
! Effects
! Class 1
! Class 2
! Class 3
! Class 4
! Class 5
! Class 6 |
| :--- |

1. # Heat mathematics

  1. # Rack heat

The following tables specify how exactly module type and hull size affect heat generation.

| Module Type | Rack Heat Generation/second |
| :--- | :--- |
| Afterburner, Microwarpdrive | 4% |
| Most T2 modules | 2% |
| All other non-T2 Modules | 1% |

| Hull Size | Rack Heat Generation Rate |
| :--- | :--- |
| Frigate, Interdictor, Command Destroyer | 100% |
| Destroyer, Tactical Destroyer | 85% |
| Cruiser, Industrial, Mining Barge | 75% |
| Battlecruiser | 65% |
| Battleship | 50% |
| Carrier, Force Auxiliary | 40% |
| Dreadnought, Supercarrier, Orca, Rorqual | 35% |
| Titan | 25% |

The values from these tables cannot be found in-game. They must be found on outside sources. Module heat generation rates can be found on modules, under the attribute <code>heatAbsorbtionRateModifier</code>, and hull heat generation modifiers can be found on ship hulls, under the attribute <code>heatGenerationModifier</code>.

The time required for a rack to reach a certain heat level (starting from **0%** rack heat) with a given set of overheated modules can be calculated with the following formula:
H(t)=(heatCapacity/100)-e^(-t*heatGenerationMultiplier*sum(heatAbsorbtionRateModifier))
> <math>\displaystyle \text{H(t)}= 1 - e ^ \left( \text{-t} \cdot \text{heatGenerationMultiplier} \cdot \text{sum} \left( \text{heatAbsorbtionRateModifier} \right) \right)</math>
or, rearranged,
> <math>\displaystyle \text{t} = \frac{-\ln{\left(1 - H(t) \right)}}{\text{heatGenerationMultiplier} \cdot \text{sum} \left( \text{heatAbsorbtionRateModifier} \right)} </math>
where
- H(t) is the target heat level, as a decimal (for example, 90% = 0.9)
- t is the time in seconds
- heatGenerationMultiplier is the "Rack Heat Generation Rate" from the above table based on hull size
- sum(heatAbsorbtionRateModifier) is the sum of the "Rack Heat Generation/Second" (as a decimal) of all currently overheated modules in the rack

So for example, if a frigate overheating a Warp Scrambler I, it would take:
> <math>\displaystyle \text{t} = \frac{-\ln{\left(1 - 0.5 \right)}}{1 \cdot \text{sum} \left( 0.01 \right)} = \frac{-\ln{0.5}}{0.01} = \frac{0.693}{0.01} = 69.3  </math>
69.3 seconds to reach 50% rack heat, and
> <math>\displaystyle \text{t} = \frac{-\ln{\left(1 - 0.9 \right)}}{1 \cdot \text{sum} \left( 0.01 \right)} = \frac{-\ln{0.1}}{0.01} = \frac{2.303}{0.01} = 230.3 </math>
230.3 seconds to reach 90% rack heat

Meanwhile, if a **Catalyst**, with 8 Light Neutron Blaster IIs, was overheating its full gun rack, it would take:
> <math>\displaystyle \text{t} = \frac{-\ln{\left(1 - 0.5 \right)}}{.85 \cdot \text{sum} \left( 0.02 \cdot 8 \right)} = \frac{-\ln{0.5}}{0.85 \cdot 0.16} = \frac{0.693}{0.136} = 5.1 </math>
5.1 seconds to reach 50% rack heat, and
> <math>\displaystyle \text{t} = \frac{-\ln{\left(1 - 0.9 \right)}}{.85 \cdot \text{sum} \left( 0.02 \cdot 8 \right)} = \frac{-\ln{0.1}}{0.85 \cdot 0.16} = \frac{2.303}{0.136} = 16.9 </math>
16.9 seconds to reach 90% rack heat

This illustrates the speed at which large gun racks heat up and burn out, versus the much slower rate at which individual E-War or local repair modules will heat and burn.

The time required to increase rack heat from a given level to a target level is found by calculating the time required to reach the higher level, and subtracting the time required to reach the lower level. So, for that frigate to increase from 50% rack heat to 90% rack heat, it would take (230.3 - 69.3) = 161 seconds.

The logarithmic nature of this formula dictates that it is, in theory, impossible to reach 100% rack heat, which is why the above sections used the more accessible numbers of 50% and 90%. However, in practice, once rack heat passes 99% it's near enough to 100% that it can be effectively considered 100%; and besides, if you're overheating your modules to the point that you hit 99% rack heat you're well on the road to burning out the entire rack anyway.

  1. # Rack heat dissipation

When no modules in a rack are being overheated, the rack will dissipate stored heat, at a rate proportional to how hot the rack is. The rate of dissipation is:
> <math>\displaystyle \text{Heat Dissipation per second} = ( \text{Current Rack Heat }\% ) \cdot 1 \%</math>

For example, at 60% rack heat, the rack will lose heat at 0.6%/second.

Unlike heat generation, heat dissipation is constant across all ship sizes.

The actual time required for a rack's heat to dissipate can be calculated using the following formula:
> <math>\displaystyle \text{H(t)}= \text{H(0)} \cdot e ^ \left( \text{-t} \cdot \text{heatDissipationRate} \right)</math>
or, rearranged,
> <math>\displaystyle \text{t} = 100 \cdot \ln{\frac{\text{H(0)}}{\text{H(t)}}}</math>
where
- t is time in seconds
- H(t) is the target heat level, as a decimal (for example, 90% = 0.9)
- H(0) is the initial heat level
- heatDissipationRate is 0.01 (on all ships)

So, for example, the time required for a ship to drop from 90% rack heat to 50% rack heat is equal to
> <math>\displaystyle \text{t} = 100 \cdot \ln{\frac{0.9}{0.5}} = 100 \cdot 0.58778 =  \text{58.8 seconds}</math>
and the time required to drop from 50% rack heat to 20% rack heat is equal to
> <math>\displaystyle \text{t} = 100 \cdot \ln{\frac{0.5}{0.2}} = 100 \cdot 0.91629 =  \text{91.6 seconds}</math>
The logarithmic nature of this formula implies that actually reaching 0% rack heat is impossible, so at some low value (unknown but below 1%) the server simply rounds down to 0%. If we assume that low value is 0.5%, then the maximum possible heat dissipation time is
> <math>\displaystyle \text{t} = 100 \cdot \ln{\frac{1.0}{0.005}} = 100 \cdot 5.2983 =  \text{529.8 seconds}</math>
-Which is just less than 9 minutes.

The following is a quick-reference table of heat dissipation times

| - | Heat Level | 100% | 90% | 80% | 70% | 60% | 50% | 40% | 30% | 20% | 10% | 0% |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Time to lose next 10% | 10.5s | 11.8s | 13.4s | 15.4s | 18.2s | 22.3s | 28.8s | 40.5s | 69.3s | 299.6s | - |  |
| Cumulative loss time from 100% | - | 10.5s | 22.3s | 35.7s | 51.1s | 69.3s | 91.6s | 120.4s | 160.9s | 230.2s | 529.8s |  |

This table also demonstrates a very useful rule-of-thumb for managing rack heat in combat: It takes **69 seconds** for a rack's heat to drop by half.

  1. # Heat attenuation values

In most cases, the number of slots in a rack directly corresponds to that rack's <code>heatAttenuation</code> attribute

| Slot count | heatAttenuation |
| :--- | :--- |
| 1 | 0 |
| 2 | 0.25 |
| 3 | 0.5 |
| 4 | 0.63 |
| 5 | 0.707 |
| 6 | 0.758 |
| 7 | 0.794 |
| 8 | 0.82 |

  1. # Master overheat damage formula

The odds for a given module to sustain overheat damage on a single cycle can be condensed into one formula:

> <math>\displaystyle \text{Damage Chance}= \text{Rack Heat} \cdot \left( \frac{\text{Online Hi+Mid+Low Modules}}{\text{Total High+Mid+Low+Rig Slots}} \right) \cdot \text{heatAttenuation}^\mathrm{Distance}</math>

For example:
- An **Enyo** (slots 5/3/4, 2 rigs), with 1 empty High slot, at 60% Rack Heat, overheating a Warp Scrambler in mid rack slot 1.

Odds of damaging the Warp Scrambler itself:

- Damage Chance = 0.6 * [4+3+4 / 5+3+4+2] * [0.5 ^ 0]
- Damage Chance = 0.6 * [11 / 14] * 1
- Damage Chance = 0.6 * 0.786 * 1
- Damage Chance = 0.471 = 47.1%

Odds of damaging the modules in slots 2 and 3:
- Slot 2 = 0.6 * [4+3+4 / 5+3+4+2] * [0.5 ^ 1]
- Slot 2 = 0.471 * 0.5
- Slot 2 = 0.236 = 23.6%

- Slot 3 = 0.6 * [4+3+4 / 5+3+4+2] * [0.5 ^ 2]
- Slot 3 = 0.471 * 0.25
- Slot 3 = 0.118 = 11.8%

1. # External links
- [The original EVE Forum thread](https://forums-archive.eveonline.com/message/344300/) by Kadesh Priestess (2011), containing his research on overheat math.
- [Everything you need to know about heat](https://www.youtube.com/watch?v=3B0c_D7XGSk) (2019), a complete guide video by successful PvP pilot Suitonia.
- [EVE Online Fanfest 2007 - Presentation - Tuxford - Heat](https://www.youtube.com/watch?v=bR1n0HxgYeo) (2007), CCP introduces heat to the game and the underlying math that makes it work.
