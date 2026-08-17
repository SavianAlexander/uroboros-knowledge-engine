---
title: "Cloaking"
url: "https://wiki.eveuniversity.org/Cloaking"
pageid: 12361
source: "EVE University Wiki"
categories: ["Fitting"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Cloaking

- Cloaking** allows a ship to become completely invisible to almost all forms of detection. The ability to disappear from view offers many obvious tactical advantages allowing you to observe without being seen, launch surprise attacks or to slip away from dangers.

1. # Cloaking devices

Cloaking devices are high slot modules that allow ships to turn invisible.

| - | link=]] | wheat|Cloaking device}}''' works on any ship and allows them to cloak up. The prototype cloaking device, improved cloaking device and almost all of the faction/storyline/officer cloaking devices count as standard cloaking devices.

This type of cloaking device comes with severe penalties:
- Installed cloaking device will apply scan resolution penalties at all times even if the cloak is offline.
- While the cloak is active the ship suffers massive speed penalty. -90% on prototype cloak and -75% on improved cloak.
- While the cloak is active the ship is unable to warp.
- While the cloak is active the ship cannot target anything.
- After a ship uncloaks it is unable to target anything while the sensors are being calibrated (up to 27 seconds on most basic cloak and skill). |
| :--- | :--- | :--- |
| 2}} | wheat|Covert ops cloaking device}}''' can only be used by certain T2 ships, faction ships and T3 cruisers with a specific subsystem. 

The covert ops cloaking device has drastically less severe penalties compared  to the normal cloak:
- No scan resolution penalty.
- No speed penalty while active.
- Ship is able to warp while cloaked.
- While the cloak is active the ship cannot target anything.
- After a ship uncloaks it is unable to target anything while the sensors are being calibrated (up to 6 seconds). |  |

  1. # Cloaking mechanics

Cloaking is a nuanced mechanic and knowing the exact way it interacts with other aspects of the game is important.

Once the cloaking module is activated the ship is immediately considered to be cloaked. The cloaking animation itself will take a few seconds to play, during which time the cloaking ship is visible in space and on the overview, and can be selected, but cannot be targeted. Once the cloaking module is deactivated, the ship will immediately appear on the overview and be targetable, even though the decloaking animation also takes a few seconds to play.

While active the cloak will prevent activation of all modules, including reloading them or moving items between containers in inventory. However, non-offensive modules can still be activated during the first 5 seconds of being cloaked. Modules that are active before cloaking will also finish their cycles normally, however some modules such as the **micro jump drive** will decloak the ship if their cycle completes while the ship is cloaked. While cloaked, modules also cannot be set to Overheat.

There are multiple factors which can prevent ships from cloaking or forcibly cause a cloaked ship to decloak.
- Being within 2000 m from any object will prevent ships from cloaking and cause cloaked ships to decloak. This includes often ignored objects such as jettisoned cans, corpses, collidable structures, drones, and gas clouds. Non-interactable objects like the crystal asteroid environment around Pochven wormholes will also trigger decloaking.
  - Missiles **will decloak** cloaked ships.
  - Exceptions: Cloaked ships and scanner probes do not decloak cloaked ships. As a side-effect of this, multiple cloaked ships in the same spot will not collide with one another, however if one of them decloaks they will all forcibly decloak and potentially be sent bouncing away from each other. Also, snowballs and fireworks will not decloak.
- Being targeted will prevent a ship from cloaking. This includes being targeted by an NPC or a passive targeting module which does not show as yellow box.
  - However, only completed target locks will prevent cloaking. If the cloaking device activates before a target lock is established, the targeting attempt will fail.
- If you are already cloaked you cannot cloak. This may seem like a non-problem but this will force you to break the gate cloak (see below) before you can activate your cloaking module, and in the process briefly reveal yourself.
- Faction police and CONCORD ships can locate cloaked ships. If you are being chased by either of them due to low standing or criminal action they will warp to you even if you are cloaked.
- Offensive area-of-effect modules such as **Bombs** and **Smartbombs** will *damage* cloaked ships but will *not* decloak them.
- **Command Bursts** do not apply to cloaked ships.
- It is impossible to cloak in all systems affected by an **Electric metaliminal storm**.

  1. # Cloak stabilization
Cloaked ships are subject to an effect known as "decloaking pulse", which comes from one of the following objects:
- In lowsec and nullsec (but not highsec, wormhole space, Pochven, or deadspace including Abyssal deadspace) it is possible to deploy a **Mobile Observatory**, which has a 40% chance to decloak a cloaked ship in its system every 10 minutes.
- [Dazh Liminality Locus](https://everef.net/types/52693) is present in Triglavian Minor Victory systems and in Pochven, which has a 60% chance to decloak a cloaked ship in its system every 9 minutes.

Cloaked ships are immune to Mobile Observatories for the first 15 minutes that they are cloaked: this time is represented by the "cloak stabilization" timer visible above the circular capacitor / hit points / heat indicator in the bottom-centre of your screen. Stabilized cloak duration can be increased by up to three times by the use of the **Strong Veilguard Booster**. In highsec and wormhole space, this timer is effectively irrelevant and can be ignored.

Observatories were added to the game to discourage players from leaving their characters cloaked up in a system for hours without even being present at their computers.

  1. # Skills

 is the only cloaking related skill. This skill allows you to use cloaking devices and also reduces the duration of recalibration delay that comes after decloaking by 10% per level.

  1. # Covert Ops Ships

A limited set of ships can fit and use the Covert Ops Cloaking Device. As noted on the page on **Jump Drives**, this is also the set of ships allowed to use Covert Jump Bridges, and (except for the Deathless and SoE ships), fit Covert Cynosural Field Generators.

- **Covert Ops** Frigates
- **Stealth Bombers**
- **Force Recon Ships** (but not Combat Recon Ships)
- **Blockade Runners**
- **Strategic Cruisers** fitted with the Covert Reconfiguration subsystem
  - Strategic Cruisers not fitted with Covert Reconfiguration can fit the Covert Ops Cloaking Device, but cannot activate it. (The module will be set to consume 10,100 CPU and is forced offline.)
- The  **SoE** **Astero**, **Stratios**, and **Odysseus**
- The  **Deathless Circle** **Tholos** and **Cenotaph**
- The  **ORE** **Prospect**
- The Special-Edition Covert Ops, Logistics, and Recon ships

1. # Jump cloak

To prevent situations where a ship is vulnerable to instant death before its client finishes loading into a new system, Jump Cloak (or Gate Cloak) is an effect automatically applied to every ship that jumps through a stargate or wormhole. Jump Cloak renders the ship invisible, and invulnerable, until it expires. A ship protected by Jump Cloak cannot be decloaked, damaged, or displaced by any outside means. Jump Cloak lasts for 60 seconds, starting when the server registers the jump completing, or until the cloaked ship attempts to move or enter warp. The time remaining is visible via a blue icon in the top left, as shown in the image.

It is often a good idea to take full advantage of the 60 seconds of protection to look at the other ships on grid, player names in Local chat, or objects visible on **directional scan**, and assess the best course of action. Be advised however, that while a ship protected by jump cloak is invisible and invulnerable, its pilot's name *will* still appear in Local chat, potentially alerting enemies to its arrival.

1. # See also
    - Cloak trick**
    - Exploration**
