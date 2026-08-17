---
title: "Anchoring structures"
url: "https://wiki.eveuniversity.org/Anchoring_structures"
pageid: 11907
source: "EVE University Wiki"
categories: ["Structures"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Anchoring structures

This article covers the basics of anchoring an **Upwell structure**.

1. # Preparations
In order to anchor a structure you'll need the role of **Station Manager**, alternatively be a **Director** or **CEO** of your corporation. Additionally the role of **Config Starbase Equipment** is needed to manage these structures in the **Structure Browser**.

In order to anchor a structure, such as a **citadel**, you'll need a ship with an appropriately sized cargo hold or fleet hangar, the right roles and a suitable spot to anchor your citadel.

  - Citadels:**
- The medium **Astrahus** is 8k m3 packaged and fits in **Blockade Runners**.
- The large **Fortizar** is 80k m3 packaged and fits in cargo-fitted **Orca**s.
- The extra-large **Keepstar** is 800k m3 packaged and fits in **Freighters**.

1. # Placement

  1. # Restrictions
While you can anchor these structures mostly anywhere, there are a few restrictions both to which systems can have them and where (in space) you can place them.

- Citadels  be anchored in shattered wormhole systems (including **Thera**).
- Citadels  be anchored in [starter systems](https://support.eveonline.com/hc/en-us/articles/203209712).
- Citadels  be anchored in **trade hubs** (Jita, Amarr etc.).
- Citadels  be anchored in deadspace pocket.
- Citadels must be placed between 50-75km away from the anchoring ship dependent on citadel size.
- Citadels must be anchored at least 1000km away from an existing station, citadel or asteroid belts.
- You can move the anchoring position on the x and z axis. To move the position on the Y-axis, move the anchoring ship.
- Anchoring a citadel at a moon is possible but there is only a small area where it is considered valid placement (this is due to the old POS-anchoring mechanics as shown [here](http://imgur.com/ONsYLBP)).

  1. # Placing the Structure
Once a location is selected you can begin by right-click the packaged structure and selecting **Launch for Corporation** from the structure's context menu.

From the **Deployment** menu you can now move the outline of the structure around and rotate it. As structures such as citadels cannot be unanchored or repositioned care should be taken to ensure the citadel is in an optimal position, once finished proceed by pressing the **Position** button.

  1. # Setting up the Name and Permissions
In the final menu you are now asked to set the **Structure Name**, and **Profile**. Profiles define the permissions allowed to different groups or individuals such as docking permissions however these are configured in the **Structure Browser** and new profiles can be assigned at anytime with the appropriate roles/permissions.

1. # Anchoring timer (a.k.a. time to build)
After Deployment, anchoring will not start until an initial **15-minute **vulnerability**** has passed. Once the Anchoring is in progress, the structure cannot be attacked until the anchoring completes (usually 24 hours), and becomes vulnerable again and a **Quantum Core** must be inserted to begin a **15 minute repair timer**. When the repair timer finishes, the structure gains its shields and armor and becomes ready to fit.

The order of events for anchoring is:

# Place the structure.
# A **15 min Repair Timer** occurs, during which the structure can be destroyed outright
# A **24 hour Anchoring Timer** *(Longer in Sov Null if you do not own the space)*, during which the structure is invulnerable
# The structure then enters the **<nowiki/>'No Core**' state, in which it only has Hull HP and is vulnerable to immediate destruction
# When the Core is inserted, another **15 Min Repair Timer** is begun, during which the structure still only has Hull can also be destroyed in its entirety
# When the insert core repair window is finished, the structure enters the **'Low-Power**' state
# When a Service Module is onlined (with fuel) the structure enters the standard **'Vulnerable**<nowiki/>' state (see **Vulnerability** for more information on structure states)

  1. # Anchoring in Sov Null
If a citadel is anchored in a Sov Null system which isn't owned by your alliance the anchoring will take an extra 24 hours per level of Strategic Index (not to be confused with Activity Defense Multiplier which is linked to the Strategic Index but not the same thing) for that system. So for a system with zero Strategic Index the anchoring would take the standard 24 hours; but a system with a Strategic Index of 3 would take 96 hours (24 hours + 3x(24 hours)).

In addition to that, if a systems Activity Defense Multiplier is higher than 4.0, only members of the alliance claiming the system will be able to start anchoring medium Upwell Structures (Astrahus, Athanor or Raitaru). Any larger Upwell structures may still be anchored by anyone in such a system.

== Final Steps == 

The structure is now placed, the Anchoring Timer and its subsequent 'repair' timer has been passed, the station will now say "Low Power" - There are a few more steps to do at this point.

  1. # Coring an Upwell Structure

Upwell Structure's require a Structure Core to be added in order to come online. This core can only be added after the Structure has undergone a 24 hour anchoring period and a 15 min repairing timer, in which it was vulnerable to destruction.

To core a structure the following must be done:

# Dock with the Structure with the Core in a ship hanger
# Take control of the Structure
# Open the Inventory for the Station - just like you would when flying a ship in space (alt+c is the default hotkey)
# Drag the Core into the Core Bay of the Structure itself

  1. # Fueling Structures and Onlining Modules
If there are no Service Modules online, then the Structure will be in a Low-Power state. Onlining a Service Module requires Fuel Blocks, such as Hydrogen Fuel blocks. There is no requirement for a specific type of Fuel Block, so use which ever one is cheaper.

To online a Module you must have enough fuel present in the Fuel Bay of the structure to run the module for 3 days of operation. This amount changes based on the particular service module.

You can add Service Modules, Rigs, and Weapons to a Structure by opening the Fitting Window after Taking Control of the Structure. Just like fitting a ship, you drag the modules from whatever hanger bay the are part of and add them to the Structure (You can even save the Structure fits in your fitting window)

The Fuel Blocks must be present in the Fuel Bay of the Structure.Move the Fuel Blocks from whatever ship or personal hanger they are in into the Fuel Bay for use. You can access the Fuel bay in the same manner as the Core Bay when in control of a station - open the Inventory window (alt+c is the default hotkey)

You can get a rough idea how much fuel will be needed per day from the Fitting Window as well.

1. # Adjusting Access

Even though you set up an initial profile when anchoring the structure, you may wish to change this or add new ones. You can do this through the Structure Browser, which can be found by going to your Neocom > Utilities > Structure Browser

Select My Structures tab then the "+ New Profile" button at the bottom. Name the profile.

On the right side of the window, select the structure you want to apply the profile too, and add assign the profile to it.

From here, per profile, you can assign permissions such as docking, ability to take control, ability to use various Service Modules, the market tax, and more.

1. # Reinforcement Timer

As the structure owner, you can set the median time a structure can come out of Reinforcement - with an  understood jitter of +/- some hours. (The amount differs between station size and security status of the system). 

When first anchoring a structure a reinforcement timer is set. You can change this timer through the Structure Browser, after selecting a structure you have the ability to set. Do note however, that such changes will not take affect for 30 days (need to verify this timing window)

1. # Decommissioning / Un-anchoring
To remove a structure, you must start the Un-anchoring process from the Station Browser.

Select the station, and right click on it, selecting "Decommission"

You can also do this from the station itself, by taking control and right clicking your capacitor and selecting "Decommission".

This begins the 7 day period before the station can be picked up. 

1. # See Also
- [Upwell Structure Deployment and Unanchoring](https://support.eveonline.com/hc/en-us/articles/208289335-Upwell-Structure-Deployment-and-Unanchoring)
- [Structure Management](https://support.eveonline.com/hc/en-us/articles/208289605-Structure-Management)
