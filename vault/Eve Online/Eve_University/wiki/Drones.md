---
title: "Drones"
url: "https://wiki.eveuniversity.org/Drones"
pageid: 220
source: "EVE University Wiki"
categories: ["Candidates for verification", "Drones", "Needing updates", "Weapons"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Drones

- Drones** are semi-autonomous vehicles launched from ships and designed to augment the launching ship's capabilities. All four races use drones to a greater or lesser degree, so many ships, especially larger ships, will have drone capabilities.

While most drones are used as support, some ships use drones as their primary way of dealing damage. In addition, there are drones for specialized uses: such as **mining**, **electronic warfare**, and **logistics**.

Compared to the other combat **weapons systems** in EVE, drones provide a great deal of flexibility. On the other hand, drones need to travel to their targets before applying their damage, and they can be destroyed by enemy fire.

1. # Drone basics

If you undock with drones in your drone bay, a new window for controlling drones will appear on your screen. Via this window, you can launch drones from your drone bay, give commands to them once they are in space, and recover them back into your drone bay.

This window also shows the active status of any drones you currently have in space. These are listed in the last folder. If any of those drones are damaged, the three little bars to the right of the drone will turn red - indicating hull, armor and shield … in that order.

Drones can be grouped through the drone control window. This makes controlling drones easier, as you can give a command to the entire group. To move a drone in or out of a group, right-click on the drone, or drag it in or out of the group.

Create groups of drones that you intend to launch and use together; usually, this means groups of five identical drones, but in some cases, you may want to create groups with a mix of drones. Only drones of the same type may be grouped (you cannot, for example, put e-war and combat drones in the same group.)

You can delete unused drone groups by right-clicking in your drone control window and selecting "Delete group".

Drones have built-in weapons that don't need to reload. If damaged, a drone's shields will slowly regenerate on their own, but damage to its armor and hull will need to be repaired (e.g. by using the repair services at a station).

Drones are capable of serving many different roles and exist in many different sizes. There are five general categories:
- **Combat drones**
> Targeting enemy ships, these apply the **basic types of damage**.
- **Electronic warfare and combat utility drones**
> Targeting enemy ships, these **weaken and interfere** with the enemy.
- **Logistics drones**
> Targeting friendly players, these provide aid to ships in a fleet.
- **Salvage drones**
> These target wrecks for **salvage**.
- **Mining drones**
> These target asteroids or ice and **mine them** for resources.

Details on the characteristics of individual drone types are shown below in **Drone Type Details**. A discussion of the uses of these drones in game can be found in **Drone mechanics**.

  1. # Drone bay

A ship must have a drone bay to use drones. You can find out if a ship has a drone bay, and how big it is, by looking at the Attributes tab in its Show Info window. If it has a drone bay, it will tell you the drone bay's capacity in cubic meters (). The size of a ship's drone bay determines how many drones you can carry with you, ready to be launched into space; larger and more powerful drones take up more space in your drone bay.

{{example|The **Tristan** has a 40 drone bay, which means it can carry up to eight light drones (which take up 5 each), or four medium drones (10 each), or a combination of the two (e.g. two medium and four light drones).}}

The size of your ship's drone bay is fixed and cannot be enlarged using modules or skills. Only drones can be carried in a drone bay; it cannot be used to carry other cargo. While you can carry drones in your cargo bay, you can only use them if they are in the drone bay. You can only move drones in or out of your drone bay while docked at a station, or by using a ship/structure with a fitting service (e.g. a **Mobile Depot** or a **Capital Ship**).

  1. # Bandwidth
The other important ship attribute is its **bandwidth**. This is the ship's ability to control drones in space and is measured in Mbit/sec. You can only deploy as many drones as you have available bandwidth on your ship, and bigger drones require more bandwidth. Your ship's bandwidth is fixed and cannot be increased by skills or modules (but it can be decreased if a **Warp Core Stabilizer** is fitted).

Many ships (and especially **dedicated drone ships**) can carry many more drones in their drone bays than they can deploy at once; this allows them to selectively deploy different types of drones, or to replace drones that are destroyed in combat. With the exception of **fighters** (which are only used by capital ships) and special limited edition drones, a drone's bandwidth requirements (in Mbit/sec) is always the same number as its volume (in).

However, irrespective of your ship's bandwidth, you can only have as many drones in space at once as you have levels in the  skill which allows up to 5 drones at level V. (The only exception to this limit is the very rare **Guardian-Vexor** cruiser.) This means that with high bandwidth you might be able to deploy five heavy or five light drones, while with lower bandwidth you may only be able to put out five of the light ones.

{{example|The Tristan's bandwidth is 25&nbsp;Mbit/s, allowing it to deploy, at most, five light drones in space at once (they need 5&nbsp;Mbit/s each), but only if the pilot has trained the  skill to level V. If it's carrying a mixture of light and medium drones, it could deploy up to two medium (10&nbsp;Mbit/s each) and one light drone at once, assuming the pilot has trained Drones III.}}

  1. # Control range
You can only command a drone to attack/repair/mine a target if that target is within a certain range of your ship; this range is known as the "drone control range". By default, your control range is 20km, which means that you can only order a drone to attack an enemy ship if it's within 20km of your ship. This range can be extended by training:
- : Increases drone control range by 5km per skill level.
- : Increases drone control range by 3km per skill level.

Note that in order to command a drone to attack/repair/mine a specific target, you'll need to have a target lock on it, which can limit the benefit of the control range. If the command can be given without having a target (such as for salvage drones), the drones will seek out applicable targets within the entire command zone regardless of targeting capacity.

With Drone Avionics and Advanced Drone Avionics at level V, your drone control range is 60km. To increase it further, you can install modules and rigs on your ship:
- **Drone Link Augmentor** module: A high-slot module, that increases drone control range by 20km (24km for the Tech 2 module)
- **Drone Control Range Augmentor** rig: Increases drone control range by 15km (20km for the Tech 2 rig)

Once you've ordered them to attack a target, your drones will pursue that target even outside your drone control range, whether or not you continue to have that target locked.

Drones will shut down if they exceed 500km distance from their host ship, or if their host ship activates its warp drive. See **Abandoned Drones**, below, for your options if you lose touch with your drones.

  1. # Navigation and Distance
Almost all drones (except the stationary sentry drones) have a built-in **microwarp drive (MWD)**, which allows them to travel quickly to engage a target. Once they arrive near their target, they shut down their MWD, orbit the target, and fire their weapons. This means that drones have to travel to the target and then stay within range of it in order to apply their damage. In practice, this means that drones will have difficulty against faster, more agile targets, as even though they may be able to catch them thanks to their MWD, they may not be able to stay within weapons range for long at their non-MWD speed. Larger drones in particular are almost useless against fast frigates for this reason.

No skill or module affects the orbit speed of drones.

  1. # Direct Drone Commands
You can give commands to each drone individually, or to all of your drones at once. If you issue a command like "attack that target", the drone will fly to the target you have selected and start firing on it once it's within weapons range, *but you cannot exercise any finer control than that*.

You can give a drone commands either by right-clicking it, selecting it in the **overview** and using the overview buttons or by using a radial menu (by long-clicking). You can also give "launch" and "return to drone bay" commands by dragging drones in the drone control window from the "drones in bay" to the "drones in space" folder.

Additionally, you can use keyboard shortcuts for many of these commands. These can be changed in the **Game Settings** window.

| Command | Shortcut |
| :--- | :--- |
| All Drones: Engage | F |
| All Drones: Return and Orbit | Shift-Alt-R |
| All Drones: Return to Drone Bay | Shift-R |
| Drone Settings: Toggle Aggressive/Passive | (None) |
| Drone Settings: Toggle Focus Fire | (None) |
| Fighter Settings: Toggle Attack and Follow | (None) |
| Launch Drones | Shift-F |
| Reconnect To Lost Drones | (None) |

You can give any drones these generic commands:
- ****: Launch the selected drone(s) from your drone bay into space.
- ****: Order your drone(s) to fly back to your ship and orbit it, awaiting further commands.
- ****: **Abandons** your drones in space. While normally you would want to order your drones to return to your drone bay, in some situations (particularly PvP) this can take too long, and you may want to abandon your current drones in order to launch a different drone type which is better suited to engaging your current enemy.
- ****: Order your drone(s) in space to fly back to your ship and land in your ship's drone bay.
- ****: If your drone has become disabled in space (i.e. is no longer responding to commands), you can fly your ship to it and, once you are nearby (2500m), scoop the drone into your ship's drone bay. You can also scoop up drones abandoned by other players (e.g. their ship was destroyed, or they warped off without docking their drones).
- ****: Similar to the "Scoop to Drone Bay" command, but scoops the drone to your cargo bay instead of your drone bay. This is useful if your drone bay is already full.

You can give the following commands to drones that have the associated abilities.
- ****: Orders your drones to engage (attack, repair, jam, mine, etc) the target you have currently locked. They will fly to your target, attempt to orbit it, and engage it. Note that your drones will engage whatever you order them to, including your other drones or your fleetmates.
- ****: If you give this command your drones will assist a member of your fleet, and will engage whatever target they are attacking.
- ****: Similar to the "Assist" command, except that your drones will engage whatever ships attacks the fleet member you order your drones to guard.
- ****: Orders your mining drone(s) to mine the asteroid you have targeted for one cycle (60 seconds), then return to your ship, drop the mined ore off in your cargo or mining bay. They will immediately return to the asteroid after they have dropped off their ore at your ship and continue mining. You can redirect them to a different asteroid at any time.
- ****: Orders your salvage drone(s) to salvage the wreck you have targeted; if you give this command without anything targeted, your salvage drones will automatically salvage every wreck *belonging to you* within your drone control range. To salvage wrecks belonging to other players (coloured yellow on the **overview**), you need to manually target them and give the "Salvage" command.
 
Once you give a command to your drones, they start carrying it out in the next **server tick**. In practice, this means that your drones may take 1-2 seconds to respond after you give a command.

  1. # Default behavior settings

The  drones' default behavior can be set through the menu that appears when clicking the cog icon on the "Drones in space" folder bar. The icon becomes visible when hovering over the folder bar.

****:
> ; Disabled : Drones will not automatically attack hostile ships, but will stay in orbit around the ship until given a specific command. This is the default mode, and it is recommended to keep drones in this mode for PvE (particularly when running missions, as you want to control which rats you aggro) and for most PvP.
> ; Enabled : Drones will automatically attack any entity which shows aggression to them or the ship (using the same targeting logic as **auto-targeting missiles**). Note that they will only react to hostiles which begin aggressing <em>after</em> the drones were launched.

Enabling this mode can be useful when being **jammed**, as it gives a chance to attack <em>something</em> at least. However, as drones are fairly dumb in their target selection, in almost every other situation you want to command the drones manually as drones may inadvertently attack something you would rather not.

> :;
> :: Only applies when Auto Attack is enabled.
> ::; Disabled : Every drone will decide its own target.
> ::; Enabled : All drones attack a single target. There are almost no situations in which this box should not be checked.

****:

> Only applies to fighter and fighter-bomber drones (as used by **capital ships**). As these drones have built-in warp drives, they can follow targets even if they warp away - to prevent this (and keep the drones with you), uncheck the box. Disabling the "attack and follow" setting is a good idea if you suspect that the target may warp to a **POS** and if the fighters follow, they will likely be destroyed by the POS' defenses.

  1. # Abandoned drones
If you warp away while your drones are in space, if your ship is destroyed, or if you give the "abandon" command, your drones will become inactive and remain stationary in space. At this point, anyone can recover them (by flying to them and using the "scoop to drone bay" or "scoop to cargo bay" command). You can also reconnect with any drones which you have personally abandoned by right-clicking on your ship (or the capacitor on your HUD) and selecting "reconnect to lost drones"; this works as long as the drones are nearby, on the same **grid**. It's not possible to use a tractor beam on abandoned drones.

If you've warped away without recalling your drones, but cannot directly return to the location (e.g. if you left your drones in a mission **deadspace** pocket, but you completed the mission, and therefore no longer have the bookmark for the location), you can **probe scan** your lost drones using combat probes.

  1. # Damaged drones

Your drones can take shield, armor, and structure damage during a fight (just like your ship). Their shields will regenerate slowly, whether the drone is in space or in your drone bay (at the same rate), but armor and hull damage need to be repaired. When in combat with drones, keep an eye on your drone's health through the drone control window, and when a drone starts taking armor damage, recall it to your drone bay and launch a fresh drone (if you have spares) - it's much cheaper to repair drones than to replace them.

If you dock at a station with repair facilities, you can easily repair all damaged drones at the cost of some ISK. Also, they get repaired automatically at no cost while your ship is **tethered** to a **Citadel**.

If you don't have access to a station, you can repair drones in space by using remote armor and hull repair modules, or by using logistics drones. If you plan on being away from stations for a while, it may be a good idea to carry small armor and hull repair modules with you, and fit these modules to your ship (using a **mobile depot**) in between combat encounters to repair your drones. Light armor and hull logistics drones are also an option if you have space in your drone bay, but keep in mind that they repair very slowly - a single light armor repair drone takes about 3 minutes to fully repair a damaged heavy drone, while a small remote armor repair module can do it in about 30 seconds.

1. # Drone-centric factions
Certain factions offer ships that are focused on drones. These ships are most often used as "**Drone Carriers**" by players who are using drones as their primary weapons.
 

| Empire factions |
| :--- |
|  |
|  |
| Other factions |
| :--- |
|  |
|  |

1. # Drone type details
Drones are capable of serving many different roles and exist in many different sizes. There are seventeen different groups of drones, which can be divided into five categories:

**Combat drones**:
> These are the most common drones and are (as the name suggests) used to damage and destroy enemy ships. There are six different types of combat drone:
> * ***', ***', and **** drones, generally for use on frigate, cruiser, and battleship-sized ships, respectively.
> * **** drones, which act as stationary, long-range turrets.

**Electronic warfare and combat utility drones**:
> These drones impair an enemy ship using **electronic warfare** or similar methods. There are drones for each of the four methods of electronic warfare: ***' (TD), ***' (ECM), ***' (SD), and ***' (TP). Additionally, there are drones that drain an enemy's capacitor (***'), or reduce a ship's speed (***').

**Logistics drones**:
> These drones assist friendly ships by repairing their ***', ***', or ****.

**Salvage drones**:
> These drones are used to ****.

**Mining drones**:
> These drones **** for resources.

  1. # Combat drones

Combat drones come in four types:

      - :
- Use 5 space and 5&nbsp;Mbit/sec bandwidth
- Move and track targets very quickly
- Are the best drones to use against frigates and destroyers

      - :
- Use 10 space and 10&nbsp;Mbit/sec bandwidth
- Move and track moderately quickly
- Are the best drones to use against cruisers, and are also good against battlecruisers

      - :
- Use 25 space and 25&nbsp;Mbit/sec bandwidth
- Move and track slowly, but do lots of damage
- Are good against battleships, and can handle battlecruisers

      - :
- Use 25 space and 25&nbsp;Mbit/sec bandwidth
- Do not move in space
- Can hit targets at long ranges, but have poor tracking, and so will have difficulty against close or fast targets
- Most effective against battleships and battlecruisers, but can also hit smaller targets if they are far enough away

Each race has its own light, medium, heavy, and sentry drones, and they each do one **damage type** (for instance, all Amarr drones do EM damage, while all Caldari drones do kinetic damage).

  1. ### Light, medium and heavy drones

These are the types of drones people first think of when they hear "drones". They are mobile platforms that fly to the target and shoot them once they get close. As long as the target is within the drone control range they can engage. Though travel time may be a problem at long ranges, especially with heavy drones.

The faction variants do not just deal with different damage types.
- Minmatar drones are the fastest drones (50% faster than Gallente drones with MWD on), and so excel at chasing fast ships. However, they do the lowest damage.
- Gallente drones do the most damage (23% more than Minmatar drones), but are the slowest.
- Amarr and Caldari drones fall between Gallente and Minmatar drones in terms of damage and speed (Caldari drones do a little less damage than Gallente drones, but are a bit faster; Amarr drones do a little more damage than Minmatar drones but are a bit slower). Additionally, these drones orbit a little further away from their targets, making them apply their damage more consistently, and are a little tougher (+25% more hit points, compared with Minmatar and Gallente drones).

Therefore, the four race's drones represent a sliding scale between damage and speed (the percentages in the table below are relative to the worst-performing drone family). Note that the table lists two values for speed: the speed with MWD on (when the drones are chasing a target), and the orbital speed with MWD off (when the drones are orbiting and attacking a target).

| ! colspan=2 | Damage
! colspan=4 | Faction comparison |
| :--- |
| Faction | Light | Medium | Heavy | Prim | *Sec | DPS | Speed |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 70px|link=|Gallente Federation]] | 60px]]Hobgoblin | 60px]]Hammerhead | 60px]]Ogre | 32px|link=|Thermal damage]] Thermal | 32px|link=|Kinetic damage]] Kinetic |  | +23% |
| 70px|link=|Caldari State]] | 60px]]Hornet | 60px]]Vespa | 60px]]Wasp | 32px|link=|Kinetic damage]] Kinetic | 32px|link=|Thermal damage]] Thermal | +15% | +13%(+13%) |
| 70px|link=|Amarr Empire]] | 60px]]Acolyte | 60px]]Infiltrator | 60px]]Praetor | 32px|link=|EM damage]] EM | 32px|link=|Thermal damage]] Thermal | +8% | +37%(+26%) |
| 70px|link=|Minmatar Republic]] | 60px]]Warrior | 60px]]Valkyrie | 60px]]Berserker | 32px|link=|Explosive damage]] Explosive | 32px|link=|Kinetic damage]] Kinetic | +50%(+36%) |  |
| All drones deal the primary damage type.* 'Integrated' and 'Augmented' drones deal a mix of the primary and secondary damage types. |  |  |  |  |  |  |  |

Please note that you can hover over the titles for an explanation of the terms and units.

| + **Drone attributes**
! Faction
! Drone
! DPS
! MWD Speed
! Orbit
! Tracking
! Weapon range
! EHP |
| :--- |
| Amarr |
| Caldari |
| Gallente |
| Minmatar |
| &nbsp; |
| Amarr |
| Caldari |
| Gallente |
| Minmatar |
| &nbsp; |
| Amarr |
| Caldari |
| Gallente |
| Minmatar |
| &nbsp; |
| Gecko |
| 'Subverted' JVN-UC49 |
| Hellhound I |

|  +20%
| +20% 
| +20% 
| (Size) Drone Operation V(Race) Drone Specialization I
|-
| 'Augmented'
| +34% to +42%
</references>

  1. ## Sentry Drones
Sentries are immobile drones that serve as stationary gun platforms. They are carried in a ship's drone bay and launched as needed. However, they cannot move and must be picked up physically at the conclusion of an engagement.

At the same size (25) and bandwidth (25Mbit/sec) as heavy drones, sentries are powerful, long range damage dealers. Their immobility and somewhat low tracking speeds makes them most effective against slower, larger targets, and generally, they are deployed from battleships or similar combat vessels.

Sentry drones begin with approximately 2800 HP of defense (shields, armor, structure). They are incapacitated after being 75% damaged.

Although each type of sentry drone does the damage typical of its racial affiliation, drone choice often has to do with relative damage, range, and tracking. These are summarized here, with the detailed numerical data shown next.

    - Notes***
- The Warden has the longest range. Targets are generally drawn straight towards it from far away, which offsets its slow tracking and smaller damage factor.
- The short-ranged Garde has the fastest tracking and damage factor. This makes it more effective than the others as a close defense.
- The Bouncer and Curator are in the middle and somewhat comparable; the Curator has a higher tracking speed and slightly higher damage factor, while the Bouncer has a longer range.

| + Sentry Drones: Comparison |
| :--- |
| Bouncer |
| Curator |
| Garde |
| Warden |

| + Sentry Drones Attributes*+ Shows T2 values if different* |
| :--- |
|  Bouncer |
|  Curator |
|  Garde |
|  Warden |

Like the light-heavy drones, the sentry drones also have faction variants. Though no 'integrated' or 'augmented' sentries exist as only the navy variants are available.
- T2 drones do the same base damage as T1s. However, they have longer range and better tracking.
- T2 sentry drones gain additional damage bonus from the trained racial drone specialization skill level.
- Faction variants do the same damage as T1 and T2 drones. They have the same range as T2 sentry drones, but higher tracking speeds and are stronger defensively. T2 drones are boosted by the racial drone specialization skill; faction drones are not.

| Variant | DPS | Range | Tracking | EHP | Skills |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Tech 1 | Sentry Drone Operation I |  |  |  |  |
| Faction | Same | 24px|link=]] +20% | 24px|link=]] +26% | 24px|link=]] +80% | Sentry  Drone Operation I |
| Tech 2 | +2% to +10% | 24px|link=]] +20% | 24px|link=]] +20% | 24px|link=]] +20% | Sentry Drone Operation V(Race) Drone Specialization I |

, respectively.

Energy neutralizing drones are occasionally used to cap out tackle frigates or to keep a neuted target at zero capacitor.

Just like EW drones, these drones require  and the EW skill .

| + Energy neutralizing drones |
| :--- |
| Drone | Capacitor neutralized |
| :--- | :--- |
| Acolyte EV-300 | 5 GJ |
| Infiltrator EV-600 | 10 GJ |
| Praetor EV-900 | 25 GJ |

| 1,100/25
| 80
| 175 m/s
|}

| 1,100/25
| 310 s
| 90 m/s
|}

  1. # Mutated (Abyssal) Drones

Mutated drones are created using Abyssal Exigent Mutaplasmids. These are acquired either from Triglavian Bioadaptive Caches found in **Abyssal Deadspace** or in the wrecks of Invading Precursors found in **Triglavian Invasion** systems. Mutaplasmids are also tradable on the market. 

The process of combining a mutaplasmid and an existing T1, T2, or Faction combat drone "mutates" it into a unique Abyssal drone with the original drone's stats randomly modified (for better or worse). The new drone will have the word Mutated inserted into its name such as Sentry Mutated Drone, and it will have unique stats and thus cannot be traded on the Market (you can trade them via Contracts etc.)

There exist separate mutaplasmids for each drone type and size and there are different ones depending on which stats you want to improve. "Exigent Sentry Drone Firepower Mutaplasmid" as an example that increases the damage stat. The effects that the mutaplasmid will have on the drone are described in its info. It will specify one or more stats that will be improved (by 0%-20% as an example) and it will alter each of the remaining stats (by -30% to +15% for example, but it varies by mutaplasmid and stat). Each stat change appears to be random and independent. By choosing the appropriate mutaplasmid you can thus guarantee that the stat(s) it primarily targets will go up (maybe not by much), but the rest of the stats are likely to decrease on average. You could, of course, get lucky and end up with a very powerful and valuable drone. A table of possible attribute changes is below.

| -
! Attribute !! Falloff !! HP !! Damage !! Speed !! Optimal !! Tracking |
| :--- |
| Durability |
| green |
| Firepower |
| green |
| Navigation |
| green |
| Projection |
| green |

You perform a mutation by right clicking the mutaplasmid and activating it. This produces a window where you can drop a drone of the appropriate type at which point it will show you the possible range for every stat after it is mutated. Once you commit to the mutation it will go through an animated sequence of rolling each stat change one by one. The mutaplasmid and the input drone are consumed by the process. The mutated drone gets a new icon, and its altered info window Attributes will show red or green with a tooltip to show you where in the probability range it rolled, and a new large tooltip will appear any time you mouse over any mutated drone icon that shows its complete information including the original drone type, and red/green bars that clearly indicate how good or bad the mutation changes are. This is also visible when looking at the items in Contracts etc.

Creating a mutated drone does not require any skills (thus making "drone gambling" a potentially viable Alpha activity) but using one will require Omega clone status and , which in turn requires all four of the main faction Drone Specialization skills at I, and Drones V. Total cost for all those skill books is roughly 100M ISK. The Mutated Drone Specialization provides a 2% damage boost per level for all mutated drones.

You can't use a mutaplasmid on an already Mutated drone, so if you don't like the new stats you get you'll need another drone and another mutaplasmid to try again.

A Gecko, Hellhound I, Aralez, Civlian Hobgoblin, or 'Subverted' JVN-UC49 cannot be mutated.

1. # Skills

  - Basic skills:**
- : Allows you to operate 1 drone per level (up to 5 at level V). This is the foundation skill of any drone pilot, and should be trained to at least level III as a top priority, and to level V soon after (at latest when you start flying ships with 25 drone bays or larger).

  - Combat drone skills:**
These skills allow you to use light, medium, heavy, and sentry combat drones, respectively. Level V is needed for Tech 2 and 'Augmented' drones; all others only need level I. Additionally, these skills increase the damage of their respective drone group by 5% per level. Note that you don't need any skills to load drones into your drone bay; you only need the skills to launch and control them.
- . Requires .
- . Requires .
- . Requires .
- . Requires , , and .

  - Improved drone performance skills:**
These are the "drone support skills", which improve the performance of your drones. Nearly every skill requires  to level IV or V.
- : Increases your drones' damage (and mining yield for mining drones) by 10% per level. Train this to level IV quickly to make your drones much more effective (level IV is the equivalent of having two extra drones in space); the long train to level V is worth it if you're specializing in drones, or as a prerequisite for capital ship drones.
- : Increases the shield, armor, and structure hit points (HP) of your drones by 5% per level. Useful to make (particularly your more expensive) drones live longer but it is not a high-priority skill.
- : Increases your drone control range by 5km per skill level, and allows you to use Drone Link Augmentor modules (which increase your drone control range even further). Training this skill is vital for sentry drone users, and moderately useful for other combat drones. It's less useful for salvage and mining drones, due to their need to return to the owner periodically.
- : In addition to unlocking EW drones (see below), this skill also increases your drone control range by 3km per skill level.
- : Increases your drones' optimal range (but not their falloff) by 5% per level, and allows you to use Omnidirectional Tracking Link and Omnidirectional Tracking Enhancer modules (which boost drone optimal range and tracking). This skill is vital for sentry drones but less important for other drones.
- : Increases your drone's microwarpdrive speed by 5% per level, and allows you to use Drone Navigation Computer modules (which increase it even further). This skill is very important for users of heavy drones (and of no small benefit to light and medium drones). Also useful for most other types of drones (except Sentry drones)

  - Racial drone specialization:**
These skills are required to use each faction's Tech 2 and 'Augmented' drones. Additionally, they increase the damage of these drones (but not other drone types) by 2% per level. These skillbooks come from LP stores and therefore vary in price; they require .
- 
- 
- 
- 

  - Mutated drone specialization:**
This skill is required to use drones created using rogue drone and Triglavian technology. It adds a 2% bonus per skill level to the damage of light, medium, heavy, and sentry drones requiring Mutated Drone Specialization.
- . Requires , , , .

  - Support drone skills:**
These skills unlock the electronic warfare (EW), combat utility, logistics, and mining drones.
- : Unlocks mining drones and increases their yield by 5% per level.
- : Unlocks logistics drones and increases their repair amount by 5% per level. Requires .
- : Unlocks the salvage drone and increases its chance to salvage by 2% per level. Requires .
- : Unlocks T2 salvage drone and increases salvage chance and maximum velocity by 2% per level. Requires  and .
- : Unlocks EW and energy neutralisation drones. Also increases your drone control range (see above), and requires .

  1. # Spaceship Command
Lastly, if you're flying a drone boat, training its **spaceship command** skill will often improve the performance of your drones considerably. For instance, if you're flying a Gallente **Vexor** cruiser, training  gives a 10% bonus per skill level to your drones' damage and hit points. Unfortunately, these bonuses don't transfer to other ship classes or factions - your Gallente Cruiser skill won't help you to fly an Amarr **Prophecy** battlecruiser, or improve the performance of its drones - but if you're planning to fly a particular ship for a longer period of time, then investing skill training time here can be very beneficial.

1. # Equipment
Most drone modules fit into mid and low-slots, leaving the high-slots free for weapon or utility modules. Most modules in this list are subject to **Stacking penalties**.

 for the Drone and Fighter equipment which can be mutated with Mutaplasmids.

| - | High slot modules |
| :--- | :--- |
| link=]] | wheat|Drone Link Augmentor}}''' increases your drone control range by 20km (24km for the Tech 2 variant). This module is particularly useful for sentry drones (allowing them to snipe distant targets), but less useful for other drones, as the travel time usually precludes using drones at long ranges. Unlike the rest of the list, this module is not subject to stacking penalties. |
| Medium slot modules |  |
| link=]] | wheat|Drone Navigation Computer}}''' increases your drones' microwarpdrive (MWD) speed by 25% (30% for the Tech 2 variant). Note that this doesn't affect their non-MWD speed (i.e. it will help them reach a target faster, but won't help them while orbiting the target). This module is particularly useful for heavy and fighter drones, allowing them to better catch up to faster ships. |
| link=]] | wheat|Omnidirectional Tracking Link}}''' increases your drones' tracking speed and weapon range (optimal and falloff). Great for sentry drones, less used for other drones although it can still improve their damage application, especially if you use your drones against smaller ships than intended (e.g. medium combat drones versus frigates). Just like **turret tracking computer** modules, these can be loaded with **scripts** to double either the tracking or the range bonus, at the cost of eliminating the other bonus. Unlike low-slot Omnidirectional Tracking Enhancer modules, they need to be activated to provide a benefit, and they need a little capacitor energy to run. |
| Low slot modules |  |
| link=]] | wheat|Drone Damage Amplifier}}''' increases the damage your drones deal by 15% (20.5% for the Tech 2 variant or 31.2% for Mutated). |
| link=]] | wheat|Omnidirectional Tracking Enhancer}}''' increases your drones' tracking speed and weapon range (optimal and falloff). It's similar to the mid-slot Omnidirectional Tracking Link module but provides slightly higher bonuses to range, and slightly lower bonuses to tracking. Also, it cannot be scripted and is a passive module (i.e. it does not need to be activated and uses no capacitor energy). |
| Other |  |
| link=]] | Fitting Modules and Rigs Guide#Rigs|l1= Rigs list}}

Various rigs improve drones at the expense of the CPU of the ship.
- **** Increases drone control range by 15km (20km for the Tech 2 rig).
- **** Increases drone hit points (shield, armor and structure) by 20% (25% for the Tech 2 rig).
- **** Increases mining drone yield by 10% (15% for the Tech 2 rig).
- **** Increases the amount repaired by repair drones by 10% (15% for the Tech 2 rig).
- **** Increases drone optimal weapons range by 15% (20% for the Tech 2 rig).
- **** Increases drone microwarpdrive (MWD) speed by 10% (15% for the Tech 2 rig).
- **** Increases the damage done by sentry drones by 10% (15% for the Tech 2 rig).
- **** Improves velocity decrease caused by your stasis webifier drones by 15% (20% for the Tech 2 rig). |
| link=]] | wheat|Overmind 'Hawkmoth' Drone Tuner S10-25T }}''' improves drone speed by 10% while reducing their structure, armor and shield capacity by 25%
- **** improves drone structure, armor and shield capacity by 10% while reducing their speed by 25%
- **** improves drone structure, armor and shield capacity by 10% while reducing their damage by 5%
- **** improves drone damage by 5% while reducing their structure, armor and shield capacity by 5% |

1. # External links
- [Dev blog: Giving Drones an Assist](https://www.eveonline.com/news/view/giving-drones-an-assist) (2014)

{{#css:
table.drones {
  font-size: 90%;
  text-align: center;
 }

table.drones tr th {
  background-color: var(--background-color-warning-subtle);
  padding: 0.2em 0.5em;
  white-space: nowrap;
 }

table.drones tr td {
  padding: 0.2em 0.5em;
 }

}}
