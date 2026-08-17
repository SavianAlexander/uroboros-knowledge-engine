---
title: "POS Setup"
url: "https://wiki.eveuniversity.org/POS_Setup"
pageid: 1961
source: "EVE University Wiki"
categories: ["Candidates for cleanup", "POS"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# POS Setup

1. # Overview

- covers everything in the old POSs and you PDF guide

- does not cover offense/defense except in passing (see the **POS Warfare** page for that complicated topic)

- need to add reasons on why to setup a POS

- POS structures are going to get moved to a another page **POS Structures**

1. # Standings and Sovereignty Restrictions

With the release of Crius, you no longer require standings with factions to anchor in any high security systems. In addition, Crius opened up almost all 0.8 to 1.0 systems with the exception of a few restricted systems. You do, however, still require Starbase Charters from the relevant faction to keep your tower online. You will also need a corporation that is at least one week old to anchor a tower.

  1. # 0.5 to 1.0 Security Systems
- No standings required.
- Faction Starbase Charters are required.

  1. # 0.1 to 0.4 Security Systems
- No standings required.
- No Starbase Charters required.

  1. # 0.0 or Null-Sec Systems
- No Starbase Charters required.
- Sovereignty not required, but anchoring a tower in another alliance's system will send a notification to all members of that group with appropriate roles. Don't expect it to survive long unless you've first gotten permission to deploy your tower.
- If deployed in a system where your alliance holds Sovereignty, a 25% fuel consumption discount will be applied to all Alliance control towers in the system

1. # Choosing a Tower
- standard towers vs faction towers
- For Increased upfront cost you can invest in a faction tower which will give you a reduced tower fuel consumption(Really Awesome), and a greater amount of hitpoints(kinda meh).
- Standard Towers, and faction towers however have the exact same CPU and Powergrid, so there are no fitting advantages of choosing a faction over a standard in that respect
- Faction towers also benefit from reduced intial anchor/unanchor/online timers for the tower itself. Note this effects only the tower itself, not the anchor/unanchor/online timers for POS modules

- matching fuel type to location or why not to

1. # Fuels

  1. # Starbase Charters
All POSs located in hi-sec space (0.5 to 1.0) require starbase charters in order to operate. These charters are race-specific based on the region where you are placing the POS and are bought with **Loyalty Points** from NPC corporations.

All size towers require 1 charter per hour.

  1. # Fuel Blocks
Control towers consume a certain number of fuel blocks per hour. There are four types of blocks, one for each race, the difference being which kind of isotopes are used in their manufacture. They are manufactured like ammo (using a blueprint in a station or POS ammo or component assembly array, in batches of 40).
- Amarr, (True) Sansha and (Dark) Blood towers use Amarr Fuel Blocks, which use Helium Isotopes
- Caldari and (Dread) Guristas towers use Caldari Fuel Blocks, which use Nitrogen Isotopes
- Gallente and (Shadow) Serpentis towers use Gallente Fuel Blocks, which use Oxygen Isotopes
- Minmatar and (Domination) Angel towers use Minmatar Fuel Blocks, which use Hydrogen Isotopes

The quantities are:
- Small: 10 blocks / hour, 7200 / 30 days
- Medium: 20 blocks / hour, 14400 / 30 days
- Large: 40 blocks / hour, 28800 / 30 days
Faction towers use less (10% less for tier 1, 20% less for tier 2). You also get a 25% discount if your alliance holds sovereignty where the tower is anchored.

With a fully researched BPO, the materials required to make one batch of 40 blocks (and therefore to run a large tower for 1 hour) are:
- Coolant **[P2**]: 8
- Enriched Uranium **[P2**]: 4
- Mechanical Parts **[P2**]: 4
- Oxygen **[P1**]: 20
- Robotics **[P3**]: 1
- Heavy Water **[Ice**]: 150
- [Racial] Isotopes **[Ice**]: 400
- Liquid Ozone **[Ice**]: 150

There are two competing theories on tower selection vs fuel availability. Some POS owners will choose a tower based on the region in order to reduce the distance that isotopes will have to be hauled. Other POS owners will choose a tower based on attributes and are willing to haul isotopes from other regions. If you do not have access to an orca or freighter, you may wish to choose your tower type based on isotope availability within the region or neighboring regions.

Formerly, consumption of liquid ozone and heavy water was based on powergrid and CPU usage. With the switch to fuel blocks in Crucible 1.1 this is no longer the case and the quantities above hold regardless of what modules you have online. Generally heavy water is cheap, while liquid ozone is 3x to 4x more expensive due to its use in **cynosural field generators** (needed to use jump drives).

  1. # Strontium Clathrates
The fourth component that is refined from ice (besides isotopes, liquid ozone and heavy water) is **Strontium Clathrates**. Unlike the other fuels, Strontium Clathrates are only used when the POS is placed into **reinforced mode**. There is a separate fuel bay for Strontium Clathrates in the tower called the "stront bay". As explained on the **POS Warfare** page, you should always put at least 1 hour's worth of Strontium Clathrates into the stront bay.

- Small: 100/hr, 4166 max units for 41.7 hours
- Medium: 200/hr, 8333 max units for 41.7 hours
- Large: 400/hr, 16666 max units for 41.7 hours

As a general rule of thumb, if you put "N" units of Strontium Clathrates in your tower, you should keep a spare stock of "N" units Strontium Clathrates in a nearby location. That way, if the attackers leave you alone after the initial attack, you can quickly replenish the "stront bay".

  1. # Summary Fuel Table

| + POS fuel usage per hour
! Tower size !! Small !! Medium !! Large |
| :--- |
| 1 || 1 || 1 |
| :--- |
|  |
| 10 || 20 || 40 |
| :--- |
|  |
| 2 || 4 || 8 |
| :--- |
| 1 || 2 || 4 |
| :--- |
| 1 || 2 || 4 |
| :--- |
| 5 || 10 || 20 |
| :--- |
| ¼ || ½ || 1 |
| :--- |
| 37.5 || 75 || 150 |
| :--- |
| 100 || 200 || 400 |
| :--- |
| 37.5 || 75 || 150 |
| :--- |
|  |
| 100 || 200 || 400 |
| :--- |

1. # Corporate Roles

In order to allow people other then the CEO or Directors to manage the POS, you must hand out some corporate roles.

  1. # Config Equipment
This role does not have any direct role on starbase equipment, but the starbase management panel's structure access tab may be used to grant access to some structures to users having this role.

  1. # Config Starbase Equipment
  - Do not hand out this role lightly.** People with this role can unanchor your POS structures or even the POS tower. They can change the POS force field password, bumping pilots suddenly out of the POS into the arms of waiting enemies.

Allows:
- Viewing contents of Ship Assembly Arrays.
- Access to the "Force Field" and "Defense" tabs of the tower management UI.
- Take from Ship Maintenance Array.
- See the true capacity in use of Ship Assembly Arrays, but only view/take according to corporate roles for each tab.

  1. # Starbase Defense Operator
Allows:
- Pilot to take active control of POS weaponry.
- Pilot will receive Notifications if any corporation starbase or starbase structure comes under attack.

  1. # Starbase Fuel Technician
Allows:
- Deposit into Ship Assembly Arrays, but not view contents or capacity used.
- Deposit into the tower fuel bay, and to view fuel quantities.
- Deposit into the stront bay, and view stront quantities.
- View "Structures" and "Processes" tabs of the tower management UI.
- Take from silos(?).

1. # Setup

Before setting out to setup your shiny new POS tower, keep in mind the following points:

- Anchoring and putting a tower online takes a long time. Allow 15+ minutes for a small tower, 30+ minutes for a medium tower and 60+ minutes for a large tower.
- You will also need a lot of time to anchor modules, especially if you have a complex setup.
- A corporation that is not a member of an alliance can only anchor a single POS tower per day per system. However, a corporation could anchor multiple POS towers in multiple systems on the same day.
- An alliance can anchor a maximum of (5) POS towers per day per system. Even if there are multiple corporations in the alliance. Just like with the corporate limit, the alliance may anchor more towers in other systems on that day.
- This throttling also applies in wormholes (**w-space**).  (This no longer appears to be accurate as of Feb 2024)
- The anchor limit does not count the unanchoring of a tower. (needs verification)

Before setting off to go anchor the tower, you should make a list of things to bring along. **Orca** ships make wonderful POS builders, but you can also use a T1 or T2 hauler to haul the tower, modules and fuel. Keeping in mind that T1 haulers are extremely fragile and a POS tower plus modules makes for an attractive gank target. The list of things that you should bring:

- The **POS tower**
- 12-36 hours worth of "**stront**"
- At least 2-3 days worth of POS fuel, or maybe a full 28 days worth.
- **Shield hardening modules**
- Other **defensive structures** (ECM and sensor dampeners)
- (some) **Offensive weapons**

For the initial setup, unless there are logistical issues involved in making a second trip, you should probably leave things like labs, silos, ship assembly arrays, and maintenance bays for later. Putting up a POS in lo-sec, w-space, or null-sec is a risky operation until the tower is fueled and online. The more items that you bring along before the POS tower shields are active, the more items that you risk losing if someone attacks you. Once anchored, put online and fueled, the POS tower's shield system will come online and offer you a refuge.

  1. # Anchoring the Tower

Once you have settled on a location and found an empty moon, you should haul your tower out to the location along with a bit of fuel and "**stront**" to get the tower online. You can not start anchoring without corresponding Starbase charters in cargo. Even one piece is enough to start process.

- Warp to the chosen moon at a random distance
- Right-click the tower in your cargo hold, choose "Launch for Corp"
- Right-click the tower in space, choose "Anchor"
- Right-click the tower and bookmark its location

The tower will then be moved by the EVE server to the center of that grid location. This can be up to 200km away from your warp in point, so you may have to look around to find it. Anchoring time varies by tower size. Small towers take 450 seconds (7.5 minutes), medium towers take 900 seconds (15 minutes) and large towers take 1800 seconds (30 minutes). When you anchor a tower, make a note of the EVE time and the estimated time for it to finish (or use a watch / timer).

Since you can do nothing else during the tower anchoring process, you may want to warp off to a safe-spot to wait out the timer. Preferably a "deep" safe-spot that is more then 15AU away from any celestial body and not inline between two celestial bodies.

  1. # Initial Fueling

When the timer is up, warp back to your tower's bookmark at 0km. Now you can fuel the tower and put it online. You must be **within 2500m** of the tower in order to access the fuel/stront bays.

- Right-click the tower, "Access Strontium Bay"
- Drag and drop the Strontium Clathrates into that bay
- Right-click the tower, "Access Fuel Bay"
- Drag and drop the fuel into that bay
- Right-click the tower, choose "Put Online"

Once again, there will be a long delay while the tower goes online. Online time also varies by tower size. Small towers take 450 seconds (7.5 minutes), medium towers take 900 seconds (15 minutes) and large towers take 1800 seconds (30 minutes). Make a note of the EVE time and when you estimate that the tower will finish going online. If you are worried about unwanted visitors, warp back to a safe-spot to wait out the timer.

  1. # Basic Tower Configuration

After the tower has finished going online, and for as long as the fuel holds out, the tower will now have a protective force field bubble around it. At which point you should warp back to the POS tower and finish the initial configuration. Most importantly: **you must set a password before the shields will keep unwanted visitors outside the bubble**

- Get on grid with the tower and be within 50km
- Right-click the tower, choose "Set Password"
- Enter a good, random password (you can always change it later)

See **Force Field Settings** on the **POS Warfare** page for a more detailed description of how POS shields work.

The "Allow Corporation Members" and "Allow Alliance Members" (if you are in an alliance) will be checked by default. For most cases, you will want those two check-boxes in the enabled state. If you do not check one or both of these then when the shield goes online after entry of the password, you will be kicked away from the POS tower by the bubble. If this happens, re-approach the tower and right-click the tower to get back into the management screen. You can then fix the restriction masks while outside the bubble. (See "**Restriction Masks**".)

On the "**Defense**" tab, the only check-box that should be turned on in high-security space is "Attack if at War". (See "**Tower Defense Settings**" for more details.) Make sure that you **click the "Apply" button** to save your changes.

  1. # Anchoring Modules

Once the tower is fueled, online and the shield is up, you can start anchoring modules. But first, keep in mind the following limitations and common mistakes:

- Only one module can be in the process of "Anchoring" or "Onlining" at a time
- Batteries (weapons / electronic warfare) must be mounted at a minimum distance outside the POS bubble
- Arrays should be located inside the POS bubble, at a minimum distance from the tower
- Anchoring is a two-step process
- If your ship is moving, the anchoring box will also move

To anchor a module:

- Right-click it in your cargo hold, "Launch for Corp"
- Right-click the item in space and choose "Anchor"
- A translucent green box with white arrows will appear
- Drag the box around with the arrows
- Right-click on one of the arrows, and choose "Anchor Here"

After anchoring, you can either leave the module offline or you can right-click the module to put it online and active. When moving the green box with the arrows, every "step" is about 960m. Most modules need to be placed a minimum of 1920m away from the nearest module (2 steps).

1. # Maintenance

  1. # Fueling

One thing, as a POS fuel jockey, which will make your life easier are spreadsheets. Ideally, you should setup a spreadsheet such as the [POS Fueling (blank)](https://docs.google.com/spreadsheet/ccc?key=0AsopBfkYYvf3dFVpZmZZU3VQRnR6TElubWJXYy1yREE&hl=en_US|EVE) and use it to track:
- Fuel costs (by querying EVE-MarketData, EVE-Central or EVEMarketeer)
- The fuel supply that you have stockpiled.
- How much per hour the tower currently consumes.
- The amount of fuel in the tower.
The spreadsheet should also have a feature where, if you tell it how much fuel is in the tower, that it will tell you how many units of each fuel type to take out to the tower to get a balanced fuel load.

1. # Tear Down and Mothballs
Eventually, all things must come to an end and it is time to tear down your tower, or move it to a new location, or just go on temporary hiatus.
  1. # Tearing down a POS Tower
Taking a tower down is faster then putting it up, but you should still allow a few hours if you have lots of modules anchored. You will need some sort of cargo ship (T1 hauler, T2 transport, orca, etc.) to scoop the modules to your cargo hold. If you are working on scooping up batteries outside the shield which are spread apart, then an afterburner module will be very useful.

- You must be within 3000m of the module to initiate the offline/unanchor process.
- You must be within 2500m of the module in order to scoop it to your cargo hold.
- The tractor beam will not work on unanchored modules.
- Labs, storage, guns, etc. will have to be emptied of any contents before they can be offlined.
- In order to unanchor the tower, all modules must be taken offline and unanchored.

  1. # Mothball
Sometimes you'll want to save on fuel costs but not entirely abandon your location at the moon. This is done by unanchoring any expensive modules, then taking the tower offline. The POS shield will vanish and everything that was online will go offline. Note that since the tower is now defenseless, you should only mothball towers in hi-sec (or possibly player-controlled null-sec).

1. # Additional Reading
See also the following UniWiki pages:
- **POS Structures** - A list of all structures that can be anchored at the tower.
- **POS Warfare** - Covers the setup of offensive / defense modules and combat.
You may wish to also reference these informative pages:
- [POS'S AND YOU (forum thread)](http://www.eve-ivy.com/forums//viewtopic.php?t=21196)
- [POS Setups: Jump Bridge/Cyno Jam/Reactions, Moon Mine/Mining, Labs, WH (forum thread)](http://community.eveonline.com/ingameboard.asp?a=topic&threadID=817184)
- [POS FAQ at EVE-Guides](http://www.eve-guides.com/poss/FAQ.php)

1. # Tools and Links
Fueling calculators, POS fitting calculators, etc.
- [EVE Online POS Builder](http://www.vexar.de/pos_fitter/)
- [MyPOS (calculate fits)](http://www.eveonline.com/ingameboard.asp?a=topic&threadID=1258028)
