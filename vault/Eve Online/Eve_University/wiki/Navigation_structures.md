---
title: "Navigation structures"
url: "https://wiki.eveuniversity.org/Navigation_structures"
pageid: 17597
source: "EVE University Wiki"
categories: ["Candidates for verification", "Needing updates", "Structures"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Navigation structures

Navigation structures are part of the Upwell Fast Logistical Expansion (FLEX) structures and currently the only FLEX structures. The three navigational structure types are the Ansiblex Jump Bridge, the Pharolux Cyno Beacon, and the Tenebrex Cyno Jammer.

1. # Mechanics
All three structures come with a built-in service module but cannot be fitted further. You can also not dock in them, but you can board them. Boarding them is mostly used to put their module online. You leave your ship in space if you board them like if you board another ship.
Any pilot can add fuel to them. For that you simply deposit the fuel in them.

  1. # Deployment
Each navigation structure requires a specific **Infrastructure Hub** upgrade so you can install it. This means they can only be deployed in **sov space**. The deployment takes 45 minutes if you are holding the sov. Afterwards you can directly online the structure. If you’re not holding the sov, the deployment time is <math>( 1 + \text{strategic index} ) \times 45</math> minutes. Their volume is 5000 which means that a **blockade runner** can carry and anchor it.
You can unanchor an undamaged navigation structure in 45 minutes and then scoop it.

  1. # Destruction
Navigation structures are easier to destroy than other upwell structures. Because they cannot be fitted they have no defences of their own.

Like other **Upwell structures**, they can be in high or low power mode. They are in high power mode if their module is online. As this is the more common case, we’ll cover it first:

If a Navigation structure is in high power mode, you can shoot its shields and then its armor. The owner has a reinforcement hour set. This hour can be obtained by anyone through hacking the structure with a data or relic analyser. When the armor hits zero HP it enters a reinforcement cycle and low power mode. The time when this happens is added by 1h and then the next time the reinforcement hour determined. This is added by a random time +/- half an hour. This means the reinforcement period can last between 0.5 and 25.5 hours. If your primary aim is to destroy the structure you would aim for a timer as short as possible that means you aim to reinforce a bit over an hour before the set reinforce hour. This leads to a timer between 0.5 and 1.5 h. If the primary goal is to get a fight maybe at the next day. People might hit the structure pretty much at any time. When it exits the reinforcement, you can destroy it. If not more than 10% of the damage cap is applied for 15 minutes, it fully repairs though. But it is still low power and needs to be onlined.

If the structure is in low power, you can directly destroy it without a timer. Additionally, the shield and armor HP are a quarter of a high powered structure.

All navigation structures have a damage cap of 5000 HP/s and a flat resist of 20%. This means you need to deal 6250 DPS to hit the damage cap and at least 625 DPS to keep it paused.

The cyno beacon and jump <s>gate</s> bridge have each three million shield and armor HP. This means it takes at least twenty minutes to reinforce the structure (because of the damage cap). Their hull HP is three million which leads to at least 10 minutes for the final timer.

The cyno jammer has a bit more HP with each four million shield and armor HP. This means it takes at least twenty-six minutes and forty seconds to reinforce it. Its hull HP is four million which leads to at least 13 minutes and 20 seconds for the final timer.

1. # Ansiblex Jump Bridge

Ansiblex Jump Bridges are supposed to work similar to **stargates** but have some differences. You can only jump to them if the **Access List** allows you to do so.
The Jump Bridges work in pairs, which connect each other. They don’t have to be owned by the same alliance, and the Access Lists can be set up differently for both sides. You get a warning message if you can only jump one way because of that. The maximum range between the pair is five lightyears.
The maximum mass of a ship to use an Ansiblex Jump Bridge is 1.48 mega tons. This means that super capitals cannot use Ansiblex Jump Bridges. All other ships can use them. (It can happen that normal capitals are over the maximum mass if they have their prop mod on or fit more than two plates which is uncommon.)
Each use consumes liquid ozone in the Ansiblex Jump Bridge’s fuel bay. The consumption depends of the mass of the ship and the range:
> <math>\text{Ozone consumed} = \text{Ship Mass in kg} \times \text{Jump Distance in LY} \times  0.000003 + 50</math>
The owner can set up tolls per liquid ozone used. This is done through Access Lists which means the tolls can be set differently for different characters. The user gets a popup message to confirm the payment. You can also set automatic payments in your wallet (Default hot-key  + ). The automatic payments are (like the tolls) per liquid ozone consumed.

The Ansiblex Jump Bridge has a build-in Standup Conduit Generator. If this module is online and pointed to another Jump Bridge which points back, the Jump Bridge can be used. The module needs 30 fuel blocks an hour. The fuel bay is 2,239,121.8 and shared with the liquid ozone.

An Advanced Logistics Network upgrade needs to be installed in the **Infrastructure Hub** so that the Standup Conduit Generator can be onlined. Its daily upkeep cost is twenty million ISK. It cannot be deployed within 500 km of another Upwell structure or 100,000 km of stargates, stations or starbases. Only one per system is allowed.

1. # Pharolux Cyno Beacon

The Pharolux Cyno Beacon has a built-in Standup Cynosural Generator. If this module is online, ships with a **jump drive** can jump to the beacon (given they are in range of course) and ships with a Jump Portal can **bridge** to it. Which pilots can use the beacon is handled through an **Access List**.

The module needs 15 fuel blocks an hour. The fuel bay is 352,055, which corresponds to 70,411 fuel blocks. A full fuel bay would last for 195 days.

A Cynosural Navigation upgrade needs to be installed in the Infrastructure Hub so that the Standup Cynosural Generator can be onlined. Its daily upkeep cost is five million ISK. It cannot be deployed within 500 km of another Upwell structure or within 1000 km of stargates, stations or starbases. Only one per system is allowed.

1. # Tenebrex Cyno Jammer

The Tenebrex Cyno Jammer has a build-in Standup Cynosural Jammer. If this module is online, no new “hard” **cyno** can be lit and the cyno beacon goes offline (if the system had one). Covert cynos can still be used in the system. Other than for the previous structures you can anchor up to three Cyno Jammer in one system but only one can be online at the same time. But its module, the Standup Cynosural Jammer, has a spool up time of five minutes. If a system is jammed, it is visible in the sovereignty info panel at the top left of the screen.

The module needs 40 fuel blocks an hour. A Cynosural Suppression upgrade needs to be installed in the Infrastructure Hub so that the Standup Cynosural Jammer can be onlined. Its daily upkeep cost is thirty million ISK. It cannot be deployed within 500 km of another Upwell structure or 1000 km of stargates, stations or starbases. Up to three per system are allowed but only one can be online.

1. # History
The navigation structures were introduced on November 13, 2018 in the **Onslaught** expansion. The goal was to replace the corresponding functionality provided by **Player-owned starbases** (POSs) before.

The minimum ranges for Ansiblex Jump Bridges and Tenebrex Cyno Jammers (from other Upwell Structures) was increased to 500 km on November 12, 2018.

1. # References

1. # See Also
- **Upwell structures**
- [Navigation Structures Inbound!](https://www.eveonline.com/article/phs7yj/navigation-structures-inbound) Dev blog introducting the navigation structures. Be aware that some mechanics might have changes since then.
