---
title: "How to get ID"
url: "https://wiki.eveuniversity.org/How_to_get_ID"
pageid: 21144
source: "EVE University Wiki"
categories: ["API"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# How to get ID

In EVE Online all characters, structures, corporations, alliances, item types, and other things have a unique identifier (ID). There are multiple ways to find these identifiers.

1. # API Explorer
API Explorer can be used to easily find IDs for agents, alliances, characters, constellations, corporations, factions, inventory_types, regions, stations, and systems.

# Go to https://developers.eveonline.com/api-explorer#/operations/PostUniverseIds
# In the Body block input the name of the thing you are looking for in quote marks surrounded by brackets. If you want to search for multiple things at once multiple names can be placed in brackets separated by commas. The names must be typed exactly right.
# Press "Send API Request".

For example, if you want to search for Rifter and Jaguar your search string would be `["Rifter", "Jaguar"]`.

The response from ESI, in the response block would be

 200 OK
 
 {
   "characters": [
     {
       "id": 187399875,
       "name": "Rifter"
     },
     {
       "id": 300556952,
       "name": "Jaguar"
     }
   ],
   "inventory_types": [
     {
       "id": 587,
       "name": "Rifter"
     },
     {
       "id": 11400,
       "name": "Jaguar"
     }
   ]
 }

From this, you would see that the ID for the ship "Rifter" is 587 and for ship "Jaguar" is 11400. It also tells us that there is a player named "Rifter" with id 187399875 and a player named "Jaguar" with id 300556952.

1. # In game links
This method works for acquiring IDs of all the things you can link to in chat. This includes specific deployed structures, contracts, rats, items, players and more.

# Generate link ingame. Usually, this is done by dragging the image of the thing from the info window into the chat input.
# Select the link ( - ), right click the chat input, and select "Copy Selected With Formatting".
# Paste to out of game text editor.
# Grab the ID

For example, if you do the first three steps from above to Gravity Well citadel you will get the following:
> <code><nowiki><a href="showinfo:35833//1021628175407">Boystin - Gravity Well (The Graduates)</a> </nowiki></code>
From this, you can get two IDs. 35833 is the ID for Fortizar item type while 1021628175407 is the ID for this specific deployed structure.

The link very often contains two IDs. One ID for the type of the thing and another ID for this specific instance of the thing.

1. # Third party sites
Many third party EVE sites will include the ID in their url when you look up info on them.

Some examples:
- https://zkillboard.com/character/94849044/ - The ID of this character is 94849044.
- https://evewho.com/corporation/917701062 - The ID of this corporation is 917701062.
- https://everef.net/type/17038 - The ID of this rat is 17038.
- https://www.adam4eve.eu/structure_history.php?id=1021628175407 - The ID of this specific structure is 1021628175407.
- https://evemarketer.com/types/44992 - The ID of this item is 44992.

Fuzzwork also has a simple API for finding IDs for items https://www.fuzzwork.co.uk/tools/api-typename-to-typeid/

1. # Scripts
With basic programming skills, you can make scripts that find and display IDs for various exotic things like dogma effects, graphics effects, bloodlines, market categories, and others. This is done using multiple **ESI** endpoints or with the help of static data export. How this is done is beyond scope of this article and is left as an exercise to the reader.

1. # References
