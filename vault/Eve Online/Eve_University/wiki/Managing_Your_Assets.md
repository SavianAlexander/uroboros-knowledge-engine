---
title: "Managing Your Assets"
url: "https://wiki.eveuniversity.org/Managing_Your_Assets"
pageid: 7500
source: "EVE University Wiki"
categories: ["Getting Started", "User Interface"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Managing Your Assets

Notice: Like so many UI elements in EVE, you may experience inconsistencies from what is described here. This page was last updated under Odyssey 1.1.

One of the most significant parts of playing EVE, no matter your chosen profession, is managing your assets. The Assets window is a crucial tool for keeping track of all of your collected ships and items across the galaxy, and the Inventory window will allow you to view any items within a particular station hangar, or the ship you are currently flying. Because of the huge potential amount of data in the Assets window, it is not updated in real time like the Inventory window is, and there is a built in delay of a few minutes before it is refreshed.

1. # API Access
Third party applications with access to AssetList can retrieve and search all of your possessions, including inside containers and ships.

In order to view assets located in Corporation Hangars or Market Orders (see below), a separate Corporation API key type is required.

1. # Containers
The Assets window is able to search containers, as of 2015, but it does not show or search inside the contents of ships. In order to view inside them, right click and Show Contents. A smaller UI window will pop up with a simplified list, which will display fitted modules as well as cargo.

POS living presents another challenge to inventory management, particularly in wormhole space. A Personal Hangar Array has 50,000 m3 of space and does not allow for containers to be manipulated directly inside the array. Assembled containers can be placed, but their inventory tree does not function, and they must be moved to active ship's cargo in order to view or withdraw contents. For POS arrays, filters are greatly more practical unless you have items to "box up".

1. # The Asset Window
  1. # Tabs
- All - Everything you own in the universe.
- Region - A quick contextual filter for assets in your current region.
- Solar System - A quick contextual filter for assets in your current solar system.
- Search - A contextual list of items based on queries. Clicking the Search button with an empty query field will (should!) force the asset list to refresh immediately. This is common after making a market purchase to confirm the item's location.

  1. # Basic Search
- "Navy" will return all named items such as Caracal Navy Issue, Navy Cap Booster 150, etc.
- "Ship" will return all category items classified as a Ship.

  1. # Advanced Search
The Search tab has functionality that differs from most other modal UI windows as it has predictive autocomplete features, like Google Instant, which can suggest the parameters below. When you have personal or corporation assets spread all over the universe as well as numbering in the vast hundreds, cluttering everything up, this feature quickly becomes indispensable.

You may also type three-letter abbreviations of some of the parameters, such as sta: for a station name. Please note that if you are searching by item name, you should include the "type:" parameter to ensure it combines properly with the others.

Parameters include:
- type: matches item type names
- group: matches the group name of items (battleship, mineral, fighter bomber etc.)
- category: matches the category name of items (ship, module, commodity etc.)
- minimum: minimum number of items in a stack
- maximum: maximum number of items in a stack
- metalevel: matches the metalevel of an item
- metagroup: matches the meta group name of items (ie. faction, storyline, officer)
- techlevel: the tech level of item (1, 2 or 3)
- minsecurity: minimum security status of item's location (-1.0 – 1.0)
- maxsecurity: maximum security status of item's location (-1.0 – 1.0)
- security: matches security level, as a text string (high, empire, low, null, zero)
- system: name of the solar system the item is located in. Can overlap with "station:" parameter.
- constellation: name of the constellation the item is located in
- region: name of the region the item is located in
- station: maches parts of station names.
- blueprint: matches either copy or original
(in progress, CCP documentation [available here](https://wiki.eveonline.com/en/wiki/Assets))

  1. # Uses of the Assets List
You can perform the following actions directly from the Assets list right-click menu without being docked in a station. Be aware that the Assets list will not refresh immediately, causing error messages if assets no longer exist in the same state as the list shows.
- Creating contracts
- Repackaging items and containers
- Creating market Sell orders (requires Marketing skill)
- Viewing cargo contents of ships or containers
- Destroying items

These tasks require you to be present in a station
- Moving items between containers or hangars
- Repairing or reprocessing (station service)
- Viewing corporate hangars (roles allow this to be done only in the Corporation tab)
- Stripping a ship of fittings
- Repackaging a ship with rigs

These tasks are not possible with assets in any POS hangar array
- Creating contracts
- Repackaging ships
- Creating market orders

1. # The Inventory Window
The inventory window is made up of three panes: index (sidebar), filters (sidebar), contents.
  1. # Sidebar
The inventory window's left sidebar can be hidden or shown by clicking the left/right arrow above the top-left corner of the contents pane.
  1. ## Index pane
The index pane contextually (if applicable) displays the following category "trees" in order. Nested trees are expandable if there is a foldout arrow on the left side of the list. 
- &#9660; Active Ship
  - Active Ship Bays
  - Active Ship Assembled Containers
- &#9660; Station Ship Hangar
  - &#9660; Docked Assembled Ships
    - Docked Ship Bays
    - Docked Ship Assembled Containers
- &#9660; Station Personal Hangar
  - Assembled Containers
- &#9660; Station Corporation Hangar (if in a player corporation, with an active rented office)
  - &#9660; Hangar Divisions
    - Assembled Containers
- Market Orders (if in a player corporation, with you having appropriate market roles)
  1. ## Index preferences
At the top-left of the inventory sidebar is the heading "Index", next to a 4-line preferences menu icon. The options given in this menu are:
- Always open in separate window
  - By default you can create a new window pane for any container by shift-clicking. This option creates the new window pane when double-clicking.
- Keep filter value between inventories
  - By default the My Filters box will reset itself when you change the container being viewed. This option makes filters persistent.
- Always show full tree
  - By default nested trees are collapsed. This option begins the view fully expended.

  1. # Filters pane
Filters provide a dynamic rule-based way to control what items are shown in the contents pane. This can allow for faster and more powerful viewing options than the UI controls can normally offer.
  1. ## Filter Examples
The basic layout of the Filter creator is: Filter | Boolean | Subfilter(s), with an All/Any rule matching option at the bottom of the modal window. The minus sign to the left of all rows will delete that row. There is no plus sign, simply scroll down. Depending on the filter chosen, the rest of the selection boxes for that line will change.

Crafting rules to create filters involves an understanding of how items are defined as Categories and Groups in the game, and how boolean rules can distinguish them from each other. Charge is a category, and Heavy Missile is a Group which is distinct from Advanced Heavy Missile. The Filters UI doesn't make this abundantly clear because Category is not an option for the first filter box. 

- Ammunition (a default option)
  - Group Is Charge All
  - Match: irrelevant

- T1 Missiles (All)
  - Group Is Charge Cruise Missile
  - Group Is Charge Heavy Assault Missile
  - (etc. there are so many missile types this is quite tedious to do!)
  - Match: **Any**

- T1 Missiles (Easier Method)
  - Group **IsNot** Charge Frequency Crystal
  - Group **IsNot** Charge Hybrid Charge
  - Group **IsNot** Charge Projectile Ammo Charge
  - Group **IsNot** Charge Scanner Probe
  - (etc. there are fewer types of non-missile charges to filter out)
  - Match: **All**

- Meta 3-4 Modules
  - Meta level Greater than 2
  - Meta level Less than 5
  - Group Is Module All
  - Match: All (this filter does not work when choosing Equal to 3 and Equal to 4)

- Repackage Modules and Drones (very useful to avoid error messages)
  - Assembled Is true
  - Group Is not Celestial All
  - Group Is not Charge All
  - Group Is not Blueprint All
  - Match: All (unfortunately Damage is not a filter option!)

- Slot Highs (it is common to separate modules into station containers, but it's not necessary, and not feasible in POS arrays for w-space)
  - Slot type is High Power
  - Match: irrelevant

- Valuable Items (a default option)
  - Estimated unit price Greater than 200,000.0
  - (Change this as your definition of valuable grows over time!)
  - Match: irrelevant

  1. # Contents pane
Here the inventory of a hangar or cargohold will be shown, if any.
  1. ## Toolbar
Above the contents pane are several icons and readouts. From left to right: Volume, quick-filter, next/previous, views.

Inventory and Assets can be viewed in three ways: Icons, List, and Details.
- Icons is a visual layout that is effective in wide windows, as the items will display from left to right, top to bottom. If you recognise items primarily by their icon, this can be a quick way to glance at your holdings. Icons also have visual cue badges for fitting slots, tech level, and item types.
- List is a compact table layout that includes a small icon and several descriptive category columns.
- Details is a very compact table layout with no icon, except for a small badge that indicates tech levels of 2 and above.

The volume meter shows the current cubic meter (m^3) value of the inventory, and also the maximum volume if the current view is a container. The bar fills to visually represent this percentage, and has two shades to represent a drag-and-drop movement that has not been completed.

The next/previous buttons function just like forward/back in a web browser, and keep a limited history of the containers viewed.

Quick-filter offers an alphanumeric matching function based on the inventory contents.

  1. ## Categories
Two categories are hidden by default: Meta Level, and Category. Right click on the column headings in order to Show these columns if desired, then you can also sort by them.
