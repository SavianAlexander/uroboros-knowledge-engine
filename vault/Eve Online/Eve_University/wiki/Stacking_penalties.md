---
title: "Stacking penalties"
url: "https://wiki.eveuniversity.org/Stacking_penalties"
pageid: 2288
source: "EVE University Wiki"
categories: ["Fitting", "Game mechanics"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Stacking penalties

- Stacking penalties** refer to an effectiveness reduction that is incurred when using two or more **module**s or **rig**s that affect the same attribute. The more modules or rigs affect the same attribute, the less effective each additional module is; in practice, having more than three or four modules/rigs affecting the same attribute is not worth it.

Most (but not all) modules and rigs will show in their description if they are subject to stacking penalties. 

Note that it is the stat bonus that is affected, not the module itself. For example, if you fit both a Nanofiber Internal Structure (boosts agility and velocity) and an Overdrive Injector System (boosts velocity), the Nanofiber's velocity bonus would suffer a stacking penalty, but not its agility bonus. Similarly with armour or shield resistance modules: if you fit an EM hardener, an explosive hardener and an omni-hardener (Multispectrum Shield Hardener or Multispectrum Coating): the EM/Explosive resistances from the omni-hardener would be stacking-penalized but the Kinetic/Thermal resistances would not.

Also of note is that module drawbacks (negative effects) can also be stacking penalized.

1. # Effects of stacking penalties

Normally, the benefits of additional modules/rigs would be multiplicative. So if fitting one Speed Booster (a fictional module with nice round numbers to make the math easier to understand) module increases a ship's speed by 10%, fitting two of them would increase a ship's speed by 21% ((1 + 10%) &times; (1 + 10%) = 1.1 &times; 1.1 = 1.21), and fitting three would increase it by 33% (1.1 &times; 1.1 &times; 1.1 = 1.33). 

However, due to the stacking penalties effect, the second, third, and fourth Speed Booster modules' effects are only partially effective (86.9%, 57.1%, and 28.3% respectively - see **below** for details), and would therefore only increase a ship's speed by:
- 10% &times; 86.9% = 9% for the second module
- 10% &times; 57.1% = 5.7% for the third module
- 10% &times; 28.3% = 2.8% for the fourth module

Therefore, the actual speed increase for the ship would be: 
- One Speed Booster module: +10%
- Two Speed Booster modules: (1 + 10%) &times; (1 + (10% &times; 86.9%)) = (1 + 10.5%) &times; (1 + 9%) = +19.8%
- Three Speed Booster modules: (1 + 19.8%) &times; (1 + 5.7%) = +26.7%
- Four Speed Booster modules: (1 + 26.7%) &times; (1 + 2.8%) = +30.3%

However, the modules' bonuses still multiply, so even if the *percentage* increase of each subsequent module decreases sharply, the *absolute* increase of each subsequent module drops off more slowly. If we take a ship with a nominal speed of 100&nbsp;m/s:
- Adding one Speed Booster module: 100 + 10% = 110 m/s, an increase of +10&nbsp;m/s
- Adding a second Speed Booster module: 110 m/s + 9% = 120 m/s, an additional increase of +10&nbsp;m/s
- Adding a third Speed Booster module: 120 m/s + 5.7% = 127 m/s, an additional increase of +7&nbsp;m/s
- Adding a fourth Speed Booster module: 127 m/s + 2.8% = 130 m/s, an additional increase of +3&nbsp;m/s

1. # The Formula
  - thumb|400px|The effectiveness of stacking penalized modules plotted.**
Stacking-penalized modifiers are applied one at a time, in descending order of strength. 

The *n*-th modifier is multiplied by S(*n*-1), as follows:

> <math> S(u) = e^{-(u / 2.67)^2} </math>

  1. # The Numbers
The exact numbers for stacking penalties can be gained by the formula above, but here are some rounded guidelines for quick calculations that don't need to be precise:
- 1st mod: 100.0% effectiveness
- 2nd mod: ~86.9% effectiveness
- 3rd mod: ~57.1% effectiveness
- 4th mod: ~28.3% effectiveness
- 5th mod: ~10.6% effectiveness
- 6th mod: ~3.0% effectiveness
As is clear, stacking more than 3 or 4 modules or rigs - unless you really have nothing else at all that you could fit there - that affect the same stat is fairly pointless, as your benefit is so tiny.

1. # What suffers stacking penalties?

- Absolute effects are never stacking-penalized, only percentage effects. That is to say, things like +1 warp core strength, +1000 structure HP, +15&nbsp;m signature radius, +400&nbsp;GJ capacitor are not stacking-penalized because they are not percentage (%) effects.
- Modules, rigs, the effects of **Command Bursts** and environmental effects of **Abyssal Deadspace**, **Triglavian minor victory**, **EDENCOM systems** and **Pochven** are stacking-penalized.
  - Skills, ship bonuses from ship skills, implants, hardwirings, **boosters** (such as Synth Blue Pill, Strong X-Instinct, and others) and the effects of **wormhole space** are not stacking penalized.
- Negative and positive effects are stacking-penalized separately. So, one +% and one -% effect to an attribute suffers no penalties, whereas with two +% and two -% effects, one of each would only be 86.9% effective. An example might be velocity modifiers: if you have one Overdrive Injector System on your ship (to increase your speed) whilst at the same time being slowed by a single Stasis Webifier from an enemy ship - both velocity modifiers are 100% effective. If you are then affected by second Stasis Webifier (from the same or another ship) that second web will be only 86.9% effective.

It can be hard to tell exactly what suffers stacking penalties and what does not. For instance, the Overdrive Injector System II gives +12.5% velocity at a cost of -20% cargo capacity, and the description claims it suffers stacking penalties. The velocity bonus is stacking-penalized, but the cargo drawback is actually *not*. Similarly, the Warp Core Stabilizer II gives you one extra warp core strength at a cost of -40% targeting range and -40% scan resolution. It doesn't mention stacking penalty in the description, but the drawbacks *are* actually stacking-penalized. 

We can learn from this that it is not the module itself which determines whether its effects are stacking-penalized, but rather the attribute affected. 

Assuming the attribute they affect is actually stacking penalized, **Command Burst** modules are stacking penalized as normal, along with the rest of your modules and rigs.

Here's a handy table of what ship effects are stacking-penalized and which aren't; there are some weird exceptions which are further discussed below the table. Remember, it is only *percentage* effects from modules/rigs that are penalized.

1. # Is *<insert attribute>* stacking-penalized?

| - style="background-color: var(--background-color-warning-subtle);"
! Ship attribute 
! Stacking-penalized |
| :--- |
| Powergrid (including reduced-PG-need effects) |
| CPU (including reduced-CPU-need effects) |
| Cargo capacity |
| Capacitor capacity |
| Capacitor recharge rate |
| Energy Warfare resistance |
| Module capacitor use |
| Shield recharge rate |
| Shield / armor / hull hit points |
| Shield / armor / hull resistances |
| Shield boost / armor repair bonus |
| Sensor strength |
| ECM jammer strength |
| Sensor dampener scan resolution dampening strength |
| Sensor dampener targeting range dampening strength |
| Scan probe sensor strength |
| Scan resolution |
| Targeting range |
| Signature radius |
| Velocity |
| Inertia modifier (agility) |
| Mass |
| Duration (cycle time) bonuses (weapons) |
| Duration (cycle time) bonuses (other) |
| Missile launcher rate of fire |
| Missile damage |
| Missile explosion velocity |
| Missile explosion radius |
| Missile flight time |
| Missile velocity |
| Turret rate of fire |
| Turrets and missile launchers (damage bonus) |
| Turrets and missile launchers (Rate of fire bonus ) |
| Capacitor transmitters |

Many overheating bonuses are not stacking penalized simply due to the fact that there are no modules or effects that would modify the same stat as the overheat bonus.These modules are considered to be not stacking penalized until an effect that modifies same stat as the overheat bonus is released.
Modules with no overlaping effects:  
- Sensor boosters
- Capacitor boosters
- Tracking/guidance computers
- omnidirectional tracking links
- Hull repairers
- Active hardeners
- Energy neutralizers and nosferatus
- Smarbombs
- Reactive armor hardener
- Target spectrum breaker

  1. # Weird Exceptions
