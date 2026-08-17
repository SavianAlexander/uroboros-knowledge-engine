---
title: "Capacitor warfare"
url: "https://wiki.eveuniversity.org/Capacitor_warfare"
pageid: 2010
source: "EVE University Wiki"
categories: ["Game mechanics", "PvP"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Capacitor warfare

- 650px|thumb|400px|Visual effects for Energy Neutralizers (left) and Energy Nosferatus (right)**
  - Capacitor warfare** is the attack strategy of using equipment to drain a target ship's **capacitor**, its available energy for powered modules. A ship without sufficient capacitor energy can lose the ability to fire certain **weapons**, actively **repair** itself, use **propulsion equipment** or other powered modules, or even **warp** to another location.

1. # Overview
  - thumb|Heavy Energy Neutralizer I stats**
Capacitor warfare (or "cap warfare") equipment drains capacitor energy from the target ship. Both modules and drones are available and come in multiple types:
- **Energy Neutralziers** ("**neuts**") destroy capacitor energy, consuming a large amount from the attacker to nullify a similar amount from the target ship. [*High* slot, short range]
- **Energy Nosferatu** ("**vampires**", "**NOS**") siphon a small amount of energy, transferring it from the target to the attacker (with restrictions). [*High* slot, short range]
- **Energy Neutralizer Drones** - Light, medium, and heavy drones, and a wing of support fighters, based on Amarr combat drones.

Cap warfare modules are fitted into a ship's *High* slot, and both types, Neutralizers and Nosferatu, operate at short range. (By contrast, most **electronic warfare** modules are *Mid* slot modules and operate at mid-range or long-range.) While conventional weapons require a turret or missile launcher *High* slot, a capacitor warfare module has no such requirement and can fit into any *High* slot.

Ships can resist capacitor warfare by fitting modules with Neutralizer Resistance, such as the **Cap Battery**. Also, one ship may transfer capacitor energy to another by using a **Remote Capacitor Transmitter**.

1. # Limitations
Some systems are unaffected by capacitor warfare. Projectile turrets and Missile Launchers do not require capacitor energy to operate. **Shields** continue to function and regenerate without capacitor needs, and subspace engines still function. However, a ship with a fully drained capacitor cannot **warp** or activate **propulsion equipment**, severely limiting range control and escape options.

1. # General principles
Understanding capacitor warfare requires an understanding of capacitor mechanics. Capacitors are a self-recharging resource measured in gigajoules (GJ), with a **capacitor recharge rate** determined both by the specific ship and the percentage level of the capacitor, measured in gigajoules per second (GJ/sec).  The 'peak' recharge rate occurs at 25% capacity, with the recharge rate sharply decreasing below this amount, and more gradually decreasing above it. Therefore, the rate of recharge is lowest when the capacitor is full (100%) or empty (0%). This is the same principle that governs the recharge rate of shields, though the values are slightly different.

The goal of capacitor warfare is to use enough neutralization to overcome the peak recharge rate of the target's capacitor, and while capacitors recharge continuously over time, Neutralizers remove capacitor in single large chunks with every module cycle. As a result, the effectiveness of Neutralizers is often expressed in effective GJ/sec to facilitate easier comparison to the target's recharge rate. Capacitor warfare will have the smallest relative effects at around peak recharge, as the amount of capacitor removed will be countered by the highest recharge rate the target's capacitor is capable of. As a result, it is much more difficult to "break" a target by bringing its capacitor below 25% than it is to keep it at 0% once it gets there. (i.e. it may take 3 Neutralizer modules to bring a target below 25%, but only one Neutralizer module to keep it at close to 0.) As such, the common rule of thumb for Neutralizer-focused ships or fleets is to have *much* higher neutralization potential than the enemy's conceivable recharge rate.

This being said, even without sufficient neutralizers to break a target, neutralizers can still have a meaningful effect on them. A pilot whose ship is hovering at around 30% capacitor needs to start making choices about which capacitor-consuming modules to use or not use, or may need to start using a Cap Booster to keep themselves up. Being forced to choose which modules not to run opens room for mistakes, and may force the target pilot to choose between not performing their role in the fleet, or dying; and Cap Booster charges will eventually run out in a longer fight and result in a slow death by attrition.

Like many other Electronic Warfare modules, Capacitor Warfare modules have both Optimal and Falloff ranges. Using modules outside their Optimal range results in reduced effectiveness. The formula for effectiveness loss is the same as Turret falloff:
- at 100% Optimal + 0% Falloff = 100% Effectiveness
- at 100% Optimal + 100% Falloff = ~50% Effectiveness
- at 100% Optimal + 200% Falloff = ~6% Effectiveness
- at 100% Optimal + 300% Falloff, the module shuts down as the target is considered 'out of range'.

Like weapons, capacitor warfare modules benefit from **overheating**; as an overheated weapon deals more damage-per-second, an overheated capacitor warfare module sucks the opponent dry faster.

1. # Energy Neutralizers
  - Energy Neutralizers** ("**Neuts**", also formerly called **Energy Destabilizers**) are the heavy hitters of capacitor warfare, able to remove large amounts of capacitor and leave an enemy capped out faster than any other capacitor warfare system. However, they also require a large amount of capacitor to activate and have a long cycle time. Energy Neutralizers have relatively short ranges, though this range scales with module size to retain effectiveness on larger hulls.

All neutralizers have a similar set of attributes. The different sizes of neutralizer differ significantly, but for each size tier they are fairly consistent across meta levels.  Aside from fitting considerations, the only attributes that change from meta 0 all the way to commander modules is the range and the amount of energy neutralized.
- Module activation cost is consistent ( for small,  for medium, and  for heavy).  Therefore, at each size, higher meta modules are more efficient: meta 0 modules destabilize as much as their activation cost (100% efficiency), and this efficiency trends up to meta 5 (tech II) and higher modules at 120% efficiency. Module activation costs are reduced by the  skill, which provides 33% increased efficiency at level V.
- Cycle time is also consistent ( for small neuts,  for medium, and  seconds for heavy).
- Optimal range for modules from meta 0 to the highest are: small from ; medium from ; heavy from ; and capital from .
- Faction and Deadspace Neutralizers have increased range, but the same drain amount as T2 variants. Faction Neutralizers have reduced CPU and Powergrid costs; Deadspace Neutralizers have increased Powergrid costs.
- Overheating a neutralizer shortens its cycle time, which means it will drain its target's capacitor faster but (users should remember) also that it will put an increased load on its user's capacitor.

{{#CSS:

.neut-stats td:nth-child(2),
.nos-stats td:nth-child(2)
 {
   text-align: center;
 }

.neut-stats td:nth-last-child(-n+9),
.nos-stats td:nth-last-child(-n+7)
 {
   text-align: right
 }

.neut-stats td:nth-child(4),
.neut-stats td:nth-child(7),
.nos-stats td:nth-child(4)
 {
   color: lightblue;
 }

.neut-stats td:nth-child(5),
.neut-stats td:nth-child(6),
.nos-stats td:nth-child(5),
.nos-stats td:nth-child(6)
 {
   color: lightgreen;
 }

.neut-stats td:nth-child(8),
.nos-stats td:nth-child(7)
 {
   color: red;
 }

}}

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |
| Deadspace |

When activating an Energy Neutralizer on a target, the activation cost will immediately be deducted from the neutralizer's capacitor and the neutralization amount (modified, if in falloff range or if the target has some form of resistance) will be immediately deducted from the target's capacitor.  This will be repeated each cycle time for as long as the neut is activated.

1. # Energy Nosferatu
'Energy Nosferatu (also called "**NOS**" or "**Energy Vampires**") remove small amounts of capacitor from their target and use it to recharge the user's capacitor, and cycle more quickly than Energy Neutralizers. However, Energy Nosferatu are far more restricted in their effectiveness due to the double upside inherent in their use. Energy Nosferatu share the limited range of Energy Neutralizers, and drain much less capacitor. Most importantly, Energy Nosferatu only transfer capacitor when **the user's capacitor is less than the target's capacitor.** This is measured in terms of absolute capacitor amount, *not* capacitor percentage, e.g. a capacitor with 120 GJ of capacitor will always be able to transfer capacitor from a ship with 2000 GJ, regardless of what percentage of each ship's capacitor those amounts represent.

  - Blood Raider** ships have a unique interaction with Energy Nosferatus: Nosferatus used by Blood Raider ships *ignore* the target's capacitor level, and *always* transfer energy. This means that, for a Blood Raider ship, a Nosferatu is functionally both an indefinitely sustainable Neutralizer with a lower strength but a much shorter cycle time, and a Cap Booster that does not consume cap charges. This also means that a Blood Raider-run Nosferatu can be used to test whether or not a target ship's capacitor is dry: that NOS will only start draining 0GJ/cycle if the target *has* 0GJ available.

All Nosferatus have a similar set of attributes.  The different sizes of Nosteratus differ significantly, but for each size tier they are fairly consistent across meta levels.  Aside from fitting consideration, the only attributes that change from meta 0 all the way to commander modules is the range and the amount of energy transferred to the user.
- Cycle time is consistent ( for small NOS,  for medium, and  for heavy).
- Small Nosferatu will transfer from  across the meta levels, medium from , and heavy from .
- Optimal ranges for all the modules from meta 0 to the highest are between: small from ; medium from ; and heavy from .
- As with neutralizers, overheating a Nosferatu module decreases its cycle time. Unlike overheating a neutralizer, this will result in both more energy drained from the target's capacitor, *and* more energy deposited in the user's capacitor.

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |

| gray|* - Last verified: January 2017*}} |
| :--- |
| Tech I |
| Tech I |
| Tech I |
| Tech II |
| Storyline |
| Faction |
| Faction |
| Faction |
| Faction |
| Deadspace |
| Deadspace |
| Deadspace |
| Deadspace |

When within range of a target, and the target's capacitor amount (not percentage) is higher than your cap amount, then an activated Nosferatu acts similarly to a neut. However, the capacitor drain occurs at the *end* of the cycle rather than the beginning, and rather than consuming the user's capacitor to reduce the target's, the energy which is removed from the target's capacitor is added to the user's. A NOS will stay activated as long as the target is in range and pull cap when the cap level condition is met, so there is no downside to keeping a Nosferatu activated at all times. The primary caveat to using Nosferatu is that a NOS is highly likely to be effective when fighting bigger targets, but not likely to work when fighting smaller targets. 

A NOS is easier to effectively employ in a gang situation with multiple targets.  While neuting the main target, a pilot can NOS an alternative target (ideally a bigger ship) to maintain the Nosferatu's effectiveness. Properly employed, this synergy between neuts and NOS is extremely effective.

1. # Energy Neutralizing Drones

  - thumb|200px|Acolyte EV-300 stats**
Light, medium and heavy neutralizing drones employ the same general principles as other drones.

- Strengths
  - Normal drone range mechanics
  - Neutralizer drones have no impact on your cap
  - Quick 6 sec cycle time for all sizes
- Weaknesses
  - Normal drone weaknesses of vulnerability, flight times, inability to overheat, etc.
  - Relatively small portions of cap neutralized

Cycle times are identical (6 seconds) for all three sizes of drones.  The amount neutralized is easy to remember, as it is identical to the drone bandwidth:  for Light,  for Medium, and  for Heavy drones.  Like all other drone-based EWAR, pilot EWAR skills have no effect on the drones. There are no stacking penalties when using Neutralizer Drones.

Accordingly:
- A full flight (5) light drones will neutralize 25 GJ every 6 seconds.  This is roughly 1/2 as effective as 1 small neut.
- A full flight (5) medium drones will neutralize 50 GJ every 6 seconds.  This is roughly 2/3 as effective as 1 medium neut.
- A full flight (5) heavy drones will neutralize 125 GJ every 6 seconds.  This is exactly as effective as 1 meta 0 heavy neut.

1. # Capital Energy Neutralizers
Neutralizers and Nosferatus also exist in Capital sizes, with increased range, strength, and fitting costs to match. However, Capital Neutralizers have a unique feature that sets them apart from other sizes, and also limits their use: Capital Neutralizers have an additional attribute, **Neutralization Signature Resolution**, which has a value of  on all variants. This attribute works similarly to the **Explosion Radius** attribute of Missiles: when the Neutralizer activates, this Signature Resolution value is compared to the target's Signature Radius, and if the target's Sig Radius is less than the neutralizer's Resolution, the neutralizer's strength is reduced based on the ratio of Sig Radius : Sig Resolution. The result of this is that Capital Neutralizers are extremely powerful on-paper, but are only effective against other capital ships, and cannot be meaningfully used against battleships and below. As such, most capital ships that use Neutralizers will fit a Heavy Neutralizer, rather than a Capital-sized variant.

1. # Protection from capacitor warfare
There are four main ways to protect a ship from capacitor warfare:
# Increase Capacitor capacity and regeneration
# Fit a Capacitor Booster to use as an emergency source of cap
# Fit a Nosferatu of your own, to drain back some of the cap you lose
# In a fleet context, use Remote Cap Transmitters to send cap between allied ships (similar to option #2, but more sustainable)
Number 1 is the most common solution in PvE, and the first three are all commonly used together in PvP. There are several modules that can be used to achieve #1:
- Cap Batteries are the most commonly used, as they increase your capacitor capacity (which increases regeneration rate, and also increases the number of neutralizer cycles required to bring you down to 0), but more importantly, they also all provide a percentage resistance to the power of incoming Neutralizers and Nosferatus. This resistance ranges from  based on the battery variation, and the resistance values from multiple batteries do stack (although **Stacking penalties** apply).
- Capacitor Rechargers increase capacitor regeneration rate. Depending on the ship and other fitted modules, they may or may not provide more regeneration than Cap Batteries, so simulate and test to compare.
- Capacitor Power Relays increase capacitor regeneration rate, but reduce the strength of fitted (local) Shield Boosters. This makes them a bad choice for Active Shield Tanked ships, but useful in other cases.
- Power Diagnostic Systems give a modest increase to capacitor regeneration rate and capacity (and several other attributes). The individual bonuses they give are small, but they can sometimes be useful on Shield-tanked ships because they give so many different small bonuses.
- Capacitor Control Circuit Rigs increase capacitor regeneration rate; Semiconductor Memory Cell rigs increase capacitor capacity. CCC Rigs are generally preferred, as their bonus to regeneration is usually more effective than SMC Rigs' bonus to capacity.
- **Strategic Cruisers**' Augmented Reactor subsystems give significant bonuses to either capacitor capacity or regeneration, and up to  resistance (based on Core Systems skill levels) to incoming Neutralizers and Nosferatus.
- Capacitor Flux Coils should **** be used for capacitor warfare resistance, as while they significantly increase regeneration speed they also significantly *reduce* capacitor capacity, thus making you more vulnerable to having your capacitor quickly dropped to 0.

1. # Skills
Prerequisite skills:
- is the prerequisite skill for Energy Neutralizers and Nosferatus. It's the only skill that directly impacts the effectiveness of capacitor warfare modules; however, it only affects neuts. It reduces the activation cost of all neuts by 5% per level which has excellent results on efficiency. At level V, a Tech II heavy neut will only require 375 GJ per cycle to neutralize 600 GJ (160% efficiency). Unfortunately, this has no positive effect on NOS or drones as they do not have a capacitor activation cost.
- is the prerequisite skill for Neutralizer Drones (and all other electronic warfare drones).

The better a ship's capacitor, the more effectively it can conduct capacitor warfare.  Therefore both  and  are extremely important skills and should be trained to V for serious capacitor warfare users.

All the supporting capacitor management skills as listed will assist in getting pilots through a fight with more capacitor available for capacitor warfare.  Depending on preference, ship types, and fits, the relative importance of each skill will change, but each can be considered a good investment of SP.

1. # Implants
Talisman **implants**, the Blood Raider pirate set, directly enhance capacitor warfare by reducing the duration of modules requiring .  The complete high-grade set (slots 1-6) will have an overall effect of -38.12% cycle time.  This is of course a huge increase in the amount of GJ/sec drained.  A max skill Curse with a full Talisman set will neutralize 40.4 GJ per sec with a single meta 4+ medium neut.

Low-Grade: total effect -26.94% 

| Name | Effect | Set Effect | Attribute |
| :--- | :--- | :--- | :--- |
| Alpha | 1% reduction of duration | 10% effect on bonus of the set | +2 Perception |
| Bravo | 2% reduction of duration | 10% effect on bonus of the set | +2 Memory |
| Gamma | 3% reduction of duration | 10% effect on bonus of the set | +2 Willpower |
| Delta | 4% reduction of duration | 10% effect on bonus of the set | +2 Intelligence |
| Epsilon | 5% reduction of duration | 10% effect on bonus of the set | +2 Charisma |
| Omega | 25% effect on bonus of the set |  |  |

High-Grade: total effect -38.12%

| Name | Effect | Set Effect | Attribute |
| :--- | :--- | :--- | :--- |
| Alpha | 1% reduction of duration | 15% effect on bonus of the set | +3 Perception |
| Bravo | 2% reduction of duration | 15% effect on bonus of the set | +3 Memory |
| Gamma | 3% reduction of duration | 15% effect on bonus of the set | +3 Willpower |
| Delta | 4% reduction of duration | 15% effect on bonus of the set | +3 Intelligence |
| Epsilon | 5% reduction of duration | 15% effect on bonus of the set | +3 Charisma |
| Omega | 50% effect on bonus of the set |  |  |

In addition, the following hardwirings are worth considering in addition to or in place of the Talisman set:

Slot 6
- Engineering - 'Squire' Energy Systems Operation EO-6##, +(1-6)% faster capacitor recharge. Most pilots who use cap warfare, especially on dedicated ships, will use cap boosters. As such, cap recharge rate becomes a minor factor in cap warfare.
Slot 7
- Engineering - 'Squire' Energy Emission Systems ES-7##: -(1-6)% capacitor usage by cap warfare modules and energy transmitters. This implant has a significant impact on the capacitor usage of cap warfare modules. It however stacks with the Egress Port Maximizer rig.
Slot 8
- Engineering - 'Squire' Energy Management EM-8##: +(1-6)% capacitor size. This implant is more useful than the EO-6##, but less than the ES-7##. A bigger capacitor is always useful.

1. # Boosters
When approaching **boosters** from a capacitor warfare perspective, Mindflood is the drug of choice.  This booster increases capacitor by a percentage that stacks on top of all other modifiers without stacking penalty.

| Type | Increases Cap by | Side Effect Chance | Side Effect Strength |
| :--- | :--- | :--- | :--- |
| Synth | 6% | 0% | 0% |
| Standard | 10% | 20% | 20% |
| Improved | 15% | 30% | 25% |
| Strong | 20% | 40% | 30% |

The potential side effects are:
- Shield Boost Amount
- Armor Repair Amount
- Turret Optimal Range Penalty
- Missile Explosion Cloud Penalty

On drone boats like the , , and , the impact of these possible effects is usually minimal, as DPS usually comes from drones and many popular fits are buffer tanked only.  The worst penalty is potentially the armor repair amount for a solo fit Sentinel or Pilgrim, although there are Curse fits that use missile launchers to up DPS.  

Blood Raider ships using lasers and cap warfare mods may have more of a trade-off to consider.  Individual pilots will have different risk assessments, but once the applicable skills have been trained ( and ), the risk and impact of side effects can be greatly reduced.

1. # Rigs
The Egress Port Maximizer rigs decrease the capacitor use of all energy weapon modules. The Tech I rig reduces activation cost by 15%, and the Tech II by 20%. More than one rig can be used, but because of stacking penalties, the effects get lower as more rigs are added.

1. # Capacitor warfare and PvE
Certain **NPC Factions** use Energy Neutralizers as their choice in electronic warfare. This means that capacitor warfare resistance is often not important in PvE, however for fighting certain factions (Blood Raiders, Sleepers, Triglavians, and the Amarr Empire in particular) it can become *very* important.

The use of Energy Neutralizers have an odd history in PvE. Traditionally, Neutralizers have had no effect on NPC ships, as most NPC ships do not use Capacitor to function; and Nosferatus have been of questionable use at best as NPCs had small capacitors and poor regeneration so using a Nosferatu as a backup energy source was generally ineffective. This applies to most common NPC ships found throughout all levels of K-Space and J-Space.

However, in the years since the Into The Abyss expansion (May, 2018), that story has changed. All NPC ships which have been introduced since the creation of **Abyssal Deadspace**, including the ships which are found inside the Abyss and all ships involved in the **Triglavian Invasion**, ***do*** use their Capacitors to power their electronic warfare and local and remote repair abilities, and thus are vulnerable to having energy neutralizers shut them down. (It is not known whether or not they also use capacitor to power their weapons or high-speed 'chase' mode.) These ships can also be used as Nosferatu targets for emergency capacitor sustain, as they themselves frequently bring neutralizers to drain players who would fight them.

1. # Capacitor Warfare and PvP Ships
The following ships have some bonus related to Energy Neutralizers and Energy Nosferatu for range, drain amount, or efficiency:

  1. # Frigates
- (Pirate faction frigate)
  - 15% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level
- (**Electronic Attack Ship**)
  - 20% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - 80% bonus to Energy Nosferatu and Energy Neutralizer optimal range per level of
  - 40% bonus to Energy Nosferatu and Energy Neutralizer falloff range per level of
- ,
  - 50% reduction to Energy Neutralizer capacitor cost

  1. # Destroyers
- (Destroyer)
  - 20% bonus to Energy Nosferatu and Energy Neutralizer optimal range per level of
  - 10% bonus to Energy Nosferatu and Energy Neutralizer falloff range per level of
- ,
  - 50% reduction to Energy Neutralizer capacitor cost

  1. # Cruisers
- (Pirate faction cruiser)
  - 15% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level
- (**Recon Ship**)
  - 10% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - 20% bonus to Energy Nosferatu and Energy Neutralizer optimal range per level of
  - 10% bonus to Energy Nosferatu and Energy Neutralizer falloff range per level of
- (**Recon Ship**)
  - 40% bonus to Energy Nosferatu and Energy Neutralizer optimal range per level of
  - 20% bonus to Energy Nosferatu and Energy Neutralizer falloff range per level of
  - 20% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
- (**Strategic Cruiser**, equipped with Energy Parasitic Complex Electronic Subsystem)
  - 10% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - 10% bonus to the benefits of overheating Energy Nosferatu and Energy Neutralizer modules per level of
- , , ,
  - 50% reduction to Energy Neutralizer capacitor cost

  1. # Battlecruisers
- 
  - 50% reduction to Energy Neutralizer capacitor cost

  1. # Battleships
- (Battleship)
  - 10% bonus to Energy Nosferatu and Energy Neutralizer optimal range per level of
  - 5% bonus to Energy Nosferatu and Energy Neutralizer falloff range per level of
- (Pirate faction battleship)
  - 15% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level
- 
  - 50% reduction to Energy Neutralizer capacitor cost

  1. # Capital Ships
- 
  - 15% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level
- 
  - 50% reduction to Energy Neutralizer capacitor cost
- 
  - 20% bonus to Energy Nosferatu drain amount, optimal range, and falloff range, per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level
- 
  - 15% bonus to Energy Nosferatu and Energy Neutralizer drain amount per level of
  - Energy Nosferatus will drain energy from targets regardless of capacitor level

1. # Unbonused ships
A number of ships fitted for cap warfare are not bonused for it. The  and the  are well known examples of ships with no bonus to cap warfare range or transfer amount which have been used with great effect. While any ship could conceivably be fitted with a neutralizer or a nos, the following elements help make an unbonused ship suitable for cap warfare:
- Free high slots. The ship needs a place to fit the modules.
- Drone capacity. When using high slots for neuts, pilots have to rely on drones for damage. A drone damage bonus is also helpful.
- Powergrid. Neuts cost a lot of powergrid to install.
- Capacitor size. Neuts cost a lot of cap to run, and a ship with a big capacitor will be easier to fight with.
- Tank. Neutralizers and Nosferatus have short ranges, so pilots will need to be close to their target, and will thus be more vulnerable to damage.
- Range. In an unbonused ship, you need to be be close to your target to use cap warfare modules. Don't mix cap warfare modules with long range modules such as ewar.

  1. # Frigates
- The  is often flown with a utility cap warfare module.
- Many solo fits for frigates use a small cap wafare module.

  1. # Destroyers
- Except for the  (see above), destroyers are not usually used for cap warfare.

  1. # Cruisers
- The  is usually flown with cap warfare modules. Its tank is not that great but it has a nice drone damage bonus.
- The  can be used as a surprise neuting cruiser. It won't have any dps to speak of, but can fit a point, a scram or a web while being cap stable and have more than 50K EHP.
- The  is often flown with a utility cap warfare module.
- The , when used as a covert hunting ship (usually in **Wormhole space**), is often fit with 3 Neutralizers (alongside its probe launcher, cloak, and large Drone bay).

  1. # Battlecruisers
- The  can be effectively fitted with capacitor warfare modules in its high slots. It has a good tank, capacitor and with good drone skills a reasonable amount of dps.
- Brawling **22px|link=|Minmatar****Hurricane**s are often flown with a utility cap warfare module.

  1. # Battleships
- The  is often used a cap warfare ship. Its great drone bonus makes it ideal as a close range cap warfare ship.
- Brawling **22px|link=|Minmatar****Typhoon**s are often flown with a utility cap warfare module.
- **22px|link=|Minmatar****Tempest**s are often flown with a utility cap warfare module.
