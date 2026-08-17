---
title: "Electronic Countermeasures"
url: "https://wiki.eveuniversity.org/Electronic_Countermeasures"
pageid: 1570
source: "EVE University Wiki"
categories: ["Game mechanics"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Electronic Countermeasures

- Electronic Countermeasures**, also known as **ECM** or "jamming", gives a chance to cause the targeted ship to lose all targets it has locked (except for the jammer), and loses the ability to target anything that is not currently jamming it for 20 seconds (5 seconds for ECM drones). During combat, this means the affected ship cannot shoot or use any targeted modules on any of your fleet mates. Your target will still be able to use modules that don't require a target such as **smartbombs** or other area effect weapons.

1. # ECM Mechanics
Every ship in the game has a base sensor strength and this sensor is always of a certain type (gravimetric, ladar, radar, magenetometric). 

The jam strength of your ECM is compared to the sensor strength of your target and the jamming is applied based on probability.

Each individual ECM module is applied separately and there are no stacking penalties. This makes it possible to scale up ECM without limit.

Your chance to jam a target is based on this equation:

> <math> \displaystyle\text{Chance to jam} = \frac{ \text{ECM strength} }{ \text{Sensor strength} } </math>

And if you use multiple jammers of same strength:

> <math> \displaystyle \text{Chance to jam} = 1 - \left( 1 - \frac{ \text{ECM strength} }{ \text{Sensor strength} } \right) ^{\text{Number of jammers}}</math>

Note that when calculating the chance to jam a single target using a rainbow fit, the above formula must be modified, considering that a rainbow fit will have different jam strengths per racial jammer.

1. # Falloff and Optimal range

The ECM modules have two separate range attributes: Optimal and falloff. As long as you are within your optimal range your ECM modules will work with full efficiency but once you go to your falloff the ECM module will start to lose its effectiveness.

The ECM module follows the same formula for range as all other modules that have a falloff mechanic:

> <math> \displaystyle \text{Jam strength} = \text{Base} \times 0.5^{ \left( \frac{\max(0,\ \text{Distance} - \text{Optimal})}{\text{Falloff}} \right)^2 } </math>

Going slightly beyond your optimal is not a problem but the effectiveness of ECM will degrade more rapidly as you go further away as seen in the table below.

| Parts into Falloff | Relative jam chance |
| :--- | :--- |
| 0 | 100% |
| 0.2 | 97% |
| 0.4 | 90% |
| 0.6 | 78% |
| 0.8 | 64% |
| 1.0 | 50% |
| 1.2 | 37% |
| 1.4 | 26% |
| 1.6 | 17% |
| 1.8 | 11% |
| 2.0 | 6,3% |

As seen in the table above at range of optimal + 0.4×falloff the jammers are still 90% effective so going slightly beyond optimal is not a big problem.

Here is an example:
let's assume your ECM module has a 50 km range and a 40km falloff. When your target is within optimal range you have a 20% chance to jam them per cycle of your modules.

<math> \displaystyle \text{Jam strength} = \text{20}\% \times 0.5^{ \left( \frac{\max(0,\ \text{Distance} - \text{50km})}{\text{40km}} \right)^2 } </math>

- If your target is 50 km away you will have the full 20% chance to jam
- At 60 km (50 km + 10 km) you will now have 19,15% chance to jam (95,76% of 20%)
- At 70 km (50 km + 20 km) you will now have 16,82% chance to jam (84,1% of 20%)
- At is 90 km away (50 km + 40 km) you will now have 10% chance to jam (50% of 20%)
- At 130 km away (50 km + 40 km + 40 km) you now have a 1,25% chance to jam (6,25% of 20%)

1. # Using your ECM Modules
The race-specific modules are not named in a way that makes it obvious what race of ships they're effective against. Remember that each race's ships all have the same colour background in the portrait image you see when you have them targeted.

- Amarr - Radar (yellow-coloured jammers)
- Caldari - Gravimetric (blue-coloured jammers)
- Gallente - Magnetometric (green-coloured jammers)
- Minmatar - Ladar (red-coloured jammers)

| -
!  Your Target Ship
!  Which Racial Jammer To Use |
| :--- |
| 150px|center]] |
| 150px|center]] |
| 150px|center]] |
| 150px|center]] |

If you can remember these colour match ups then you will remember exactly which module to activate on a ship you are targeting.

When you have successfully jammed your target, you will see a gray circle surrounding the jammer that acquired the jam (shown below the locked ship). Hovering over this will tell you how long until the jam ends. The circle will slowly disappear as the jam ticks down. See the image below.

1. # Examples
you are piloting a Griffin with a set of two racial gravimetric racial jammers on your griffin each giving you 8,39 jamming strength against gravimetric and 2,80 against other sensor types. your griffin also has two radar jammers with same strength but for radar. This is quite highly skilled setup.

Your FC has instructed you to jam the enemy logi, whatever they may bring. The radar jammer works best against the Amarr logi ships (Augoror/Guardian) while the gravimetric is best against Caldari logi ships (Osprey/Basilisk).

You end up against **Augoror**s with 54,2 sensor strength. With single radar jammer on an augoror the chance of successful jam is
> :8,39/54,2 = 0,155... = 16%
16% chance of jamming the target, 84% chance of doing nothing. Doesn't look too good. Lets put rest of the jammers to work too.

With two radar jammers on same Augoror the jam chance is
> :1 - ( 1 - 8,39/54,2 )^2 = 0,285... = 29%
29% chance to jam, 69% chance to do nothing. Better jam chance but we can do better.

The two gravimetric jammers are less useful against Augorors but you still decide to put them on the same Augoror. With two radar and two gravimetric jammers on the Augoror the jam chance is
> :1 - ( 1 - 8,39/54,2 )^2 * ( 1 - 2,80/54,2 )^2 = 0.357 = 36%
The gravimetric jammers are not helping much against Augorors. If there are any ships with vulnerable sensors (Caldari ships in this case) on field then it may be better to jam them even if they weren't as important jamming targets.

On the other hand, if you had had a crystal ball with you when you fit your ship you could have fitted a full rack of four radar jammers. In that case, the probability to successfully jam one enemy Augoror would have been
> :1 - ( 1 - 8,39/54,2 )^4 = 0,489... = 49%

So far the examples have been about focusing all jams on a single target. But the voice of your EWAR FC echoes in your mind *"Spread the jams"*.

If all jams are on one target you may successfully jam the target with one jam and be happy, or you may successfully jam the same target with two jammers and wonder if things could be better. If you spread the jams to one jam per target the probability to jam *at least* one target does not change **but** there is the chance to jam multiple targets.

Spreading four radar jammers to four different Augorors gives you still the same 49% chance to jam at least one of them But you will also have the chance to jam two, three or four targets. The jamming probabilities, in this case, follow **binomial distribution**.

| Numbers of targets jammed | probability |
| :--- | :--- |
| 0 | 51% |
| 1 | 37% |
| 2 | 10% |
| 3 | 1% |
| 4 | 0,06% |

1. # Skills to improve ECM

As with everything in EVE multiple skills will greatly increase your effectiveness when using ECM.

- - Reduces capacitor usage on ECM modules by 5% per level. Requirement for using ECM.
- - Increases the falloff distance of all EWAR modules by 10% per level.
- - Increases the optimal range of all EWAR modules by 10% per level.
- - Increases your jam strength by 5% per level.
- - Reduces the drawbacks of EWAR and sensor rigs by 10% per level.

Additional skills useful for ECM pilots:
- - 5% Bonus to targeting range per skill level.
- - Increases hull bonuses of Caldari EWAR frigates.
- - Increases hull bonuses of Caldari EWAR cruisers.
- - Increases hull bonuses of Caldari EWAR battleships.

1. # ECM equipment and ships

  1. # Equipment

| - | link=|]] | **Racial ECM jammers** - These are the usual jammers used. Each works well against one sensor type but poorly against others. |
| :--- | :--- | :--- |
| link=|]] | **Multispectral ECM Jammers** - These modules are reasonably effective on all targets with a high capacitor cost and shorter range than the racial jammers. |  |
| link=|]] | CONCORD'd]] if used in high security space, and thus cannot be activated in hisec if your **Safety** is not set to Red. |  |
| link=]] | Burst Projector Operation|icon=yes}}). Consumes 250 Heavy Water upon use. The **Wyvern** has a bonus to the duration of the ECM Jammer Burst Projector per level of . |  |
| link=|]] | **Signal Distortion Amplifiers** - These low slot modules increase the strength and optimal range of your jammers. |  |
| link=|]] | **Particle Dispersion Augmentors** - These rigs increase the strength of your jammers. |  |
| link=|]] | **Particle Dispersion Projectors** - These rigs increase the optimal range of your jammers. |  |
| link=|]] | ECM drones are useful for any pilot but are unaffected by any skills or ship bonuses. Jams only last 5 seconds, while still having a regular 20 second duration.

- Hornet EC-300 - Light drone - Has a strength of 1 for all sensor types
- Vespa EC-600 - Medium drone - Has a strength of 1.5 for all sensor types
- Wasp EC-900 - Heavy drone - Has a strength of 2 for all sensor types |  |
| 64px|link=]] | Chimera}} receives a bonus to the optimal range of ECM fighters. These fighters also come in Standup versions with the same jam strengths, for use by Upwell Structures.

- Scarab I - Has a strength of 1.6 for all sensor types per fighter in squadron (max 3)
- Scarab II - Has a strength of 2.3 for all sensor types per fighter in squadron (max 3) |  |

If you know the type of fight you are heading toward you can make a tactical decision and fit a full rack of specific racial jammers(or the fleet commander might make this decision before you head out). 

But if you do not know what kind of ships you are going to jam it is tough to choose between fitting several multispectral jammers or a variety of race specific jammers. 

- The practice of fitting one of each racial ECM is known as fitting a **rainbow** configuration. This generally gives higher jamming strength than multispectral if at least some of the jams are aimed at right type of ships. If you are ever in doubt about what kind of jammers to fit, you should go with a rainbow configuration.
- If you plan on fighting and jamming multiple ships then you should fit **racial jammers**. This will allow you, as the ECM pilot to target a few different ships and have a high chance of locking them all down (i.e. jamming them).
- If you plan on fighting individual ships (or very small gangs), and don't know what type of ship you will be fighting ahead of time then ECM will be more effective with **multispectral jammers** since you could activate more than one on a single target and have a higher chance of locking them down.
- If you have intelligence about the ships being flown by your enemy you can have your pilots fit multiple jammers which match the race type of your target ship(s). It can be useful to carry a spare set of one of each of the four racial jammers in an ECM ship's hold, for refitting on the fly.

  1. # Ships
Since there are no stacking penalties for ECM large number of unbonused jammers will work well. But even though all types of ships can use ECM certain ships have hull bonused aimed for ECM use.

Tech 1 ships:
- 
  - 15% bonus to ECM Target Jammer strength per caldari frigate level
  - - 10% bonus to ECM Target Jammers' capacitor need per caldari frigate level

- 
  - 15% bonus to ECM Target Jammer strength per caldari cruiser level
  - 12.5% bonus to ECM Target Jammer optimal range and falloff per caldari cruiser level

- 
  - 15% bonus to ECM Target Jammer strength per caldari battleship level
  - 25% bonus to ECM Target Jammer optimal and falloff range per caldari battleship level
  - 25% Bonus to ECM Burst Range per caldari battleship level

Faction ships:
- 
  - 10% bonus to ECM Drone jam duration per caldari frigate level
  - -85% penalty to Drone damage
  - -85% reduction in Drone hit points and control range

Advanced ships:
- 
  - 20% bonus to ECM target jammer strength and 10% reduction in ECM target jammers' capacitor need per caldari frigate level
  - 15% bonus to ECM target jammer optimal range per electronic attack ships level

- 
  - 10% Bonus to ECM Target Jammer capacitor use per caldari cruiser level
  - 30% Bonus to ECM Target Jammer strength per recon ships level

- 
  - 10% Bonus to ECM Target Jammer capacitor use per caldari cruiser level
  - 30% bonus to ECM Target Jammer strength per recon ships level

- 
  - 40% bonus to ECM Target Jammer and ECM Burst Jammer strength per black ops ships level

Tech 3 ship:
- with Obfuscation Manifold subsystem
  - 10% bonus to ECM target jammer optimal range and strength per Caldari core systems level

1. # Countering ECM
Now you should understand exactly what ECM is and how it works within EVE. How is it countered? To make it harder for ECM modules to jam you you simply need to increase your sensor strength. You can do this in a variety of ways:

- Get a bigger ship. Bigger, more powerful ships have naturally larger sensor strength: e.g a Merlin (frigate) has a sensor strength of 11 while a Raven (battleship) has a sensor strength of 22.
- Sensor Booster modules (mid slot) - These can be loaded with ECCM scripts to increase the strength against jamming. As active modules, they can also be overheated - and will normally overheat for quite some time.
- Signal Amplifiers (low slot) - These modules are similar to Sensor Booster modules but use low slots and give smaller bonuses.
- Remote Sensor Boosters - These allow you to remotely project ECCM script support onto your friend's ship.
- Gravimetric / Magnetometric / Radar / Ladar Sensor Compensation skills - Increase sensor strength by 4% per level of their respective sensor types.

Often, however, the most effective way to counter ECM is to destroy the ECM ship(s) or hurt them enough that they're forced to warp out. The Griffin, Blackbird, Kitsune, and Falcon tend to be only barely tanked if they're tanked at all, while the Rook and the Scorpion can mount tanks, but usually still have unimpressive defenses for ships of their respective sizes. ECM pilots tend consequently to be fairly jittery, so even if you can't actually kill them, if you can demonstrate the ability to hurt them they often run away.

A long-ranged, high-alpha weapons such as artillery can deal an intimidating amount of damage in one volley, which is good for this. In battles that are being fought at long range anyway, damage-dealers fitted with long-range missiles are often tasked with this kind of 'anti-support' fire because by the time their missiles travel to the primary target it would be dead anyway, and volleys of heavy or cruise missiles can also persuade ECM ships to run away.

Drones can also be an effective option. ECM ships often have trouble defending themselves against drones: drones keep fighting even if their parent ship is jammed and, although a single drone is easily jammed, the coordination and time required to lock onto and jam a full flight -- assuming the ECM pilot even has five jammers -- are considerable. Griffins and Kitsunes mount small weapons which can hurt drones, but usually can't tank the drones for long enough; a Blackbird fitted with Rapid Light Missile Launchers and a large plate or shield extender might be able to destroy drones, but the pilot would still be distracted.

1. # Flying ECM
Although flying an ECM ship can involve tough targeting decisions and complex jammer micromanagement (see below!), when you start out you can make things fairly simple for yourself. Assuming you're not flying a large, tanked ship (the Scorpion) or a ship with a covops cloak (the Falcon) -- in which case you should know what you're doing anyway -- you need to:
- be near the edge of your optimal range
- fight aligned
- run away if you're being shot
- help your fleetmates escape tackle if retreating

On most ECM ships ECM's long optimal range is one of the things that keep you out of trouble, so you should try to warp to targets at your optimal range, *not* at zero. (Sometimes you will have to fight at short range -- if the enemy jump into an offensive **gatecamp**, for example.)

Your best way of staying alive is to warp out and to be able to warp out quick enough if something starts attacking you you should be pre-aligned. When you arrive on-grid where a fight's happening, or when a fight starts where you are, you should quickly select a convenient celestial object (planets are good), or a bookmark, and align to it.  

Then, if you find yourself being targeted or if the FC orders the fleet to scatter, you can get out quickly by warping to the celestial you're aligned to. If the fight's still going on, you can then warp back in (warp at your optimal range to one of your fleetmates who was in the middle of things) and carry on jamming. Be careful when choosing an object to align to, however.  If the enemy is between you and the celestial you are aligned to, your course will take you toward the fight, and your range advantage will be negated.  If you align to an object in the opposite direction of the enemy, you risk straying out of your optimal range, and decreasing the likelihood of successfully jamming your opponent. Whenever possible, pick a celestial which, when aligned to, will put you on a course perpendicular to that of your foe, assuming you're near your optimal range, and the enemy isn't burning directly toward you. This will ensure that you don't rapidly get out of range, or wander into the midst of the battle.

If your fleet is losing the engagement and the FC calls for a retreat take a moment to see if any of your fleetmates are tackled by the opposing fleet. If so, and their ship is more expensive than yours, a valuable tactic is to jam the ships which have points on that ship.  If it's not obvious which ships to jam ask the pilot in Mumble to call out the ships with points on him.  If you think you can jam out the tackle tell your fleetmate to align out (he should be already) and spam their warp-to button as you jam the tackle. Call out any successful jams so your fleetmate can see if they're free to warp off.

With more experience, you may notice situations where it might be worth staying around until you die to get a crucial jam in, but that's something you have to make a call on yourself.

If you have some time (you are not about to die) you can gain a large advantage if you do not activate all of your ECM modules on a target.

Let's assume two targets are attacking you and your friends. Immediately you target both of them and decide you will turn on two multispectral jammers for each (four in total). One of the targets gets lucky and avoids both of the jams and the other target gets jammed from your first ECM module. The lucky enemy (that didn't get jammed) then happily targets you and blows you up! Ouch.

Now that is an unpleasant scenario we might have avoided.

This time we decide to turn on one module per target.
Target 1 is lucky and doesn't get jammed.
Target 2 is unlucky and we jam them.

At this point, we have 2 more modules to work with.
We attempt to jam target number 1 with another module and he is AGAIN lucky (just like in the first example)
We finally turn a third module onto target 1 and this time we jam him and live to fight another day!

You can see with this example that it is in your best interest to use as little number of jammers on your targets until you get an actual jam. Remember that the activation time of ECM modules is 20 seconds, which is the same length of time that the jam will last (5 seconds for ECM drones).

If you want to you can turn the auto-repeat on your jammers off. This is one of the options in the menu you get when you right-click the jammer's button on your HUD when you're in space. With auto-repeat off your jammers will deactivate after every cycle, saving you the trouble of deactivating them yourself if their target is already jammed by another jammer.

  1. # Overheating
Like many other modules, ECM jammers can be overheated. **Overheating** an ECM jammer increases its jamming strength. This can be very useful but, as with ECM in general, since it only increases your chance to jam, it's still a gamble: overheated jammers can fail to jam their targets, and when that happens you still have the heat damage from overheating. And, just like any other module that can be overheated, if you overheat too much you'll burn your jammers out. You may find it useful to persuade a fellow corpmate to be your practice dummy, letting you practice overheating and get a feel for how long you can heat your jammers before you do it in battle.

1. # ECM targets
Unless you only have one or two enemies, judging which enemy you should try to jam is an important decision. Your Fleet Commander may tell you to jam a particular target or even appoint an EWAR target caller, so you should obviously follow their orders. However, most FCs, most of the time, will not issue specific orders for their ECM ships, leaving the decision to you.

Often, particularly when you're in a large fleet, the primary target called by the FC for the damage-dealers is not the best ship to jam, since hopefully, it will die soon anyway. Instead, you should quickly look at what the enemy have and find some good targets for ECM.

If there are other ECM pilots in your fleet it can be useful to coordinate with them so that you don't waste time jamming the same target several times over. In a small fleet you might report your jams textually in the fleet chat channel, or even over Mumble on ECM subchannel. In a large fleet you could try setting up a separate EWAR chat channel for EWAR pilots.

Here are some ships that often make good ECM targets.

  1. # Logistics ships
  - Logistics ships** are T1/T2 cruisers and T1/T2 Frigates which can rapidly repair their allies' shields or armor. They have high sensor strengths, so they aren't the easiest ships to jam, but if you do jam one it won't be able to heal the rest of the enemy gang for twenty seconds. Some gangs depend mostly on their logistics ship(s) for their tank, so this can be a battle-changing move.

Jamming can be extra devastating if the logistic ships are running a cap chain. Jamming will disrupt the chain and in best case can cause multiple ships to cap out causing the chain to collapse.

The T1 logistics frigates are the **Inquisitor** (Amarr), **Bantam** (Caldari), **Navitas** (Gallente), and **Burst** (Minmatar).

The T2 logistics frigates are the **Deacon** (Amarr), **Kirin** (Caldari), **Thalia** (Gallente), and **Scalpel** (Minmatar).

The T1 logistics cruisers are the **Augoror** (Amarr), **Osprey** (Caldari), **Exequror** (Gallente), and **Scythe** (Minmatar).

The T2 logistics cruisers are the **Guardian** (Amarr), **Basilisk** (Caldari), **Oneiros** (Gallente) and **Scimitar** (Minmatar).

  1. # Enemy EWAR
If the enemy have their own EWAR ships it can be useful to jam them. This goes especially for enemy ECM ships. Equally, of course, electronic warfare ships, and especially ECM ships have high sensor strengths for their hull size.

  1. # Damage dealers
If you don't see any stand-out targets, like logistics ships, jamming enemy damage-dealers is probably a safe decision. This usually means **battleships** and **battlecruisers** but the enemy might field a fast-moving gang of smaller ships. The T2 cruiser-sized **heavy assault cruisers** and frigate-sized **assault frigate**s are noteworthy smaller damage-dealers, and they don't have very high sensor strengths.

If you're flying a Blackbird, Scorpion or Kitsune you will have a long enough range that you will be one of the few ships in the fleet that might be able to counter enemy snipers. With good ECM range skills, the Blackbird and Kitsune should have a decent chance to jam sniper HACs, and the Scorpion should have a decent chance to jam sniper battleships. (This is where a Targeting Range script can come in useful if you fitted a Sensor Booster.) Keep in mind that your jammed target can still shoot back at you if you're in range, and that **remote sensor dampeners** ("damps") or **tracking/guidance disruptors** may be more appealing, depending on the situation.

  1. # Triglavian Ships
Ships from the **Triglavian Collective** have a spooling mechanic, whereby their damage or reps get stronger the longer they're sustained on a single target. A Triglavian ship can be jammed to break its spool on a ship, reducing its potency. Like with jamming sniper damage-dealers, damps or tracking disruptors are more reliable for this purpose.

  1. # Jamming and aggression
Sometimes it is unwise to jam someone who is trying to play docking games with you. To win at docking games you sometimes need to rely on the fact that when your target shoots someone he starts a so-called **weapon timer** and cannot dock for 60 seconds, hopefully giving you time to kill them. If you happen to get a jam off on a person playing docking games he won't be able to get weapons timer for 20 seconds (5 seconds for ECM drones).

Weapon timers also prevent pilots from jumping through stargates, and so the same principle applies if you want to keep someone aggressed on one side of a stargate.

  1. # Overheating
  - Overheating** can be a powerful tool on an ECM ship, as overheating a jammer increases its jam strength by a full 20%, which can make a large difference in the odds of getting or missing the jam. However, because jammers have a fairly long cycle time (at 20 seconds), and fairly high Heat Damage (of 6.6HP) (or even more for Burst Jammers), a single overheated jam cycle from multiple jammers can build up a lot of Rack Heat, and cause a lot of collateral damage to the rack.

If in doubt, don't overheat. Better to miss a few jams than to miss *all* the jams after the first minute because you burned your midslots out.

1. # History
Since October 2018, a jammed target can attack the ship that is jamming it, see [forum post](https://forums.eveonline.com/t/ecm-balance-pass-november/115696), [patch notes](https://www.eveonline.com/news/view/patch-notes-for-october-2018-release), and [dev blog](https://www.eveonline.com/news/view/october-balance-pass). This was a notable change in mechanics as solo pilots flying an ECM ship cannot protect themselves by jamming an enemy. Before the changes, ECM was generally regarded as the most effective Electronic Warfare technique, because of its potency and the safety it provided to the user.

1. # See also
- **Electronic warfare**
- **:Wikipedia:Binomial distribution**
