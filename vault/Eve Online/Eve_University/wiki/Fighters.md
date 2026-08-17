---
title: "Fighters"
url: "https://wiki.eveuniversity.org/Fighters"
pageid: 1471
source: "EVE University Wiki"
categories: ["Needing updates", "Weapons"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Fighters

Fighters are extremely powerful **Drones** equipped with cruiser, battleship, or dreadnought-grade weaponry, launched by **carriers**, **supercarriers**, **Guristas** capital ships, and Upwell Structures.

1. # General Fighter Mechanics
In order to use fighters you need to train  (5% damage bonus per level). There are 3 types of fighters: Light (Anti-Subcapital), Heavy (Anti-Capital), and Support (EWAR). Each has a Tech 1 and Tech 2 variant. Light fighters and heavy fighters are further split between the roles they perform. Each type of fighter has a squadron size that determines how many individual fighters make up a squadron, and each carrier or supercarrier is limited by how many launch tubes exist for squadrons. A squadron of fighters is controlled and targeted as a single entity in space, and will generate a Killmail if the last fighter in a squadron is destroyed. Fighters are a lot larger, in volume, than drones. The skill  increases fighter hangar size by 5% per level.

If fighters are more than 300&nbsp;km from your carrier or structure and you recall them to their launch tube, they will quickly warp back.

Fighters cannot receive remote assistance, such as repairs or shield boosting. However, they are vulnerable to **ECM**, and with their weak sensor strengths, jamming fighters is a common strategy for reducing a carrier's damage potential.

Each race has each its own fighters, their damage matches the race's primary damage type, and they follow the same racial patterns of damage versus speed which are present on ordinary drones.

Most Fighters have two weapons systems: a primary weapon which can be fired continuously, and a secondary weapon with high damage but a cool-down and limited ammunition. When firing, all (alive) fighters in a squadron fire together, and their damage is added together.

Fighters have thick, regenerating Shields, but no Armor and only 100 Structure HP. As a fighter squadron sustains damage, the rightmost segment of its health indicators will shift color from green to yellow to red to black. When a fighter squadron sustains damage equal to the Shield (and Structure) HP of one of its fighters, one fighter is destroyed and the squadron's damage is reduced accordingly. Tech I fighters have 0% resistance to all damage, however Tech II fighters' shields come with a 30% bonus to their faction's primary resistance, and a 15% bonus to their faction's secondary resistance.

When Fighters are recalled to their carriers, they go through a short Refueling period before they can be launched again. The duration of this period is based on the number of fighters in the squadron. During this refueling period, their shields are restored and the ammunition for their secondary weapons is reloaded, and after refueling completes, new fighters can be loaded into a tube to replace any fighters which were destroyed.

Like Drones, Fighters can also be Abandoned in space in case of emergency. Unlike Drones, there is no Drone Control Range which limits the range at which Fighters can engage targets. The only limit on a fighter's engagement range is the extremely long targeting range of the carriers which launch them.

Fighters have Destroyer to Cruiser-sized signature radii of 88-120m. Combined with their high speeds, this makes fighters most effectively targeted by Small or Medium weapons and drones.

All Fighters also have Standup versions which can be used by most Upwell Structures. Standup Fighters do not require training in Fighter skills, and can be used by any player with access to Take Control of a structure. Standup fighters have improved base stats over regular fighters (2x speed, 2.5x damage, better explosion velocity and radius, +50% shield HP, better ECM resistance, 2x cargohold volume) but are not affected by any modules or player skills. Standup Fighters can be changed and loaded while an Upwell structure is damaged or Reinforced.

1. # Fighter Damage Mechanics
Fighter weapons use a variation of **Missile damage mechanics**: their weapons have explosion radii and velocities, and deal constant damage with no chance of missing. However, they also have optimal and falloff ranges, which obey the standard falloff curve of Turrets and Electronic Warfare modules.

> <math> \displaystyle \text{Total Damage} = \text{Base damage} \times {\it N} \times \min \left( 1, \frac{ Signature }{ Explosion\ radius }, \left(\frac{ Signature \times Explosion\ velocity }{ Explosion\ radius \times\ Velocity } \right)^{DRF} \right) \times
0.5^{ \left(\frac{\max(0,\ Distance - Optimal )}{ Falloff } \right)^2} </math>

Where
- Total Damage is the actual damage dealt, before resistances.
- Base damage is the damage displayed in the fighters' Show Info window.
- *N* is the number of fighters in the squadron.
- Signature is signature radius of the target.
- Velocity is velocity of the target.
- Explosion radius and explosion velocity are values for the fighters' weapon.
- Distance is the distance between the fighters and their target.
- Optimal and Falloff are the values for the fighters' weapon.
- DRF is the damage reduction factor. This is not visible either in-game, or in database statistics for fighters. In stead, it is calculated from two other values:

> <math> \displaystyle \text{DRF} = \frac{ \ln \left( \text{Damage reduction} \right) }{ \ln \left( \text{Damage sensitivity} \right) } </math>

Where Damage Reduction is specific to the weapon the fighter is using, and Damage Sensitivity is always equal to 5.5. Because these values are constants, the resulting DRF values can be easily calculated.

| - style="background-color: var(--background-color-warning-subtle);"
! Fighter type 
! Weapon
! Damage Reduction
! DRF |
| :--- |
| Space Superiority |
| Light Attack |
| Light Attack |
| Heavy Attack |
| Heavy Attack |
| Shadow |
| Heavy Long-Range |

A shorthand on the results of the range formula:
- Within Optimal range, the weapons can deal full damage.
- At Optimal+Falloff, the weapons deal 50% damage.
- At Optimal+(Falloff x2), the weapons deal 6.25% damage.
- Beyond Optimal+(Falloff x3), the weapons deal effectively no damage.

These mechanics mean that fighter damage is very predictable, and can be effectively mitigated using Afterburners (but much less effectively mitigated using Microwarpdrives). However, the lack of a 'tracking' type attribute mean that the fighters' own high speed is ignored when considering their ability to deal damage. In practice, because of their flight speed, fighter damage tends to be dealt as "If the fighters are not in orbit range, they do not deal damage; If the fighters are in orbit around a target, they deal full damage." As such, this range calculation generally is only important for long-range heavy fighters.

1. # Light Fighters
Light fighters require the skill  (5% bonus in light fighter velocity per level). Tech 2 light fighters requires Light Fighters IV.

  1. # Attack Fighters
Attack fighters are general purpose attack craft, equipped with a faction-specific primary weapon (i.e., blaster cannon, pulse cannon, autocannon) with a short effective range. Their secondary weapon is a Heavy Rocket Salvo, effectively a single volley of battleship-grade torpedoes. Also, these fighters are equipped with a Microwarpdrive that increase base speed by 500%, at the cost of a 500% signature radius increase, with a 20-second duration and 60-second cooldown.

Light attack fighters are effective against cruisers and battleships, but will struggle to effectively damage frigates and are not generally hard-hitting enough to engage capital ships.

All damage values on this page are per-fighter, not per-squadron.

| General Stats |
| :--- |
| Squadron Size |
| 22px|link=]] Volume |
| 22px|link=]] Signature Radius |
| 22px|link=]] Shield Capacity (T1) |
| 22px|link=]] Shield Capacity (T2) |
| 22px|link=]] Shield Capacity (Faction) |
| 22px|link=]] Refueling time |
| 22px|link=]] Explosion Radius (cannon) |
| 22px|link=]] Explosion Velocity (cannon) |
| 22px|link=]] Fire rate (cannon) |
| 22px|link=]] Explosion Radius (rocket) |
| 22px|link=]] Explosion Velocity (rocket) |
| 22px|link=]] Fire rate (rocket) |
| 22px|link=]] Rocket range |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Tech
! Damage
! Rocket Damage
! Range
! Falloff
! Speed (Base)
! Speed (MWD)
! Orbit |
| :--- |
|  Amarr |
| Tech II |
| Faction |
|  Caldari |
| Tech II |
| Faction |
|  Gallente |
| Tech II |
| Faction |
|  Minmatar |
| Tech II |
| Faction |

  1. # Space Superiority
Space Superiority fighters are anti-drone and anti-fighter weapons. Their primary weapons, Micro Missile Swarm, are extremely efficient at killing hostile drones and fighters, however deal greatly reduced damage (-95% damage) to real ships. Defensively, they can enact evasive manuevers that increase base speed by 200%, reduce signature radius by 80%, and increase all shield resists by 50%. Lastly, they can tackle hostile drones and fighters (but only drones and fighters), slowing them and disabling their warp drives.

| General Stats |
| :--- |
| Squadron Size |
| 22px|link=]]Volume |
| 22px|link=]]Signature Radius |
| 22px|link=]]Shield Capacity (T1) |
| 22px|link=]]Shield Capacity (T2) |
| 22px|link=]]Shield Capacity (Faction) |
| 22px|link=]] Refueling time |
| 22px|link=]] Explosion Radius |
| 22px|link=]] Explosion Velocity |
| 22px|link=]] Fire rate |
| 22px|link=]] Range |
| 22px|link=]] Fighter Tackle range |

| -  style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Tech
! Damage
! Speed (Base)
! Speed (AB)
! Orbit |
| :--- |
|  Amarr |
| Tech II |
| Faction |
|  Caldari |
| Tech II |
| Faction |
|  Gallente |
| Tech II |
| Faction |
|  Minmatar |
| Tech II |
| Faction |

1. # Heavy Fighters
Heavy Fighters are anti-capital-ship fighters, and can only be used by supercarriers. Each race has its own heavy fighters, which follow the same damage and speed patterns as light fighters.

Heavy fighters need the Heavy Fighters skill (5% damage increase per level), while Tech 2 heavy fighters requires the skill Heavy Fighters IV.

  1. # Heavy Attack
Heavy Attack fighters use a faction specific primary weapon (i.e., blaster, pulse laser, or autocannon), while their secondary weapon is a very high damage Torpedo Salvo. The large explosion radii of these weapons renders them only effective against capital ships. Additionally, they possess a Microwarpdrive that increases base speed by 500% and signature radius by 500%, with a 20-second duration and 60-second cooldown.

There is also a **Sansha** faction heavy fighter (the **Shadow**). The Shadow deals both EM and Thermal damage, significantly higher total damage than an ordinary T1 heavy fighter, and has better damage application than an ordinary heavy fighter, but does not have the secondary torpedo salvo.

| General Stats |
| :--- |
| Squadron Size |
| 22px|link=]]Volume |
| 22px|link=]]Signature Radius |
| 22px|link=]]Shield Capacity (T1) |
| 22px|link=]]Shield Capacity (T2) |
| 22px|link=]] Refueling time |
| 22px|link=]]Explosion Radius (cannon) |
| 22px|link=]]Explosion Velocity (cannon) |
| 22px|link=]] Fire rate (cannon) |
| 22px|link=]]Explosion Radius (torpedo) |
| 22px|link=]]Explosion Velocity (torpedo) |
| 22px|link=]] Fire rate (torpedo) |
| 22px|link=]] Torpedo range (T1) |
| 22px|link=]] Torpedo range (T2) |
| 22px|link=]]Shield Capacity (Shadow) |
| 22px|link=]]Explosion Radius (Shadow) |
| 22px|link=]]Explosion Velocity (Shadow) |
| 22px|link=]] Fire rate (Shadow) |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Tech
! Damage
! Torpedo Damage
! Range
! Falloff
! Speed (Base)
! Speed (MWD)
! Orbit |
| :--- |
|  Amarr |
| Tech II |
|  Caldari |
| Tech II |
|  Gallente |
| Tech II |
|  Minmatar |
| Tech II |
| Sansha |

  1. # Long Range Attack
Long Range Attack fighters have faction specific long-range weaponry (i.e, beam cannon, railgun, and artillery), a **Micro Jump Drive** for range control, and are capable of launching unguided bombs (much like **stealth bomber**s but weaker). Fighter bombs have the same 30km range, 12s flight time, and 15km damage radius of regular bombs, and are *immune* to their given damage type (making it impossible for multiple matching bombs to destroy each other in flight). Usage of these bombs are disallowed in Low Security space.

The weapons of long ranged fighters can be used against battleships, but their explosion radii leaves Light Attack Fighters as more efficient against smaller subcapital ships. This said though, long ranged fighter damage can be absolutely *devastating* to cruisers or battlecruisers with active microwarpdrives.

| General Stats |
| :--- |
| Squadron Size |
| 22px|link=]]Volume |
| 22px|link=]]Signature Radius |
| 22px|link=]]Shield Capacity (T1) |
| 22px|link=]]Shield Capacity (T2) |
| 22px|link=]] Refueling time |
| 22px|link=]]Explosion Radius (cannon) |
| 22px|link=]]Explosion Velocity (cannon) |
| 22px|link=]] Fire rate (cannon) |
| 22px|link=]] Damage (bomb) |
| 22px|link=]]Explosion Radius (bomb) |
| 22px|link=]] Fire rate (bomb) |
| 22px|link=]]Micro Jump Drive Range |
| 22px|link=]]MJD Activation Time |
| 22px|link=]]MJD Signature Penalty |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Damage
! Optimal
! Falloff
! Speed (Base)
! Orbit |
| :--- |
| Amarr |
| Ametat II |
| Caldari |
| Termite II |
| Gallente |
| Antaeus II |
| Minmatar |
| Gungnir II |

1. # Support Fighters
Support fighters are specialized fighters that each perform their own type of **EWAR**. They also each come with a Microwarpdrive, increasing their speed (and signature) by 500% for 20 seconds on a 60 second cooldown. However, they have no weapons. Unlike the others, the Siren warp disruption fighters have an Afterburner in stead of a Microwarpdrive, meaning they have a lower boost speed, but without the signature radius penalty. Support fighters require the  skill (5% increase in support fighter hit-points per level). Tech 2 support fighters requires Support Fighters IV.

| - style="background-color: var(--background-color-warning-subtle);" | General Stats |
| :--- | :--- |
| Squadron Size | 3 |
| 22px|link=]]Volume | 3000m<sup>3</sup> |
| 22px|link=]]Signature Radius | 120m |
| 22px|link=]]Shield Capacity (T1) | 6800 HP |
| 22px|link=]]Shield Capacity (T2) | 7500 HP |
| 22px|link=]] Refueling time | 2s |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Energy Neut
! Optimal
! Falloff
! Speed (Base)
! Speed (MWD)
! Orbit |
| :--- |
| Amarr |
| Cenobite II |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Jamming Strength
! Optimal
! Falloff
! Speed (Base)
! Speed (MWD)
! Orbit |
| :--- |
| Caldari |
| Scarab II |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Warp Disruption
! Range
! Speed (Base)
! Speed (AB)
! Orbit |
| :--- |
| Gallente |
| Siren II |

| - style="background-color: var(--background-color-warning-subtle);"
! Faction
! Fighter
! Velocity Reduction
! Range
! Speed (Base)
! Speed (MWD)
! Orbit |
| :--- |
| Minmatar |
| Dromi II |

1. # Fighter Improving Modules
Many modules which improve Drones also improve Fighters. All modules in this list are subject to **Stacking penalties**

| - style="background-color: var(--background-color-warning-subtle);" | High slot modules |
| :--- | :--- |
| link=|]] | wheat|Fighter support unit}}''' improves the rate of fire, velocity, shield HP, and shield recharge rate of fighters by 5% for T1 variants, and 6% for T2 variants. Since these modules boost rate of fire rather than raw damage, they do not share stacking penalties with Drone Damage Amplifiers. |
| link=|]] | wheat|Drone Navigation Computer}}''' increases fighter speed by 25% (30% for the Tech 2 variant). |
| link=|]] | wheat|Omnidirectional Tracking Link}}''' increases fighter weapon optimal and falloff ranges, increases weapon explosion velocity and decreases explosion radius. Can be loaded with scripts to either double the range bonus or the application bonus, at the cost of eliminating the other bonus. Long-ranged heavy fighters can benefit from the range bonus, and all fighters can benefit from the application bonus when engaging cruisers and smaller ships. Unlike all other fighter-enhancing modules, these need to be activated to provide their effects. |
| link=|]] | wheat|Drone Damage Amplifier}}''' increases the damage your fighters deal by 15% (20.5% for the Tech 2 variant). |
| link=|]] | wheat|Omnidirectional Tracking Enhancer}}''' increases fighter weapon optimal and falloff ranges, increases weapon explosion velocity and decreases explosion radius. It's similar to the mid-slot Omnidirectional Tracking Link module, but provides slightly higher bonuses to range, and slightly lower bonuses to tracking. Also, it cannot be scripted, and is a passive module (i.e. it does not need to be activated and uses no capacitor energy). |
