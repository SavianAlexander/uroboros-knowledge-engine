---
title: "Modules"
url: "https://wiki.eveuniversity.org/Modules"
pageid: 888
source: "EVE University Wiki"
categories: ["Fitting", "Game mechanics"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Modules

A **module** in EVE Online is an item that may be **fitted** to, that is, mounted on, a **ship**. Modules either:

- improve the attributes of the ship: for example, an armor plate increases a ship's armor hitpoints;
- grant the ship some extra function: for example, an autocannon allows the ship to shoot other ships; or
- improve the attributes of other modules on the ship: for example, a gyrostabilizer increases the damage done by projectile weapons, including autocannon.

Without modules attached, a ship can do little other than flying around and carrying things in its cargo hold. The collection of modules attached to a particular ship are called the ship's "fitting". With different fittings, a ship can be radically more or less effective, and different module choices can also radically change a ship's function.

This page discusses general mechanics of all modules, regardless of type or size. 

1. # Fitting requirements

  1. # Slots

Each module fits in one of three slot types: **high-powered**, **medium-powered**, and **low-powered**, usually abbreviated to "high", "mid", and "low slots". If an appropriate slot is not available, a module cannot be fitted.

- **High slots** typically mount active modules which are central to a ship's function, such as **weapons**, **cloaks**, and **mining** lasers
- **Mid slots** typically mount **propulsion equipment** and utility modules such as **tackle**, data analyzers for hacking, and so forth; they also mount shield **tanking** modules
- **Low slots** typically mount modules which enhance a ship's mobility, cargo capacity, or damage output; they also mount armor **tanking** modules

Most ships have high, mid, and low slots, but not all do: **freighters** only have 3 low slots, while **shuttles** have no slots whatsoever. Larger ships tend to have more slots in total, though their pattern of slot distribution can vary: the Caldari **Raven** and the Amarr **Apocalypse** both have a total of 19 slots, but their slot layouts are 7/7/5 and 8/4/7 respectively.

  1. # Powergrid and CPU

Every ship with slots has available amounts of "powergrid" ("PG") and "CPU". All of the modules mounted on a ship draw from either or both of these two resources. If a module requires more CPU or powergrid than a ship can supply--taking into account all the other modules already fitted--then it can only be mounted in an "offline" state which will prevent its use (see below).

Powergrid represents a ship's ability to supply basic energy to its modules. Ship powergrid scales with hull size: frigates tend to have tens of megawatts of powergrid, while battleships tend to have tens of thousands. Powergrid is a limiting factor on fitting modules which come in different sizes for differently-sized ships, such as weapons, microwarp drives, and armor plating.

CPU represents a ship's ability to control its modules. Ship CPU scales with number of slots: battleships have more CPU than frigates, because they have more slots, but the amounts involved are in the same order of magnitude. CPU is a limiting factor on fitting modules which can be mounted to hulls of many sizes, such as shield hardeners, damage enhancers, and probe launchers. 

Character **fitting skills** can reduce the powergrid or CPU requirements of some modules, and can increase the raw amounts of both resources available on a ship.

  1. # Skills

Modules have **skill** requirements. Often, more advanced versions of a module require higher levels in the relevant skill. A Tech 1 Overdrive Injector System, for instance, requires only  I and  I, while the Tech 2 Overdrive Injector System requires Hull Upgrades II.

To see if you have the necessary skills to use a module, SHOW INFO on the module and click the PREREQUISITES tab. That will show you the skills needed to make use of the module; these skills are needed both to fit the module to your ship and to enjoy the benefits of the module. If the skills themselves have other skills as prerequisites, then these will also be shown on the PREREQUISITES tab of the module information.

  1. # Hull restrictions

Finally, a few modules are explicitly restricted to specific hulls. The Assault Damage Control, for instance, can only be fitted to **Assault Frigates** and **Heavy Assault Cruisers**, while Interdiction Nullifiers can only be fitted to a narrow range of ships typically used for scouting and spying.

To see if your ship can accept the module, SHOW INFO on the module and click the FITTING tab.

1. # Types and states

  1. # Active and passive

Modules in EVE can be **active** or **passive**.

- Active modules do something or provide bonuses when activated; some but not all active modules draw on the **capacitor** when activated.
- Passive modules cannot be activated and simply provide bonuses or effects when they are fitted and online.

A few active modules still provide some benefits when they are inactive. The Assault Damage Control, for instance, increases a ship's resistance to damage all the time, provided it is fitted and online. When it is activated, it briefly provides a much greater bonus to damage resistance.

  1. # Unfitted

Unfitted modules are in a ship's cargo hold. They do nothing apart from taking up space in the hold.

  1. # Fitted

A fitted module takes up a slot on your ship. If the module has any associated drawbacks or penalties, then they are applied to your ship. Fitted modules can be **offline** or **online**.

  1. # Offline

An offline module provides no benefits and cannot be activated, but also doesn't use any powergrid or CPU. If a module has any drawbacks, then your ship still suffers those drawbacks even if the module is offline but fitted. 

Modules are most typically offline when you have tried to fit modules to a ship beyond its CPU or powergrid capacity. A module also goes offline if it is burned out by **overheating**. You can manually offline a module from the fitting window or by right-clicking its icon in the HUD and selecting the relevant command. Offlining a module frees up any CPU or powergrid that it was using.

In some circumstances, it is useful to offline one module so that you can online another. You might, for instance, travel in a ship with an offlined probe launcher for emergency use if you are stranded in a **wormhole**. When stranded, you could offline some other modules and bring the probe launcher online to begin probing your way back to known space.

Besides the necessary CPU and/or powergrid, bringing a module online also requires 95% of your capacitor. This stops players rapidly onlining and offlining different modules in combat.

  1. # Online

Online modules are fitted and using some of your CPU and powergrid. A passive module that is online is already doing its full job and providing any benefits it will provide. An active module will need to be activated to deliver its full use/ benefit.

  1. # Activated

An activated module is turned on and cycling, and performing its full function. Most activated modules draw on the capacitor each time they start a new cycle, but some (projectile weapons, for instance) do not.

  1. # Overloaded

Most active modules can be "overloaded" or "overheated" when activated (colloquially, most players refer to "overheating", though the game interface prefers "overloading"). Overheating a module increases its power but also builds up heat, which can damage the module and surrounding modules. An overheated module will eventually burn out and go offline if the heat is not turned off.

1. # See also
- **Fitting Modules and Rigs Guide**: sums up the different types of module available in the game.
- **Rigs**: discusses rigs, ship modifications which take up a fourth kind of fitting slot, and use up "calibration" rather than powergrid or CPU.
- **Capital Ship Modules**: modules specific to capital-sized ships.
