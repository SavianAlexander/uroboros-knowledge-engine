---
title: "Instant align"
url: "https://wiki.eveuniversity.org/Instant_align"
pageid: 9804
source: "EVE University Wiki"
categories: ["Candidates for cleanup", "Candidates for merging", "Game mechanics"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Instant align

- Instant alignment** ("insta-align") is the ability to enter warp within 2 seconds ("instawarp") from a dead stop. If your ship insta-aligns, you can't be  **tackled** as long as you hit warp before the other player hits lock. You can safely jump into, and warp off, any gate, as long as it isn't **bubbled**. Ships **fitted for instant alignment** are commonly used for interstellar travel and flying through **gate camps**.

1. # Align time
Align time is a measure of how long it takes your ship **enter warp** from a dead stop. It takes a minimum of 2 seconds (2 **server tick**s) for someone to be able to **lock** and **tackle** your ship. So if your ship aligns in 2 seconds or less then you can be in warp before being tackled.

The align time for a given fit is listed in the navigation tab of the fitting window. Remember that the align time in the fitting window is for a ship at a dead stop. The actual time it takes you to align to something will depend on your ship, velocity, and heading.

  1. # Reducing align time

The align time of a ship is based on the ship's inherent **mass** and **agility** and bonuses to **agility** and **inertia** from **skills**, **modules**, **rigs** and **implants**. Bonuses relevant to align time are either referred to as **agility** (a positive value) or **inertia** (usually a negative value, unless referred to as *"inertia modifier"* then it's positive), which for all intents and purposes in EVE are the same.

  1. ## Skills
Several skills affect your align time, starting with the most relevant skills:

| - style="background-color: var(--background-color-warning-subtle);"
! Skill
! Bonus |
| :--- |
| Evasive Maneuvering|mult= yes}} |
| Spaceship Command|mult= yes}} |

There are also special case skills, for certain ships fits with specific modules.

| - style="background-color: var(--background-color-warning-subtle);"
! Skill
! Bonus |
| :--- |
| Advanced Spaceship Command|mult= yes}} |
| Armor Layering|mult= yes}} |
| Amarr Hauler|mult= yes}} |
| Caldari Hauler|mult= yes}} |
| Gallente Hauler|mult= yes}} |
| Minmatar Hauler|mult= yes}} |
| ORE Freighter|mult= yes}} |

)
|}

  1. ## Implants
There are also **implants** that help reduce your align time, such as the  and the low- and mid-grade  set.

  1. # Advanced
  1. ## Do I know how insta locking works?
First, a good article about the [server ticks](https://web.archive.org/web/20160223014114/https://www.themittani.com/features/understanding-eve-online-server-tick), so you know how EVE Online is working server side.
After reading that article, you know how long 1 **tick** takes (1 sec for the lazy people). And you want your ship, if possible, out within 2 ticks(before the third starts, because otherwise your enemy has the 3rd tick to tackle you). So as long as your ship is faster than 2 secs align time, you are mostly safe from even instant locking ships. All thanks to game mechanics. \o/
Yes, there is a "but" as you can [read](https://www.reddit.com/r/Eve/comments/360lbq/busting_the_travelceptor_myth/) here. But I doubt that WT's are able to pull it off. :)
And another nice [graph](https://web.archive.org/web/20210111174108/https://eve.501gu.de/misc/travelceptor_vs_instalocker.png) about instalocking and how it works.

Conclusion: If your ship can align within 2 secs and your enemy has a bad internet connection(or his scan resolution is to low), you are pretty much safe from getting shot at/tackled.

- The information above may be outdated. During World War Bee 2, insta-lockers on the 1DQ1-A gate, aswell as low-sec gate-camps, have been able to catch insta-warp interceptors with near 100% success rate. MWD **Cloak trick** in an insta-warp gives you slightly better odds but your still likely to be caught. Be careful moving expensive things in an insta-warp ship, use a scout when at all possible and avoid gate camps.

  1. ## Can warp core stabs help me to stay safe on my travel?
Probably not.  But maybe.

How can stabs save you from WT's? An active warp core stabilizer will negate 2 points of points of warp disruption: 2 warp disruptors or a tech 1 or tech 2 warp scrambler.  This is enough to let you escape a casual tackler.  When fitted to a ship with a native **warp core bonus** (**Venture** or **Deep Space Transport**) this might even be enough to thwart a single serious tackler.

However, you as the target are limited to a single warp core stabilizer plus any native resistance. The attackers can just keep piling it on.  Multiple modules stack, both from a single ship and multiple ships.  Even a single module might be enough; faction warp scramblers apply 3 points of warp disruption and heavy scramblers apply 6 points (tech 1 and 2), 8 points (faction) or even 10 points (officer).

Then there are **HICs**. Those little buggers can use a point that ignores <u>all</u> your stabs and keeps you from warping.

All varieties of scrambler will also shut down your MWD.  Disruptors and HICs will not, so you could still try to crash the gate and jump away.

Conclusion: While you can try and travel in a ship that is slower than 2 secs align by using warp core stabs, they can just bring enough points/scrams or a HIC to keep you from warping.

But no rule without exception:
When can you ignore the <2 sec align time and stacking warp core stabs? Here is the short list:
- Cloaky ships
  - Cov Ops cloak
  - If you feel comfortable to use the cloak+MWD trick, do so, but they can still catch you with fast ships (As the align takes 10 seconds, which is long enough for a fast ship to decloak you and since the MWD is causing a signature bloom, insta lock you)
- Close to a community that is able to form a QRF in a reasonable time and enough buffer to last until help arrives. (Not a very good idea)

1. # Further reading
Since align times are rounded up to the nearest second, align times of 1.01s and 1.99s are, in effect, equivalent. Similarly, an align time of 2.01s is equivalent to an align time of 3s. In order to align instantly, you must have an align time of less than or equal to 2.00s. A detailed explanation can be found in [this Eve-Guides.fr article](https://english.eve-guides.fr/index.php?article=105).

The **Microwarp Drive Cloak trick** manipulates cloaking mechanics to mimic instant alignment for slow-aligning industrial ships.
