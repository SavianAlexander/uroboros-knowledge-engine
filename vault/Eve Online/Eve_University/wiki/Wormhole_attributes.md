---
title: "Wormhole attributes"
url: "https://wiki.eveuniversity.org/Wormhole_attributes"
pageid: 7611
source: "EVE University Wiki"
categories: ["Wormholes"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Wormhole attributes

Every wormhole has certain restrictions that are determined by the wormhole type. These restrictions include The maximum amount of mass that is allowed to pass through them, the maximum mass that can pass though in a single jump, and the maximum time that the wormhole will remain open for. See the table below for a list of the restrictions for each wormhole type.

This page discusses the set in game mechanical attributes and the visual attributes of wormholes. For information about wormholes in general, or how to tell the current status of an individual wormhole when on grid with it, see **Wormhole Text**.

1. # Wormhole, Wormhole Size and Stability Information

Select sites that provide wormhole information include:

[Ellatha](https://www.ellatha.com/eve/wormholelist.asp) (alternatively to set up a browser search, use the input the entrance label at the end of the URL in place of "%s": https://www.ellatha.com/eve/wormholelistview.asp?key=Wormhole+%s i.e. https://www.ellatha.com/eve/wormholelistview.asp?key=Wormhole+a009 for wormhole type A009 )

Ellatha can be set up as **custom searches** in most common browsers (Chrome, Firefox etc.).

[Anoik.is](http://anoik.is/wormholes) is also a good site to find suitable wormholes.

The following table shows the wormhole characteristics by looking at the label of a wormhole entrance. To see this label, right click the wormhole on the overview and select, "Show Info."  K162 is the generic exit name of a Wormhole; jump to the other side to get the ‘real’ type of the Wormhole.

Values in column "Total Mass Allowed" in the table below are not exact - each wormhole at its birth gets total mass limit which is within range from 90% to 110% of the value specified in the table. 
{{#CSS:
.wh-stats td:nth-child(1),
.wh-stats td:nth-child(7),
.wh-stats td:nth-child(8)
 {
  text-align: center;
 }

.wh-stats td:nth-child(4),
.wh-stats td:nth-child(5),
.wh-stats td:nth-child(6)
 {
  padding-right: 1em;
  text-align: right;
 }

.rowhighlight tr:hover {
  background-color: dimgrey;
 }
}}

| Wormhole Type
! Goes from
! Leads to
! style="width: 5.5em;" | Total Mass Allowed (t)   
! style="width: 7em;" | Max Individual Mass (t)   
! style="width: 9.5em;" | Mass Regeneration (t/day)   
! style="width: 5em;" | Wormhole Classification
! style="width: 6.5em;" | Max Stable Time (Hours) |
| :--- |
| A009 |
| A239 |
| A641 |
| A982 |
| B041 |
| B274 |
| B449 |
| B520 |
| B735 |
| C008 |
| C125 |
| C140 |
| C247 |
| C248 |
| C391 |
| C414 |
| C729 |
| D364 |
| D382 |
| D792 |
| D845 |
| E004 |
| E175 |
| E545 |
| E587 |
| F135 |
| F216 |
| F353 |
| G008 |
| G024 |
| H121 |
| H296 |
| H900 |
| I182 |
| J244 |
| J377 |
| K162 |
| K329 |
| K346 |
| L005 |
| L031 |
| L477 |
| L614 |
| M001 |
| M164 |
| M267 |
| M555 |
| M609 |
| N062 |
| N110 |
| N290 |
| N432 |
| N766 |
| N770 |
| N944 |
| N968 |
| O128 |
| O477 |
| O883 |
| P060 |
| Q003 |
| Q063 |
| Q317 |
| R051 |
| R081 |
| R259 |
| R474 |
| R943 |
| S047 |
| S199 |
| S804 |
| S877 |
| T405 |
| T458 |
| U210 |
| U319 |
| U372 |
| U574 |
| V283 |
| V301 |
| V753 |
| V898 |
| V911 |
| V928 |
| W237 |
| X450 |
| X702 |
| X877 |
| Y683 |
| Y790 |
| Z006 |
| Z060 |
| Z142 |
| Z457 |
| Z647 |
| Z971 |

1. # Classification of Wormholes

| Class 1, 2 and 3 | This wormhole seems to lead into unknown parts of space. |
| :--- | :--- |
| Class 4 and 5 | This wormhole seems to lead into dangerous unknown parts of space. |
| Class 6 | This wormhole seems to lead into deadly unknown parts of space. |
| Class 7 | A wormhole that leads to High Security |
| Class 8 | A wormhole that leads to Low Security |
| Class 9 | A wormhole that leads to k-Space Null Security |
| Class 12 | A wormhole that leads to Thera can also be referred to as C12. |
| Class 13 | Shattered Wormhole System]]. Note that other shattered wormhole systems have the same type of statics as non-shattered systems. |
| Class 25 | A wormhole that leads to **Pochven**, otherwise known as Triglavian Space |

It is worth noting that there are no Class 7, 8, or 9 wormhole systems.

There are wormholes that lead to Drifter space; a series of one-of-a-kind wormhole systems inhabited by **Drifters**. 
Some wormholes lead to **Thera**.

1. # Visual Identification

1. # Wormhole Spawning

Wormholes do not immediately spawn on both sides when a new signature appears. There are several mechanics that allow one to "Close off" a jspace system by rolling all the holes.

This graphic can help:

(see <https://forums.eveonline.com/t/k162-spawn-mechanics/8767> for more information)

So, in writing:
# Roll your Static
# New signature spawns.
# If no one warps to it, signature will remain *indefinitely* with no K162 on the other side. No timer is started.
# If warp is initiated to the new signature, the K162 side of the wormhole is now spawned, but invisible - The Drifter **can** warp to this, even though no signature is available!!! The Wormhole's Time To Live timer is now started.
# When the base time remaining on the wormhole reaches 15 hours (so immediately for a frig hole, ~1 hour for a 16 hour hole, ~9 hours for a 24 hour hole) a check will be made every few minutes. 
# This check has a progressive chance of becoming successful - i.e. the longer it goes on with out being a success, the greater chance it will be one on the next check.
# Once successfully, the K162 side of the hole will become visible in system.
# At any point, if someone jumps through from your system (the non K162 side) the K162 is immediate visible

  - NOTE!** This applies to all wormholes, wandering and static alike. However, its just impossible to tell if a new sig is a wandering wormhole without warping to it, so testing it is a matter of chance. (i.ee you note a new signature in your hole but don't scan it down or warp to it for several days, and when you finally do it turns out to be a Frig hole with a lifetime of 4.5 hours, but the sig has been there for several days)

  1. # Key Takeaways
# If a wormhole is never warped to by anyone, *it will never spawn a K162* and will not begin its timer>
# **Initiating** a warp is all that is required to spawn the *invisible* K162.
# Despite the fact that technically a rolled static that is un warped to never opens, its not good practice to rely on this and instead put eyes on the static and re roll when appropriate.
