---
title: "Weapons"
url: "https://wiki.eveuniversity.org/Weapons"
pageid: 19245
source: "EVE University Wiki"
categories: ["Combat", "Weapons"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Weapons

Weapons are modular systems that project effects to targeted entities. Most weapons are offensive and do damage to their targets. A few weapons act to weaken their targets, and a few are defensive in nature. This page gives a broad overview of EVE weapons systems. For detailed information follow the links to specific weapons topics. (Weapons intended for **capital ships** are not included here.)

1. # Generic weapon types
Weapons usually consist of a ship module that serves as a weapons platform, and ammunition that is expended as the platform fires.

There are four generic types of weapons in EVE: Turrets, Launchers, E-War and Drones.
- **Turrets** are revolving modules that fire their ammunition in a straight line out from the ship. Turrets further break down into
  - Energy: laser beams - EM and Thermal damage
    - Pulse lasers: short range
    - Beam lasers: long range
  - Hybrid: charged particles - Kinetic and Thermal damage
    - Blasters: short range
    - Railguns: long range
  - Projectile: solid projectiles - any damage type
    - Autocannon: short range
    - Artillery: long range
  - Precursor: exotic matter streams - Thermal and Explosive damage
    - Entropic Disintegrators: short range
- **Launchers** fire self-propelled ammunition that homes in on its target and causes damage when it arrives. Launchers can deliver any damage type, and come in three general types
  - Rockets, Heavy Assault Missiles, Torpedoes, XL Torpedoes: short range
  - Light Missiles, Heavy Missiles, Cruise Missiles, XL Cruise Missiles: long range
  - Rapid Launchers: undersized missiles on rapid-fire launchers, effective against smaller targets
- **Vorton Projectors** fire arcing lightning that also damage entities near the target. EM and Kinetic damage, long range.
- **Electionic warfare** (e-war) modules do not directly damage targets, but work to reduce their fighting capabilities. They come in a variety of different forms, and are often used in combination with turrets or launchers.
- **Drones** are semi-independent units that fly out to attack target ships. They are controlled by the pilot, can deal any type of damage, do not use ammunition, and are often used as secondary weapons on larger ships. However, they can be targeted and destroyed by enemies.
There are also two special weapons types: **Bombs** and **Smartbombs**, which will not be discussed on this page.

1. # Launchers and Turrets

The most widely used weapons in EVE fire ammunition at a target. Each kind of weapons module typically comes in small, medium, and large - though the naming conventions may use other descriptive terms. You can usually expect smaller weapons modules to load faster and fire more quickly than large ones. Smaller modules tend to do less damage per hit with a rapid hit rate, while larger weapons tend to do more damage per hit with more time between hits.

In practice a small, fast ship can kill a large, slow one more easily than the reverse. The large ship uses large weapons that are very powerful, but are inaccurate against small targets. The small ship does not have powerful weapons, but by moving quickly enough to avoid the larger ship's targeting, it can deliver a large number of small hits without being hit itself. This kind of encounter has as much to do with the relative skills of the pilots as with the weapons characteristics of the ships, and the moral is that the skills of an experienced pilot are usually more important than hulls and modules.

  1. # Damage
There are four **generic types of damage**: Thermal, Explosive, Electromagnetic (EM) and Kinetic. To some extent these are related to the physical aspects of real world damage, but for the most part in game they can simply be considered as categories.

The damage a weapon can deal is based on the type of ammunition used, the ship which is using the weapon and any skill-based or role-based bonuses it has, the presence of additional "damage mods" equipped to the ship (which increase the damage and fire rate of weapons), and for turrets, the turret's Damage Multiplier statistic. Damage is generally measured in both "Alpha" or "Volley", the damage dealt by a single shot of all weapons together; and in Damage-Per-Second or DPS, the damage dealt in a shot divided by the time in between shots.

Ships use shields, armor, and hull to **ward off damage**. Matching the ammunition used to the weakness in the defenses of enemy ships is an important aspect of EVE combat. Similarly, matching the weapons system range, speed, and power to the target's speed and location is essential.

Thus, the damage a weapon *actually* deals to a target is based on the target's damage resistances, the types of damage the weapon's ammunition deals, and how easily the weapon can hit the target based on the target's distance, relative flight speed, and size.

  1. # Ammunition
Ammunition plays a large role in weapons effectiveness. The type of ammunition used determines the types and amount of damage dealt, and can also increase or decrease weapon range, tracking or accuracy, and capacitor usage.

Note that weapon modules do not determine the type of damage done: whether thermal, explosive, electronic or kinetic; this is determined solely by the ammunition. Some kinds of ammunition deal damage in only one category; others do damage in multiple categories. However, ammunition is designed for specific weapons, and so it is often said that some weapons only deal specific types of damage. (i.e. "Hybrid Turrets are locked to Kinetic-Thermal", because all Hybrid Charges deal a mix of only Kinetic and Thermal damage.)

  1. # Really quick comparison
{{Color box
| color= var(--background-color-warning-subtle)
| border= #FFEEEE
| Fighting in space is a matter of physics. The detailed comparison chart below is based on physics but doesn't show it. The math in **Turret Mechanics** and **Missile Mechanics** explains the following in more detail. You can find it there if you want it - some do; some don't.

So, imagine you are in a missile boat and have locked onto a ship carrying lasers. You both fire at the same time. The laser hits you immediately. Meanwhile, your missile is flying through space. The question is: do you have enough time to fire enough missiles for the kill, or will the laser burn you out first?

More:
- If a target is standing still, you can hit it with anything. (The same is true of you … so keep moving.)
- Short-range weapons generally fire more frequently than long-range weapons
- Missiles home in on their targets.
> - Each hit always does some damage - they almost always hit. However, the size of the missile and the size and speed of the target can reduce how much damage they deal.
> - They take a long time to get there, but they lose no damage at long range.
> - They can deal any type of damage, but some ships have a preferred damage type.
> - They do not use capacitor but reload slowly.

- Turrets fire a stream of stuff - pellets, pulses, ray beams - in a straight line. They spin themselves around to point that line at their target.
> - Individual shots fired can frequently miss, but there are a lot of shots fired.
> - They reach their targets immediately, but their accuracy drops at longer range.
> : *Projectiles*: use no capacitor, can deal any type of damage. Slow reloading.
> : *Hybrids*: use some capacitor, Kinetic/Thermal. Fast reloading.
> : *Energy*: use a lot of capacitor, EM/Thermal, no reloading and immediate crystal swapping.
> : *Disintegrators*: use some capacitor, Thermal/Explosive. Immediate reloading. Damage increases over time, however bonus damage is lost by reloading or target leaving range.

- Vorton Projectors fires thick arching lightning, attracted by entites in space.
> - Like turrets, they reach their targets immediately.
> - Like missiles, each hit always does some damage as they always hit. However, the size of the lightning and the size and speed of the target can reduce how much damage they deal.
> - Unlike turrets and missiles, they do not spin themselves to point at targets, or fire entities that chase targets, but instantly cast effects on targets.
> - Due to how they do damage, the relative position and speed between the user and the target aren't matter with damage application at all, as long as the target is in range.
> - When the target is damaged, other entities near it are damaged too.
> - They deal EM and Kinetic damage.
> - They use a lot of capacitor.
> - They are fast reloading.

And if you want a bit more...............

Missiles chase; turrets turn.

Missiles depend on time. They can chase a target a long way before they explode.

Turrets depend on tracking and range. Optimal range is the place where you have the best chance to hit - not guaranteed, just the best odds. Falloff range determines how quickly accuracy gets worse outside optimal. At optimal + falloff range, the turret has a 50% chance to hit (not considering Tracking).

Tracking is how fast the turret can turn to follow the target. Faster is better. Why? Because the target is not standing still and neither are you.
}}

  1. # Weapons comparison chart
There is no "best" weapons system. Each has its own advantages and disadvantages, and in the long run you will probably seek out ships that give preference to the weapons for which you have trained skills. The most important thing, therefore, is to have a good **skills plan** to carry you forward into the game.

This table is meant to provide only a rough comparison. For detailed specifications, go to the pages for the individual weapons.

| Weapon type
! Range Class
! Range Relative
! Firing speed
! Reloading
! Magazine size
! Accuracy /Precision
! style="width: 100px;" |Damagetype
! Damageper hit
! Capacitoruse
! colspan= "2" | Links |
| :--- |
| Launcher |
| Light Missiles / Heavy Missiles |
| Torpedo / XL Torpedo |
| Cruise Missile / XL Cruise Missile |
| Rapid Launcher |
| Turret |
| Railgun |
| Energy |
| Beam Laser |
| Projectile |
| Artillery |
| Precursor |
| Vorton Projector |

  1. # Tactical choices
A new player's choice of ship may be based on the racial weapons training that they have done in their early days. Luckily, each race offers a selection of **frigates**, one of which can be used for close in fighting ("brawling"), and one of which can be used in long distance fighting ("sniping"). In addition, racial bonuses apply to frigates in a straightforward way. Thus, you can be sure that a Caldari frigate will use rockets or missiles, that an Amarr ship will use energy weapons, and so on. (Larger ships can deviate from this pattern.)

Entropic Disintegrators and Vorton Projectors are much more advanced and expensive weapons systems to train for and use. As such, they are not included in these summaries.

This chart shows typical frigate choices for the two types of tactics. These are just observations - you should always do a close analysis of a ship relative to your skills before you buy one.

| -
! Tacticalapproach
! Race
! Weapon
! Ammo
!Capacitoruse
! Frigate |
| :--- |
| **Brawling** |
| Caldari |
| Gallente |
| Minmatar |
| **Sniping** |
| Caldari |
| Gallente |
| Minmatar |

Not surprisingly, experienced players will disagree as to which is the "best" brawling or sniping frigate. The ones listed here are often used, however, and if you are a new player, you may want to start with one of these and then move in whatever direction your interests (and skill developments) take you.

  1. # Weapon names reference

| Weapon type
! rowspan="2" | Range 
! colspan="2" | Small 
! colspan="2" | Medium 
! colspan="2" | Large 
! colspan="2" | Extra Large
! rowspan="2" | User |
| :--- |
| *Frigates, Destroyers* |
| Turret |
| Dual Light |
| Small Focused |
| Beam Laser |
| Small Focused |
| Heavy |
| Hybrid |
| Ion |
| Neutron |
| Railgun |
| 125mm |
| 150mm |

1. # Electronic warfare

Technically, E-war does not do damage, but generally acts to disable or otherwise reduce the effectiveness of enemy ships. E-war does require modules, however, and since these take up space that might otherwise have contributed to the ship's offense or defense, E-war is most often used in the context of fleets. (Note that most E-war will not work against NPC mission ships.)

New players will likely put a premium on developing their offensive weapons skills. A small investment in the development of one or two low level e-war skills, however, can pay off in making the player more useful in fleet actions.

  1. # Racial E-War
Each of the four player races has ships that specialize in one kind of ***racial* E-War**. In addition each race has a corresponding **drone** that does the same thing. In each case, the targeted ship is not damaged, but it becomes less effective.

- **Weapons disruption** - *reduced weapons range and accuracy*
"Disruption" means reducing or closing down. **Tracking Disruptors** reduce the range and tracking of turrets, while **Guidance Disruptors** reduce the range and precision of missiles.
- **Sensor Dampening** - *reduced targeting ability*
Sensor dampening reduces the targeting range and **scan resolution** of an opponent's ship. This makes it harder for them to find their potential targets.
- **Electronic Countermeasures** - *break target locks*
ECM "jammers" are used to disrupt the targeting apparatus of the target ship. The **basics of ECM jamming** are fairly simple, although the **mechanics of how it works** are more complex. When you successfully jam an enemy ship, it cannot target lock on your fleetmates for a period of time. The drawback is that it can still attack *you*, but it is easy to see why jamming is useful in many fleet actions.
- **Target Painting** - *becomes easier to hit*
Target painting makes it easier for turrets and missiles to hit the target ship and is especially effective against small, fast targets. Target painting improves everyone's chance of hitting the target and so is especially useful in fleet actions.

  1. # Other E-war
In addition, tackling and capacitor warfare modules may be considered E-war weapons.
- **Tackling**
  - Stasis Webifier** modules are used to slow down a target ship, either to pull it out of position or make it easier for everyone to hit. **Warp Scramblers** prevent a ship from warping out. Used together, these can trap an enemy ship until it can be destroyed. Tackling modules are among the most widely used weapons in EVE.

- **Capacitor Warfare**
Modules such as Energy Neutralizers and Nosferatus reduce the **Capacitor** of the target ship. Since many ships depend on capacitor for weapons or defense, this increases the target's vulnerability. **Energy Neutralizers** use the player's ship capacitor to drain large amounts from the target ship. **Nosferatu** drain small amounts from the target ship but transfer that power to the player's ship.

  1. # Tactical choices
Your choice of ship may be based on the racial weapons training that you have done in your early days. Luckily, each race offers a **frigate** that can be used for e-war. Each of these has bonuses for its race's e-war specialty.

This chart shows typical frigate choices for e-war. These are just observations - you should always do a close analysis of a ship relative to your skills before you buy one.

| -
! E-war !! Race !! Weapon !!Fitting Slot !! Frigate !! Special Skills Not always required, but always useful |
| :--- |
| Amarr |
| Caldari |
| Gallente |
| Minmatar |
| Any |
| Any |

<sup>*</sup>Standard frigates generally do not have bonuses for capacitor warfare. However, there is a class of "fast frigates" that are bonused for tackling. Each race has one fast frigate, each of which also has its race's offensive weapons bonuses.
- Amarr: **Executioner**
- Caldari: **Condor**
- Gallente: **Atron**
- Minmitar: **Slasher**

1. # Drones

Combat drones are semi-independent mini-ships that fly out to damage and destroy enemy targets. Ships have space for a limited number of drones (some have none). Some ships, known as **drone carriers**, have room for a large variety of drones and use them as their primary weapons. 

Drones are a broad, somewhat complex, category of weapons. They require an investment in skill training, but since most larger ships carry at least a drone or two, improving their effectiveness can pay off in expanded offensive capability.

  1. # **Combat drones**
There are three sizes of basic combat drones:
- Light: effective on frigate and destroyer-sized ships.
- Medium: effective on cruisers and battlecruisers.
- Large: effective on battleships.

Each does one particular kind of damage: thermal, kinetic, EMP or explosive. As drones get larger, they get slower and have a harder time with targets that are faster then they are. Combat drones are launched when needed, will orbit the player's ship if not busy, and can be ordered back into the drone bay. Drones can be damaged, and if not destroyed can be repaired along with the ship.

  1. # **Sentry drones**
Sentry Drones are stationary long-range turrets. They come in each of the four damage types and with varying optimal ranges. After sentry drones are launched, they remain where they were left as the combat unfolds. The player ship must fly back and pick them up when it is ready to leave.

Sentry drones can deal high damage at long ranges, but their accuracy suffers greatly at closer ranges. Their immobility is both a blessing and a curse: on the one hand, they do not need to fly out to their targets to hit them, and thus they can swap between targets and hit them immediately; on the other hand, a ship using them must fly back to them to pick them up in order to deploy them in a new place (or not abandon them). In addition, they take up considerable room in a ship's drone bay, and so only larger ships can use them effectively.

  1. # **E-war drones**
Each of the **racial e-war types** has a corresponding drone with its own skill training. Drones for tackling and capacitor warfare are also available. The only E-war drones commonly used are ECM Drones, as E-war drones are both much weaker than ship-mounted e-war modules, and far more fragile than other combat drones.

  1. # Tactical choices
Drones are a specialty of the Gallente. The **Tristan** is the only standard frigate that can carry a full flight of light combat drones. This makes it an easy choice for new players who want to focus on drones. Among basic cruisers, the **Vexor** and the **Arbitrator** have larger capacity for and bonuses to drones.

1. # Skills
  - Skill training** can improve the effectiveness of weapons module and their ammunition including aspects such as, range, firing speed, targeting speed and damage. There also are various skills that improve the use of E-war and drones. And training in "non-weapons" areas, such as navigation or spaceship command, can directly impact the effectiveness of a ship's weapons too.

There are *many* skills that affect weapons. A few examples:
- : 5% bonus to rocket damage per skill level.
- : 5% Bonus to small hybrid turret damage per level.
- : 5% bonus to weapon turret optimal range per skill level.
- : increases the defensive abilities of your drones by 5% per level
- : +1 extra target per skill level.
- : 5% bonus to capacitor capacity per skill level.
- : 2% improved ship agility for all ships per skill level.

Because ships often have bonuses for particular kinds of weapons, the weapon skills you develop will have an impact on the kinds of ships you want to fly. It is worth the small amount of time it takes to develop a skill plan. The **E-Uni CORE Skill Plans** will give a character a basic grounding in small and medium weapon systems. New players are also directed to the **Basic Skills** page which lists all of the skills relevant to beginning the game.
