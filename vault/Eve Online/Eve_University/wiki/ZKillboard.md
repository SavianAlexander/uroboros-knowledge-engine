---
title: "ZKillboard"
url: "https://wiki.eveuniversity.org/ZKillboard"
pageid: 16165
source: "EVE University Wiki"
categories: ["Applications", "Stubs"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# ZKillboard

- [zKillboard](https://zkillboard.com/)** (short: **zKill**) is a public **killboard**. It collects **killmail**s and publishes them for everyone to read. The EVE Online community uses it for many purposes, the most common of which is to check how much was destroyed in a fight thus who the "winner" is. It is also often used to gather intel and check out what fits people use.

# How does it work
A killmail is sent to the victim, the pilot who landed the killing blow, and their corps. For a killmail to be registered on zKill, one of these entities has to give zKill the right to access it in their name (via a corp/character API). Being that zKill is the most popular killboard, most corps or individuals allow it to pull their killmails.

# Searching on zKillboard

zKillboard provides a search function. You can search and thus filter for

- character, corporation, and alliance names;
- ship types and classes;
- solar systems and regions. (But afaik not constellations.)

Where reasonable you can narrow down to kills, losses and solo.
Further it is possible to filter for certain categories. Known categories are: awox, ganked, npc, highsec, lowsec, nullsec, wh, abyssal. These filters can be combined through manipulation of the url.

Let's say you want to know all Velator losses by EVE University:
- You type the uni's name in the search box, and the resulting page will have the url https://zkillboard.com/corporation/917701062/ because 917701062 is the corresponding corp ID.
- Similarly, the search for 'Velator' results in the url https://zkillboard.com/ship/606/ because 606 is the ship ID for the Velator.
- If you now combine those two urls and append "/losses/" to the end, the resulting URL is https://zkillboard.com/corporation/917701062/ship/606/losses/ you will see all Velator losses by E-UNI.

The reverse order https://zkillboard.com/ship/606/corporation/917701062/losses/ works too, but "losses" has to be at the end. Go ahead and experiment and find out which combinations work. But keep in mind that some combinations require a certain order while others not.

Some more hints on advanced zkill-fu can be found on https://www.sacah.net/2018/08/zkillboard-url-fu.html - note especially the /reset/ keyword which allows you to filter on both victim and attacker...

As you can access zKillboard through an API. You can, in theory, apply any filter you may wish if you take the time to write the code for it.

# Intel Gathering
zKillboard can be used in various ways to gather intel. You can check out an alliance what kind of ships (and fits) they like to fly and their common online times. If you face a certain target you can search for the pilot and his losses in that specific hull. Most pilots tend to stick with similar fits, so you can get a good idea of what the target might be flying. You can even click on export -> EFT and copy & paste the fit into **Pyfa** to simulate it.
