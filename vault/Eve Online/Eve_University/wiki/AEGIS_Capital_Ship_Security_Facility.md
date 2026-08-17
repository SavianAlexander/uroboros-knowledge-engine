---
title: "AEGIS Capital Ship Security Facility"
url: "https://wiki.eveuniversity.org/AEGIS_Capital_Ship_Security_Facility"
pageid: 20367
source: "EVE University Wiki"
categories: ["Candidates for verification", "Data sites"]
harvested_at: "2026-08-16 23:22:25 UTC"
---

# AEGIS Capital Ship Security Facility

{{CMBSiteInfo
| name= AEGIS Capital Ship Security Facility
| type= 
| rating= 
| location= Low and Nullsec
| ship limit= T3 Cruiser
| faction= 
| damage= 
| resist= 
| faction2= 
| damage2= 
| resist2= 
| signature strength= 
}}  The **AEGIS Capital Ship Security Facility** is a **data site** that appears as a level III cosmic signature in Low and Null security space. The site is not restricted to spawning in any specific region of space.

Site notes:
- The site has an invisible 30 minute timer which starts after warping into room 1. The site will despawn once that timer is up.
  - If the Encrypted Key Storage has been successfully hacked and the pilot with the key leaves the site for any reason, the site will despawn immediately, bypassing the normal 2-minute despawn timer for completed sites.
- A data analyzer is required to access site rewards. The hackable key container is a 90 HP Red Core hack, the Security Vault in the second room is a 120 HP Red Core hack. (100 HP Firewall, 70 HP Antivirus, 70 HP Virus Suppressor, 90 HP Restoration Node). Tech II Data Analyzer and high hacking skills are strongly recommended. This site is not forgiving of piloting or hacking mistakes and should be given a wide berth by new explorers.
- No combat is required, so exploration/covops frigates are sufficient to run the site. Covert ops frigates are the most optimal for this site due to 5 second cloak delay + covops cloak, plus the small signature radius and fast speed of frigates. You may run it with other ships but the cloak delay will be too long to attempt pulsing the MWD between decloak cycles without aggressing the NPCs in both rooms, and without a covert ops cloak the speed penalty will cause you to run out of time before the site despawns. Running the site without a cloak to begin with is impossible.
  - Using a **Command Destroyer** is an interesting edge case to this. They are the only ships able to enter the site that can use **micro jump drives** (specifically MJFGs) and thus to great effect skip large portions of the room with skillful MJFG use and good piloting - in fact, since the second room's Security Vault container is almost exactly 100km from warp-in, one use of the MJFG will completely bypass the risks of burning through the minefield.
    - This method should be used with additional caution since command destroyers do not have any hacking role bonuses, and they remain extremely vulnerable to the one-shot damage of the minefields (see below). This method should only be attempted by those with a lot of experience with high difficulty hacks in a limited time frame, such as frequent Sleeper Cache runners.
- The proximity mines have an activation radius of 20km and hurt. The mines in the second room **do 40k omni damage, enough to one-shot anything weaker than a brick-tanked T3C.**
  - The activation radius of the individual mines is visible as a dark red translucent sphere **that is only visible when your camera is within 10-15 km of it.** Careful manual piloting and avoiding reckless use of your MWD in the second room is crucial to survival, since one wrong move or a misjudged mine's danger zone will cost you your ship. It is a good idea to spend a minute or two to stay still and map out a path to the Security Vault in the second room before you make any moves.
  - If you are uncertain about the straight-line path between your ship and the containers you need to hack (or the gate) taking you into the path of a mine, toggle "Look At" on the hackable cans a few times. If your camera goes through a red sphere at any point as you are doing so, the path is blocked by a mine.
- All hostile NPCs in this site are diamond rats and are thus visible on the Directional Scanner. They will only spawn in once someone initiates warp to the site so a potential hunter might be able to tell if someone is attempting to run the site if the NPCs are visible on D-Scan and are lined up with the site.
- All NPCs will pod players. Treat them as you would hostile capsuleers and have your pod saver tab ready to go if you are tackled and cannot escape.
- Both rooms have **AEGIS Security Scanner** and **AEGIS Security Deep Scanner** structures which periodically emit blue energy pulses at intervals of ~30 seconds that will decloak any ships within a 55 and 100 km radius, respectively. The decloaking pulses will bypass Cloak Stabilization timers. You will be notified if you are decloaked by one by the following message - "Your cloak deactivates due to proximity to a nearby object." - note the lack of a specific entity description in the reason for decloaking.

  1. # Warp-in

Acceleration Gate 20 km from warp-in. Nearly any ship class up to cruiser size can enter the site, including **Tactical Destroyers** and **Strategic Cruisers**. 

  1. # Room 1
Head to the AEGIS Encrypted Key Storage and hack it to get the **AEGIS Coded Security Key CSSF-ENS** to unlock the gate. After getting the key you can head to the gate provided you did not fail the hack at any point. 

Note: the gate will be ~175km from the Key and you will be targeted by the Stasis Tower during hacking, meaning you can't cloak again after. **Warping out of the site will cause the key to disappear from your cargo,** so using fast ship with MWD (+ Overdrive Injector Systems to boost speed even further) to counteract the webifier is advised. The position of the mines around the Encrypted Key Storage is randomized between sites, but maintain the same position relative to each other. In other words, instead of burning to the gate to get out on one site, you might need to burn to the right or left on another. 

The Stasis Tower will web out to 250 km and will be 230-235km from the hackable container. Its AI is programmed to lock and web the nearest interactable object within its range, and will thus switch to webbing the container if it loses aggro on its current player target and cannot find another player within 250 km. Thus, if you burn more than 250 km away, the tower will not re-web you after you go back within range since it has switched to engaging the container, and you can burn to the gate normally and save significant time in the first pocket. Note that it will keep you yellow-boxed and thus still prevent you from cloaking.

| 56px|link=]] | **WARNING:** Failing a single hacking attempt on the Encrypted Key Storage container will spawn a hostile response fleet which will make it impossible to get to the gate safely, even if you manage to acquire the key afterwards. Consider the site forfeit if you fail the Key Storage hack. There is roughly a 10-15 second delay before the response fleet arrives - use that time to warp out immediately and save your ship. Once the fleet arrives they will lock you extremely quickly and immediately point you from long range, and their DPS will shred exploration frigates in seconds before **podding** you afterwards. |
| :--- | :--- |

|}

  1. # Room 2
You should stay cloaked to not aggress the fleet before reaching the data can. You can uncloak for 5 seconds to activate the propulsion module, but note that active MWD enlarges your signature radius and makes you easier to target. The NPCs' scan resolution is low enough that they will ideally not be able to target you if you activate MWD **provided you reactivate your cloak first.**

The minefield in this room is significantly denser than in the first room and you land in the middle of it on warp-in. The Security Vault will be around 100km away from warp-in but will almost always be surrounded from most angles by mines which will block you from simply burning to the container safely. You generally will need to burn out of the minefield and get close to the Vault from small gaps between the mines. The position of the mines can vary between sites, however on almost all occasions there will be a safe route to the Vault be it from above, below, or from the sides. The security scanner structures will be positioned randomly around the outside of the minefield and burning too far out of it will put you within their decloaking range if you are not careful.

Once you decloak to hack the Security Vault you will only have a safe time window to attempt ~2 hacks before the NPCs get close enough to point you. (Failing the Vault hack has no penalty.) Those who are experienced with hacking and have the tools necessary (a 'Blackglass' Net Intrusion implant and a T2 Analyzer) can attempt up to 5 hacks while being wary of the range of the NPCs from their ship, though for most players this is impractical.  The Enforcers' warp disruption range is 56 km and they will approach you with a max speed of 1450m/s (though it is closer to 800-1000m/s in practice), leaving little more than a minute or two to grab your loot and escape after they've begun to aggress you. 

| 56px|link=]] | **WARNING:** The NPC fleet's lock times are extremely inconsistent and range from <5 to 40+ seconds. As a result, the decloak-MWD-recloak tactic is not completely safe to use, since there is a random chance that the NPCs will sometimes near-instalock you in between cloak cycles, even with a 5 second cloak delay and a covert ops frigate with no signature radius modifiers (Shield Extenders, active MWD, Inertial Stabilizers, etc.). Unless you are extremely close to the Security Vault already, consider the site failed and immediately warp out - the NPCs will quickly destroy untanked frigates within seconds once they are within their ~60-80km optimal range. |
| :--- | :--- |

|}

1. # Loot
The AEGIS Security Vault will always contain 1 Electro-Neural Signaller which is used to build capital ships, along with 30-50M ISK of AEGIS databases.

| -
! Item Name
! Est. Value
! Note |
| :--- |
| 1x Electro-Neural Signaller |
| 1-3x AEGIS Covert Operation Reports |
| 1-10x AEGIS Fortification Schematics |
| 1-15x AEGIS Personnel File Backups |
| 1-9x AEGIS Security Patrol Reports |

1. # References
- Video: [[Pacifier](https://www.youtube.com/watch?v=-UqdQE9A4u4) November 2021]
- News: [New Dawn, The age of prosperity](https://www.eveonline.com/news/view/new-dawn-new-quadrant)
- Patch notes: [Version 19-10 2021-11-09.1 - New Dawn](https://www.eveonline.com/news/view/patch-notes-version-19-10#2021-11-09.1)
