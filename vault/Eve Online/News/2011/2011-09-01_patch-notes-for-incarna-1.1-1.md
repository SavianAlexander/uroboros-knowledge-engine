# Patch Notes for Incarna 1.1

- **Date**: 2011-09-01T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-incarna-1.1-1
- **Tags**: #patch-notes

## Overview
Released Thursday, September 1, 2011. The following are the relevant file sizes for client updates:   Windows from Incarna 1.0.1 to Incarna 1.1 is 21.6 MB Windows full client 4.4 GB Mac from Incarna 1.0.1 to Incarna 1.1 is approximately 34.4 MB Mac full client 5.1 GB E

---

Released Thursday, September 1, 2011.

The following are the relevant file sizes for client updates:


- Windows from Incarna 1.0.1 to Incarna 1.1 is 21.6 MB
- Windows full client 4.4 GB
- Mac from Incarna 1.0.1 to Incarna 1.1 is approximately 34.4 MB
- Mac full client 5.1 GB


**EVE Gate (new forums will be open on Tuesday, September 6)**

*New official EVE Forums*


- A new server environment is being deployed to host the new forums.
- A new player forum will be added to EVE Gate and will replace the old forum on eveonline.com. It will include the same forum functionality previously enjoyed by the community, along with additional features: - Simple and advanced search options.
  - An option to choose between normal or compact view for the threads.
  - Ability to “Like” posts and see number of Likes per post.
  - Each thread has an option to "Tag as Favorite"; this will add it to your Favorites page so you can easily find it again and quickly spot any new activity in the thread.
  - A quick reply function that allows you to post a reply to a thread without loading a reply page with full formatting options.
  - A character dropdown list full of handy options, such as sending EVE Mail or going to their EVE Gate profile via one click, or the number of Likes the user has received in total on the forums.
  - RSS feeds for threads and search criteria.
  - DEV, GM, CSM, ISD and External Partner characters have a colored badge overlay on their avatar. Additionally DEV and GM badges have been added on EVE Gate profiles.
  - Forum Settings will now be located on your EVE Gate profile settings page, retaining the usual functionality of toggling corporation/alliance information.
- The old forums will be cast out into space to be frozen in time and remain fully viewable, but in a read-only mode. Threads and posts from the old forums will not be included in the new forums.


*Activity Notifications*


- The Activity Notifications function lets you know when you have interesting activity happening on EVE Gate and EVE Forums. The alerts appear in the notification icons found in your EVE Gate header; as real time popups, and for those moments you are busy looking at another site - you can see the number of new activity in your EVE Gate or Forum browser tab.
- The Mail Icon notifies you when you have new unread mail. Clicking it will take you straight to your EVE mail.
- The Notification Flag shows you how many new activities you have on EVE Gate and the forums. Clicking the flag gives you a dropdown listing your new activities and takes you straight to them. At the bottom of the notification dropdown list you find a link to your Activity Notification page where all notifications are listed by date.
- Players will be notified of the following activities in real time: - When somebody posts on your wall.
  - When somebody comments on your wall post.
  - When somebody comments on a post other character has made on your wall.
  - When somebody posts a reply to a forum thread you subscribe to.
  - When somebody likes your post on the forums.
  - When you receive an event invitation.
  - When you receive new EVE Mail.
- In your EVE Gate profile settings you can customize which notifications you receive.


*Personalized backgrounds*


- You can now choose from a selection of backgrounds in your EVE Gate profile settings. This release includes seven backgrounds: Minmatar, Caldari, Gallente, Amarr,Incarna, Incursion and Tyrannis.
- You can have a different background for each of your characters.
- Players can personalize their EVE Gate backgrounds in their EVE Gate Profile Settings.


**Captain’s Quarters**


- Some visual improvements have been made to the main screens and menu systems within the Captain's Quarters.
- Fixed a rare case where action objects would not be interactable.
- Fixed several potential crash issues with EVE Voice.
- Fixed an issue with fleet voice chat that could prevent people from using voice chat at all.


**API**

*Customizable API Keys*


- Customizable API keys and a new, improved method of accessing the API, were implemented. Please refer to [this dev blog](//www.eveonline.com/devblog.asp?a=blog&nbid=2319) for more information.
- The new API management website is located at [//support.eveonline.com/api](//support.eveonline.com/api).
- The API system will still accept legacy API keys for a limited amount of time.
- Please make sure you update your third-party applications and [create a new API key for them!](//support.eveonline.com/API/Key/Create)


*Contracts*


- Contract updates are now available to third-party applications. For more information, please read [this dev blog](//www.eveonline.com/devblog.asp?a=blog&bid=943).
- Three new pages were added to the API (in both /char and /corp): Contracts.xml.aspx, ContractItems.xml.aspx and ContractBids.xml.aspx.


*Miscellaneous*


- Items in the AssetList and ContractItems will now include a rawQuantity attribute if the quantity in the database is negative. Negative quantities are in fact codes: -1 is a singleton item and -2 is a blueprint copy.
- MarketOrders.xml.aspx will now return all active orders plus all orders issued in the last seven days. An optional "orderID" parameter can be provided to fetch any order belonging to your character/corporation.
- CharacterInfo.xml.aspx now includes employment history.
- WalletJournal.xml.aspx should no longer cause an error when rowCount is high.


**User Interface**


- The “Show Info” window for drones in your ship's drone bay now displays the correct attributes according to your skills.


**Graphic General**


- Resolved a sorting issue which made hair render in front of the ship's hologram in one's Captain's Quarters.
- The Machariel will now be animated in your station hangar view like all other ships.


**Technical**


- Switching ships while docked in a station no longer causes a session change.
- When adding or removing turrets to/from the ship, the hangar and the fitting window view wasn't updating until the next ship change or undock. This has been fixed.
- CarbonIO has been activated on the game client. More information regarding CarbonIO and our future plans can be found [here](//www.eveonline.com/devblog.asp?a=blog&nbid=2332) CarbonIO will continue to work on the server but will not be activated in the client during this patch but is scheduled for a future deployment.


**Localization**


- The German and Russian clients have had several changes made for consistency and linguistic issues throughout the game.
- The confirmation message when abandoning loot now displays the option to not show the message again for the Russian and German clients.
- Some formatting issues in the ESC menu have been resolved for the German client.


**Mac**


- Fixed an issue where NVIDIA hardware would render characters with yellow hands; this fix only affects Snow Leopard as the NVIDIA driver was fixed in Lion.
- Optimizations to VBO (vertex buffer object) should provide a performance boost to AMD systems in some cases.
- An issue where the Jukebox cut off the end of some songs has been substantially reduced in scope, some songs still lose a few seconds at the end though.
- Some memory-related fixes were introduced, significantly reducing the number of crashes due to running the client in high-detail mode.
- A workaround was implemented to circumvent a NVIDIA 9400 crash that was affecting users running OS X Lion.


**Client Update #1 for Incarna 1.1**

Released September 1, 2011

**User Interface**


- The update addresses a loading delay issue with the starmap.
- The update addresses an issue that occurred when boarding a ship from a pod.
- The update addresses an issue where booster penalties would not show up on the fitting screen.


**Incarna 1.1 Client Update #2**

Released September 2, 2011

**Miscellaneous**


- Modules are no longer being offlined when switching ships in a station.
- Changing the ship after accepting a mission broke the bookmark to the agent site. This is no longer the case.
- Ammunition is no longer disappearing at changing ships in a station.


**Incarna 1.1 Client Update #3**

Released September 7, 2011

**User Interface**


- The cargo window will now stay closed after jumping instead of re-opening every jump.
- The cargo window can once again be closed by clicking the cargo button in the HUD when the cargo window is open.
- Fixed the map option "Color by cargo illegality" when opening the map inside a station.
- Right-clicking your ship in the fitting window, while being docked in a station, will once again provide the context menu.
- The Capital Ship Navigation Window has been returned to service while docked.


**Modules**


- In some cases modules would go offline when switching ships in a station due to them being onlined in an incorrect order. This should no longer happen.


**Server changes**

Released September 7, 2011

**Technical**


- The mission journal window is now displaying correctly in space, even after accepting the mission and changing ships.


**Modules**


- Weapon groups will now be preserved correctly when storing ships in a Ship Maintenance Array.
- When fitting a ship using the Fitting Management window, the last slot in each row wouldn't be fitted. This is now resolved and the station engineers responsible have been taught to count using all fingers and toes.
