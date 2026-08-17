---
title: "EVE UNI Mapper"
url: "https://wiki.eveuniversity.org/EVE_UNI_Mapper"
pageid: 17624
source: "EVE University Wiki"
categories: ["Applications", "EVE University Services", "Exploration", "Wormholes"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# EVE UNI Mapper

- Wanderer** is a free and open-source wormhole mapping tool. This tool allows groups of players to share mapped wormhole connections, intel, and cosmic signature information.

Mapping is essential to coordinate EVE University communities' scanning and exploration. EVE University hosts a private Wanderer and was introduced in February 2025 as a replacement for our old [Pathfinder](https://pathfinder.eveuniversity.org/) tool.

1. # Accessing the mapper
# Go to https://wanderer.eveuniversity.org/maps
# Use SSO login and login EVE Online account.
# Select the Eve Uni General map.

1. # Reading the map
The map is made of systems of any **security level**, and the connections between them. The map will show some of their information in compact form. To see the complete set of information about the system, select it on the map and look at the adjacent panels.

  1. # Connections
Connections between systems will change shape and color depending on their properties. These are user-defined and rely upon capsuleers to specify this information by right-clicking on the connection on the map.

- Wormhole size limit is indicated by a letter on the wormhole connection
- Gate Connections are straight with green cores
- Reduced and critical mass wormhole connections have yellow and red cores
- End-of-life (EOL) wormhole connections have purple outlines

Clicking on the connection gives an overview of the tracked characters passing through the wormhole, and the total mass that has gone through.

1. # Managing information

  1. # Adding Systems
There are two ways to add systems.

# Automatically by Wanderer as they are jumped into (only works if your character is tracked)
# Manually create systems by right-clicking on the map

To move a system on the map, left-click and hold the wormhole, then move your mouse.

To select multiple systems, hold  while dragging your mouse.

  1. # Adding Connections
After a system has had another system added to it with a wormhole connection this can be linked to a signature in that system. Simply click the "leads to " attribute on the WH signature and select the corresponding system once the new system is present. Setting this will automatically add mass and size limit info on the connection if the wormhole was not K162.

This will only work if the two systems are already connected.

Wormhole connection health should be subsequently verified and set by right-clicking the wormhole connection. This way you can set the mass criticality and end of the lifetime of the connection. EOL connections are automatically deleted 4h 15m after the status is set. The "save mass" option is for informing other map users to not waste the mass of this wormhole.

  1. # Adding Signatures
First, make sure the correct system selected in Wanderer. Signatures can be added imported in bulk or individually. It is recommended to import them in bulk as it is much faster and easier to keep the system up-to-date. Pasting signatures directly into the signatures window will update signatures immediately. Use the signature reader to check updates before applying them.

To quickly bulk import signatures:

- Make sure the correct system is selected in Wanderer
- Copy all signatures ( +  then  + ) from the in-game scan window
- Paste the signatures ( + ) into the signature pane

Using the signature reader:

- Make sure the correct system is selected in Wanderer
- Open the signature reader from the top right of the signatures pane
- Copy all signatures ( +  then  + ) from the in-game scan window
- Paste the signatures ( + ) into the signature reader

If a signature already existed in the system, the "Last Updated" timer will reset when the signature is updated. A signature that was not copied (i.e. it has expired) will not have its timer updated.

Pressing ( +  allows for rolling back to a previous record of signatures. Useful if a signature is accidentally deleted or the wrong system's signatures are imported. You can also use the red undo button. However, you can only do this in the first 10 seconds of making the edit.

Preexisting signatures can also be edited or deleted in the signatures panel. Simply double click the signature, change the attributes you want to, and then press Save.

  1. # Adding Structures
Structures can be added to a Wanderer widget by bulk importing from D-Scan. The widget is disabled by default, and you can enable it by going to Map Settings > Widgets. You can then update the structure information by clicking on the edit button. You can change the status of the structure, the owner, and add notes. Only Upwell Structures should be added. If a POS is notable (i.e. has a warp-in trap) it should be noted in the system description, opened by double clicking the system on the map.

To bulk import structures:
- Make sure the correct system is selected in Wanderer
- Click the "D-Scan Reader" icon in the top right of the structures panel
- Copy everything ( +  then  + ) from the in-game D-Scan window
- Paste ( + ) into the Structures widget, or press the blue *add structure info* button

Due to the browser based nature of Wanderer, multiple bulk imports can occasionally be needed to add all structures on D-Scan. Repeat bulk imports of the same D-Scan will add missing structures from previous imports.

1. # Available tools and intelligence

One of the core features of Wanderer is that it provides a variety of intelligence about the local environment in a readily available manner. More specifically, when inspecting any given system, you are provided with the number of Ship & Pod kills. There are also links to [DOTLAN](https://evemaps.dotlan.net/) and [Anoikis](https://anoik.is/) located in the widget containing the system name and security status. Likewise, a truncated version of the killboard showcasing recent ship/pod kills for that system is displayed alongside the other widgets.

You can also use the routes widget, and set Thera as a destination to find the fastest routes leading there. Even if you do not have a direct connection to Thera, as long as you have a connection to a Thera connected system, a route will be displayed. (See below.)

1. # Personalizing

You can change certain aspects of how information is presented or handled on the mapper. These settings will only apply to you.

The map setting can be changed by clicking the "settings" button on the bottom right corner of Wanderer. This opens a menu with the following options:
- Common - Has the "Show Minimap" setting
- Systems - Highlight certain system types, auto-select splashed
- Connections - Thicker connections, delete connections to linked signatures
- Signatures - Link signature on splash, show unsplashed signatures
- User Interface - Compact bar menu, background pattern, soft background
- Widgets - Able to select which widgets you want to see
- Themes - Change the theme to Pathfinder or Default.

The widgets can be rearranged by dragging them from the top, or resized by dragging their corners.

1. # Routes

In addition, the mapper can look up the shortest routes to your favourite locations from a selected system. Use the Routes widget to add and save routes to specific maps.

1. # Creating maps
Pilots can create private maps in addition to the preexisting corporation maps, however this may only be done on the [public version of Wanderer](https://wanderer.ltd/). To create a map click the "Create Map" button Maps page (accessible from the sidebar). Private maps can be shared with a limited number of other players.

  1. # Map Options
  1. ## Scope
The types of systems automatically added to the map can be limited by the map maintainer.

- All - Every connection jumped will be automatically added
- Wormholes - Only wormhole connections are added
- Stargates - Only stargate connections are added
- None - No connections are automatically added, but systems and connections can be added manually

Pilot tracking has its flaws; Jump cloning, getting podded, or using Filaments can be misinterpreted as wormhole connections.
