---
title: "Overview settings"
url: "https://wiki.eveuniversity.org/Overview_settings"
pageid: 17473
source: "EVE University Wiki"
categories: ["User Interface"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Overview settings

Setting up your **overview** settings is not the most pleasant task to perform. This article will cover this aspect of the overview. Since this is such a tedious job a large number of players use **overview presets** created by other people.

1. # General Concept

The overview is composed of 5 'passes' to figure out if will show an item on the overview or in space.  Each thing in space is narrowed down to a single entity, which is just a single ID in the [Static Data Export](https://developers.eveonline.com/resource).  For example, 25 is the frigate ID.

# **Filters / Types Shown**: This is a set list of items to see if it will be referenced.  If applied to an overview tab, it will show the item on the overview. If applied to a bracket filter, it will show the item in space.
# **Filter / Exceptions**: This will alter the previous list of items.  It can add things based on state, standings, and dynamic events that happen.
# **Appearance / Colortag**: This adds a SINGLE color icon in the bottom right corner to an item/player.  This is an *ordered list*, and the order is very important.  It displays the first icon that matches, and falling all that, shows a neutral grey setting.
# **Appearance / Background**: This again shows a single color as a background only in the overview, not in the filter.  This is also an *ordered list* and can show nuance on a player.  Like if they are neutral but have a negative sec status.
# **Tabs**: Bring it all together, this coordinates a list of tabs with what overview filter is applied to the overview, and what overview filter is applied to the brackets.

Because this is such a complicated concept, the best plan is to steal an existing overview and adapt it for use.  Asking people in game is often the best option before going down the path of making a unique overview.

1. # Viewing Overview Settings

To view all your overview settings, do the following:  

# Click on **the menu icon, which appears as a 4-lined box** () on your **Overview window**. 
# Click on  **Open overview settings**.

You should now see your Overview settings window, complete with six different settings tabs (not to be confused with the actual Overview tabs displayed on the Overview). 

  1. # Editing Overview Settings While Docked

If you are docked, you can still view and alter your overview settings.
- Note:  You cannot load a preset except when in space, which is done by right-clicking on the tab on the Overview itself.

To access your Overview Settings you can either add a shortcut or use a **slash command**.

  1. ## Command

# Go into any chat window.
# Type in: **/open overview settings**

  1. ## Shortcut

# Press .
# Go to the *Shortcuts* tab.
# Within the *Shortcuts* tab, go to the *Window* sub-tab.
# Scroll down and you will find an *Overview Settings* option - set any keybind to this command. 

Now you can use this keybind even when in a station, and you will open the *Overview Settings* window.

== Overview settings == 

The overview settings are grouped to seven groups each of which has its own tab in the overview settings window.

Out of these the Overview Tabs, Tab Presets and Appearance are the most important for setting up the overview.

  1. # The Overview Tabs

This tab allows you to set up to eight different tabs, with eight different overview and bracket proﬁle presets. You will want to take advantage of this. This lets you easily switch between different loaded presets for different situations. Ultimately it's up to you what you want to name each tab. If you import an Overview profile be sure you review these so that you can rename them for your own preferences.

Brackets are the icons you see in space for an item, such as squares for stations, circles for planets, etc. Brackets can be toggled to "Show all", "Stop showing all" (this will default to loaded preset bracket settings), and "Hide all brackets."

There are occasions on which you might want your brackets to show different things than are on your overview: for example, bracket setting with drones shown, while the main overview setting does not show drones. This is because there are often swarms of drones about, which can quickly clog up the overview. 

One example of a time you might want to see drone brackets in space is in missions. You want to warp off, but you don’t know whether your drones are still out. If you have drone brackets set, you can easily see when your drones are no longer in space. Additionally, you can see when someone has drones attacking you in PvP. This can be very useful. 

Again, bear in mind that brackets can cause lag in very large fights - use them at your own risk. 

To create a bracket setting: 

1. Load the particular preset you want to create bracket settings for as your overview preset. For example, you might want drones on your wormhole setting, so you would load **6 - Wormhole** .
1. Add or remove items you do or don’t want to see in space (eg. drones).
1. Save the setting as something you’re going to recognize as a bracket setting. For example, you might save your setting as **6 - Wormhole B** .

  1. # Tab Presets

This section sets the settings for single overview preset. This preset can be used either for overview window or to brackets in space.

  1. ## Types

The types tab is where you select what you want to see on your overview. You can use this tab to select specific things (entities) - if you’re a veldspar miner, you might only want veldspar asteroids and NPC rats. If you’re a PvPer, you might only want ships on your overview, or maybe even just specific types of ships.

There is a "Filter" text box which makes it easy to locate a specific thing(s) (entities) thus saving you from open and scrolling through the various sub-type categories.

    - Asteroid:** Pretty self explanatory - all your different types of asteroids.
    - Celestial:** All your large celestial objects - planets, moons, wormholes, and so on. Also contains beacons (cynosural ﬁelds), biomass (corpses), stargates, wrecks and containers.
    - Charge:** Contains bombs and probes. Bombs are very dangerous - always good to have them on your overview.
    - Deployable:** Includes all personally deployable **Mobile structures** such as Mobile warp disruptors, mobile depots and mobile trator units.
    - Drone:** All your various types of drones. Useful if you want to target drones of any kind.
    - Entity:** Most NPC rats (NPC enemies), various NPC structures and objects as well as a few useless things like billboards.
    - Fighter** Contains fighters.
    - NPC:** CONCORD, faction and navy police and some rats.
    - Orbitals:** Orbital infrastructure, such as customs office.
    - Ship:** Player-owned ships. Usually you’ll have all of these selected, unless you want to target specific types of ships.
    - Sovereignty Structures:** Sovereignty related structures.
    - Starbase:** POS structures and modules - you might use these if you were attacking one, or living in one.
    - Station:** Pretty self-explanatory.
    - Structure:** Upwell structures - player and NPC created and owned stations.

  1. ## States

In the States tab, you can further define what you want to see or not see in the overview. Whilst the Types tab is pretty straightforward, some care has to be taken with the States tab.

States are selected by toggling one of three radio buttons, each one corresponding to the three conditions located on the right of the States window. 

    - Always show** (column on the left) - Entities with this state will always be shown regardless of the display setting of additional states they may have.
    - Filter out** (column in the center)- Entities with this state will be filtered out unless they have additional states that are set to always show.
    - Show by default** (column on the right) - Entities with this state will be shown unless they have additional states that are filtered out (selected by default for all states).

  1. ## Save Button
The **Save** button allows you to save the preset you currently have in the selected tab. It opens a dialogue box that reads "Type in label for the preset". In the text field you can enter the name you want for the preset. The field will auto populate the current name of the preset, which makes for quicker updating and editing of a preset. 

Note that this only saves the preset loaded to the currently selected tab for recall later and doesn't save the rest of your overview settings.

  1. # The Appearance Tab

In appearance tab you can set how entities appear on your overview. This includes color tags on icons and colored background in overview.

  1. ## Colortag

Colortags allow you to set which tags appear or do not appear, and which tags have priority. 

The order of tags in the list dictates which tag is shown if multiple are valid. The tag that is higher on the list overrides tags that are below it. Drag and drop to reorder the list.

Setting colortags correctly is important because they dictate which state you see. For example, if you have **Pilot has a bounty on him** set higher than **Pilot is at war with your corporation/alliance**, you will only see the black skull bounty colortag rather than the red star war target colortag. The consequences of this could obviously be very bad. 

Also note that colortag settings also affect chat channels and brackets in space. Colortags can be set to blink; this is a good idea to make wartargets in local much more obvious, for example. 

Another thing to remember is that changing these settings won’t dictate what you can and can’t see in your overview - you will still see all the things you dictated in the States tab. The only thing you’re changing here is how said things are displayed in your overview, in chat and in space. 

Note that the outlaw tag will not display for a pilot with -5 or lower security status in the local chat window. A pilot will only show as outlaw in local if he has gained that tag for reasons other than -5 or lower security status; such as a criminal or suspect flag, or if he is flagged for aggression against yourself, or flagged for theft against your corp.

  1. ## Background

The Background tab allows you to change the background of items in your overview, as well as the background of icons in space. It doesn’t affect things in chat.

Like in the Colortags tab, backgrounds have priorities. If a pilot fulfills two or more criteria, the highest on the list will take priority. Drag and drop to reorder the list.

You can change the colour of the background of any pilot state. Generally, as backgrounds are quite distracting, many players keep them unchecked except for outlaws and war targets. In a situation where you want to be able to see neutrals or hostiles very clearly, such as in nullsec or wormhole space, it can be handy to keep all backgrounds checked. 

You can also toggle ﬂashing backgrounds. This is where the term “red ﬂashy” comes from - players generally have war targets and outlaws set to a ﬂashing red background. This is useful for highlighting certain pilots in your overview.

  1. # The Columns Tab

Columns let you select which columns you want to see in your overview. Some of them are pretty useless, so you obviously don’t want those columns cramping your style. 

The column order in overview can be changed by dragging the columns in this window. Topmost thing will be used as the leftmost column.

    - Icon:** This is the object’s icon, useful for quickly seeing the difference between a stargate and a station, or a war target and a corp member.

    - Distance:** The object’s distance from your ship.

    - Name:** The name of the object, be it a player name, the name of a station, or the name of a stargate or another item.

    - Type:** Shows what type of ship a pilot is ﬂying, which is a very useful thing to know.

    - Tag:** The tag that a ﬂeet commander (FC) has assigned to an object. Useful when primary and secondary targets are called, although an FC will usually just shout out the name over Mumble. Mostly used for shooting rats, where the FC wants pilots to destroy enemies in a certain order, but doesn’t want to have to call out each target.

    - Corporation and Alliance:** A pilot’s corporation and alliance.

    - Faction and Militia:** Used in Factional Warfare.

    - Size:** The object’s size in meters.

    - Velocity:** The object’s velocity. Very useful in PvP to see enemy ship speeds to determine if they are kiting your fleet, or if they've been tackled by scrams and webs to slow them down, etc.

    - Radial Velocity:** How fast an object is traveling radially (away or towards you). Useful for seeing whether it is traveling towards or away from you.

    - Transversal Velocity:** How fast an object is traveling perpendicular to you in. In theory useful for gunnery pilots in gauging whether a target can be hit or not, and potentially valuable for frigate and interceptor pilots trying to avoid being hit by guns. An object with a faster transversal velocity, at a specific distance, will be harder to hit, and vice versa.Angular velocity is usually much more useful as it translates directly into turret tracking, since it takes into consideration the distance to the object. Angular velocity is the most valuable tab for gunnery pilots.Transversal velocity could still be useful in trying to gauge how the angular velocity could change if the movement direction of the object changes. (e.g.: an object with low transversal velocity could quickly increase its angular velocity by changing its direction to be perpendicular to yours. But if its transversal velocity is already close to its velocity, then it's already moving perpendicular to you, and its angular velocity can only decrease)

    - Angular Velocity:** is an object’s speed relative to you, measured in radians per second. This means that angular velocity takes distance from a target into account, a very important factor when trying to hit something. Even if a ship has a high transversal velocity, it may still have a very low angular velocity because it is far away; meaning it might still be easy to hit. See **turret tracking** for details on turret tracking.

  1. # The Ships Tab

The Ships tab lets you customize what you see when you mouse over an object in space. It also lets you customize the order information is shown in, and the brackets used on either side of each bit of information. To reorder the information drag and drop them in this window.

Again, some bits are useful, and some bits are not. Ship Name, for example, is rarely useful, whereas Ship Type is very useful. This information can be useful when you are looking at a battle while zoomed out, if you want to see all pertinent information when you mouse over different ships.

  1. # The Misc Tab

The Misc tab allows you to reset all of your overview settings and start from scratch. You will want to consider resetting all of your overview settings prior to importing a new overview profile. Be sure to export or save in-game your current settings prior to doing this. 

It also has the option of moving objects that are mentioned in broadcasts to the top of an overview. This can be useful in ﬂeet operations when the FC broadcasts an align command, or the like. The relevant stargate/object would then move to the top of the overview. 

Brackets and target indications are set here as well.

The Import and Export Overview Settings buttons are used to save or import your saved profiles from your computer.

  1. # The History Tab

This tab lists the last 15 overview profiles you have loaded.

There is also a ‘restore’ button, which will restore your overview back to what it was before you loaded the last overview profile, which can be handy if some joker links you a bad overview profile. Please note that this history is only stored in your local settings for that user so we recommend storing profile links you want to keep around in more permanent places such as the in-game notepad or character bio. See **Saving and Sharing your Overview Profile** for further details.

1. # Advanced overview manipulation

Any YAML exported overview can be edited to customize the appearance of the ship information in space. The overview Tabs and in-space bracket text attributes (size, color, bold) can be edited using the procedures found on this wiki page: **Overview manipulation**
Editing the Tabs and in-space bracket attributes will allow for quicker identification of items of interest.

1. # Saving and sharing your Overview Profile

Saving and sharing overview profiles solves makes it possible to grab overview made by someone else or share same overview to your different alts and computers.

  1. # Saving and retrieving the Profile to and from your computer

This is the Export and Import Overview Settings feature.

# Open your "Overview Settings".
# Go to your "Misc Tab" and you will see two buttons "Import Overview Settings" and "Export Overview Settings".  Alternatively you can right click on the Overview Settings mini menu at the top left corner of the window and you will see these two options (along with Delete).
# Click on the "Export Overview Settings" button.
# A pop-up window will appear. You will then select all of the presets you wish to export and you will give the file a name.  There is a "Check All" selection box to make this easy.
1. * Note: the default checked presets are the "General Overview Settings" and your currently loaded presets in your tabs (from 1 to 8, depending how many tabs you have enabled).
# Click on the "Export" button and your Overview Profile will be exported to your computer.
# The file is saved to the default location; for example on a PC, to "Documents / EVE / Overview"  The folder will be created for you the first time you export a profile.
1. * The exported file is saved as a YAML file.  This file can be copied/sent to another source for importing onto a different machine or your own storage.
# By selecting "Import Overview Settings" you will then replace your existing Overview set-up with the .yaml file you select.  Make sure you select the presets you wish to import. There is a "Check All" selection box to make it easy.
# Prior to importing an Overview you should select from the Misc tab the "Reset All Overview Settings" so that your new import doesn't blend with your existing settings which can lead to confusion.

  1. # Saving your Profile in-game

# Open your "Overview Settings".
# Locate the UI element at the top right called **"Share"**.
# Click and drag this to any other text field in-game, such as your Notepad. This creates an Overview Profile link, which works like any other link. This will only include the tab presets that were actually in use in the overview at the time you do this.
1. * If you want to change the text of the link, you can click on the text next to the ‘Share’ element and modify it.
1. * It can be dragged to any text input field in the game, such as MotD, corp descriptions, corp bulletins, notepads, bios, etc., so it should be easy to share with the people you play with, as well as keeping a library of your favorite overview profiles.
1. * By placing the link in your Notepad you can then access your saved Overview Profile on the same character no matter if you have to re-install your game client, or install it on another machine, etc.

Loading an overview only means you are loading that overview profile at that time to your client, but after that you are free to make any changes to the overview without affecting the overview profile the link represents.

The overview profile links are meant to replace your current overview with the linked settings. When accessing or sharing an overview profile, it will only include the tab presets that were actually in use in the overview of the player that created the profile. If you have specific needs, such as importing more tab presets or avoiding the override of global settings, importing and exporting with YAML is the way to go.

The "History" tab in the Overview Settings will contain your last 15 loaded Overview Profiles and when you loaded them last. There is also a ‘restore’ button, which will restore your overview back to what it was before you loaded the last overview profile, which can be handy if some joker links you a bad overview profile. Please note that this history is only stored in your local settings for that user so we recommend storing profile links you want to keep around in more permanent places such as the in-game notepad or character bio.
