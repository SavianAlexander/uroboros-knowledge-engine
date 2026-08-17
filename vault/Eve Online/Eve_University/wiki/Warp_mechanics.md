---
title: "Warp mechanics"
url: "https://wiki.eveuniversity.org/Warp_mechanics"
pageid: 8216
source: "EVE University Wiki"
categories: ["Game mechanics"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Warp mechanics

1. # Basic Warp Cycle
1. Select a destination via the **Overview**, **Fleet window**, **Bookmark**, *etc.* that is at least 150km away and press the “Warp To” button or menu option. Your ship enters warp to its destination.
1. Your ship travels at warp speed to its destination.
1. Your ship exits warp at the intended destination.
1. Proceed with other actions, activate a jump or acceleration gate, begin your attack on hostiles, etc…

1. # Advanced Warp Cycle
1. Select a destination that is at least 150km away via the Overview, Fleet window, Bookmark, etc… and press the “Warp To” button or menu option. This is your Warp Initiation Point (WIP).
1. Your ship aligns to the destination and accelerates to 75% of its current top speed.  The amount of time this takes is the Alignment Time (AT) and the physical distance the ship moves during this phase is the Alignment Distance (AD).
1. Your ship actually enters warp at the Warp Entry Point (WEP).
1. Your ship travels at warp speed to its destination.
1. Your ship exits warp in a random direction and distance (2,500m) from the Warp Exit Point (WXP).  This exit “area” is known as the Warp Exit Envelope (WXE).
1. Proceed with other actions, activate a jump or acceleration gate, begin your attack on hostiles, etc…

1. # What you need to know about entering warp
The most important aspect of entering warp is the time lapse between the point at which you hit the “warp” button and the time you actually enter warp.  When you hit the Warp button, your ship has to align itself physically to its destination and accelerate to 75% of its current top speed, before it can actually enter warp.  This has a number of consequences.
- While the ship is aligning, it can be targeted by other ships and have a Warp Disruptor (or warp scrambler) activated on it.  When this happens, the ships warp drive is deactivated and the ship is prevented from warping.
- During the ship’s alignment, its warp drive will be deactivated and the ship prevented from warping, if it enters an Interdiction sphere (i.e. warp bubble).
- Alignment time of a ship is directly affected by its size.  Specifically, very small ships (i.e. shuttles and most frigates) will align and enter warp very quickly, whereas large ships (i.e. battleships, capital ships, etc…) will take a long time to align and enter warp.
- Note that part of the alignment process is to accelerate your ship to at least 75% of your current top speed.  Propulsion modules (i.e. Afterburner or Micro Warp Drive), when activated, increase your mass, increasing your alignment time. (While they also increase your top speed, the change in mass is what changes align time.)
  - However, their speed increase can also be exploited for extremely large ships. If a ship's alignment time is longer than one cycle of their afterburner or microwarpdrive, the module can be activated for a single cycle to give a few seconds of boosted acceleration, allowing the ship to enter warp immediately upon the module deactivating.
- You can pre-align your ship by using the “Align To” option in the various menus.  This will align your ship to a destination and accelerate you to your maximum speed.  While in this state, you can enter warp to your pre-aligned destination instantly.  Doing this is what is meant when you are advised to “fight aligned” or “be aligned”.  The reasons for this is simple, if a hostile ship (war target, pirate, etc…) warps in on you while you are mining or doing a mission or whatever, you can warp out while they are decelerating from their warp (i.e. before they can target you and apply a warp disruptor).

The second important aspect of entering warp is the physical distance your ship moves between the time you press the "warp" button and you actually enter warp.  There are two instances where this distance is important:
# If your ship collides with a solid object (station, gate, ship, etc...) it will "bounce".  At this point, your ship will try to re-align and enter warp again.  If you are bumping in to a structure (station, asteroid, acceleration gate, etc...) this process can take a very long time.  If this happens, it is best to cancel your warp and manually pilot until you are clear of the obstruction then try and warp again. However, as per a change made on 10 September, 2019, any ship which remains stuck bumping for 3 minutes will automatically enter warp regardless of alignment.
# If your ship enters an Interdiction Sphere (i.e. bubble), your warp drive will deactivate and you will need to manually fly clear of the bubble before you can warp.

See **tackling** for information on causing warp disruption.

See **warp core strength** for information on resisting warp disruption.

1. # What you need to know about exiting warp
The most important aspect to understand about exiting a warp is the fact that you will not exit directly at your exit point.  You will always exit warp in a random direction, 2,500 meters from your actual exit point.  To see this for yourself, do the following:
1. Fly to a location in space that is away from anything else (i.e. warp to a planet at 100km).
1. Drop a container in space (i.e. jettison a single round of ammo or ore).
1. Bookmark the container
1. Warp to a another location in space (i.e. another planet).
1. Warp back to your bookmarked container at 0m.
1. When you arrive at your container, observe your distance from it.  You will always arrive at 2,500m away from the container in a random direction.

This curious effect of exiting warp at a random direction from the actual exit point has two major consequences.  The first is related to how EVE handles geometry of objects in space and the second has to with how exiting warp interacts with interdiction spheres (i.e. bubbles).

1. # EVE Geometry

While in space, all objects have three models that describe their dimensions.  First is the physical model (what you see, represented in white in the diagram).  Most objects are simple, and the three models are actually the same.  Some objects are more complicated though, most notably stations and jump gates.  When you look at a station in space, you will notice that they tend to be very intricate in their physical models with lots of bulges and spires and such.  Although beautiful, these highly complex models are extremely hard to accurately interact with quickly.  For example, detecting when a ship has collided with a model takes a lot more processing time the more complex the model is.  For this reason, CCP has created two simplified models for interaction purposes.  

This second model has been simplified to make processing of collisions faster.  This model is known as the Collision Envelope (shown as Red in the diagram).  The client will detect a “collision” with the object when a ship hits this area.  You will notice this area is fairly similar in shape, but is not nearly as detailed as the physical model.  

The third model is an even more simplified model that represents the area that will show a distance of zero to the object in the overview.  This is know as the Zero Point Envelope (shown in Blue).

- NOTE: This diagram is an approximation of the dimensions of station geometry.  It is simply a visual aid for seeing the various parts of geometry for large structures.  See **Station Geometry** for more accurate details about stations.*

  1. # What you need to know about EVE Geometry
So, why is this knowledge of the geometry of objects in space important?  Simple.  When you warp to zero on an object in space, your Warp Exit Point will be the nearest point on the Zero Point Envelope to your Warp Entry Point.  Remember, you actually exit warp in a random direction 2,500m away from your actual Warp Exit Point.  This means that you can actually exit your warp anywhere from 2,500m inside the Zero Point Envelope to 2,500m away from the Zero Point Envelope.  
This fact is extremely important when you consider the “activation range” of various objects.  For example, you can activate a jump gate if you are within 2,500m of it.  Meaning that no matter where you actually exit, if you warp to zero on a jump gate, you will be able to automatically jump as soon as you land.  

The activation range of a station (i.e. the docking ring), however, is only 500m.  When you warp to zero on a station, you will land within the docking ring about half the time.  The other half of the time, you will land outside docking ring and have to fly toward the station for a while before you can dock.  This can be very significant if you are in a very slow ship (like a battleship).  If there are hostiles outside the station, you can be targeted, webbed and killed before you can travel the distance to the docking ring.

This effect on docking is the primary reason everyone should create an instant docking bookmark for any stations that they frequent, especially if you fly large ships.  The instant docking bookmark needs to be located more than 2,500m INSIDE the Zero Point Envelope AND more than 2,500m OUTSIDE the Collision Envelope.  When set up properly, your ship will always exit warp inside the docking ring and never get “bounced” by the Collision Envelope.   By the way, capital ships appear around a cyno in exactly same way that ships exit warp (except at 5,000m in a random direction from the center of the cyno).  This same bookmark is very useful as a position to light a cyno, as it lets capital ships instantly dock in the station.  

Sometimes, the Zero Point Envelope and the Collision Envelope are very close together (like with acceleration gates).  If you warp to zero on these objects, you can sometimes land within the Collision Envelope causing very strange things to happen.  For example, if you land within the Collision Envelope of a station, your ship will be “bounced” outside the Collision Envelope.  If you are in a very large ship (i.e. battleship, capital ship, etc…) this can be devastating as it could take you several seconds (or even minutes in the case of capital ships) to get back to the docking ring.  If you land in the Collision Envelope of an acceleration gate or asteroid, you will likely become “stuck” in the object have have to spend several seconds or minutes freeing your self.

1. # Exiting Warp and Bubbles
Up to this point, we have assumed that when you warp to an object, you will land at your object.  This is not always the case.  When you are exiting warp, there is an invisible line along your direction of travel that is 150km long and that has your intended warp exit point in the middle.  However, if any part of this invisible line intersects an interdiction sphere (i.e. a warp bubble), your Warp Exit Point will MOVE to the surface of the interdiction sphere.  This means that when you exit warp, you could be a very long way in front of (or behind!) your intended target.  It is for this reason that people almost never warp to zero on any permanent objects in Null/Wormhole space.  They always set up tactical bookmarks that are more than 150km away from common warp to objects (gates, stations, etc…) that are also not in line with anything else.  That way they can warp to a position that is “on grid” with their destination and (hopefully) not inline with a bubble.

1. # Terminology
- Warp Initiation Point (WIP) - The point where the pilot presses the “warp” button.
- Warp Entry Point (WEP) - The point where the ship actually enters “warp”.
- Warp Exit Point (WXP) - The point where the ship is suppose to exit “warp”.
- Warp Exit Envelope (WXE) - The area in which the ship will actually exit the warp.
- Warp Exit Corridor (WXC) - The area in which the ships warp drive will shut down.
- Zero Distance Envelope (ZDE) - The area which will show as zero distance in the overview for an object.
- Collision Envelope (CE) - The area in which a ship will “collide” with an object in space.
- Alignment Time (AT) - The time lapse (in seconds) between the WIP and the WEP.
- Alignment Distance (AD) - The physical distance traveled between WIP and WEP.
