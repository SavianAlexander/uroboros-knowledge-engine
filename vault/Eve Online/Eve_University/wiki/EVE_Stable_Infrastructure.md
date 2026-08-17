---
title: "EVE Stable Infrastructure"
url: "https://wiki.eveuniversity.org/EVE_Stable_Infrastructure"
pageid: 15648
source: "EVE University Wiki"
categories: ["Applications", "Needing updates"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# EVE Stable Infrastructure

EVE Stable Infrastructure (ESI) is an API that can be used by **third party applications** to interact with data from the EVE game servers. It replaces CREST and the XML API which were shut down on May 8th, 2018. The data returned by ESI is in the JSON format.

ESI has both public-data and authenticated endpoints, the latter of which require a character to log in via **EVE SSO** to their character account to gain access to information specific to their character or, provided they have the appropriate **corporate role**, their corporation.

CCP has indicated that their goal is to completely replace the **Static Data Export** (SDE) with ESI, but as of September 2023, there are still many missing features. For example, industry recipes still require the SDE.

As a reminder to developers, it is expressly forbidden for developers of third party applications to use them for ill intent

ESI and SSO are commonly used together, however they do have independent features and uses as well. For this reason, they have been split into their own articles. See **EVE SSO** for information regarding the character authentication (and management thereof) aspect. Besides EVE SSO, the **Static Data Export** and **Image Server** might also be useful.

1. # ESI Endpoints
As of March 2025 ESI provides 195 endpoints, 76 of which related to public data and need no character or client authentication, and 119 of which are authenticated as they relate to privileged information about specific characters or corporations.

The general categories these endpoints fall under are:

| Category | Public | Auth | Description |
| :--- | :--- | :--- | :--- |
| Alliances | 4 | General information about Alliances and their member corporations |  |
| Assets | 6 | Inventory details for characters and corporations |  |
| Calendar | 4 | Read and respond to a character's calendar events |  |
| Character | 4 | 10 | Information relating specifically to a character, where it does not fall under any other category. |
| Clones | 2 | Information on a character's clones and their active implants |  |
| Contacts | 9 | Read Contacts lists for characters, corporations and alliances, and edit them for characters. |  |
| Contracts | 3 | 6 | List public, character and corporate contracts, bids placed on them, and items contained in them. |
| Corporation | 4 | 18 | Information relating specifically to a corporation, where it does not fall under any other category. |
| Dogma | 5 | Information regarding Dogma, EVE's system for attributes on items and entities. |  |
| Faction Warfare | 6 | 2 | Public statistics on faction warfare, systems, leaderboards, and a character's statistics. |
| Fittings | 3 | View, create or delete a character's in-game saved fittings. |  |
| Fleets | 14 | Provides endpoints for a complete breakdown of a fleet's composition, and allows managing it externally. |  |
| Incursions | 1 | A list of currently active Incursions and some basic info about them |  |
| Industry | 2 | 6 | System Cost Indices, Industry facilities, and all information about a character's active industry jobs. |
| Insurance | 1 | A list of insurance prices for all classes of ships. |  |
| Killmails | 1 | 2 | Retrieve killmails relating to a character, or all details on a killmail for which you have the appropriate information. |
| Location | 3 | View whether a character is online, what they're flying, and where they are located. |  |
| Loyalty | 1 | 1 | List offers available from a provided NPC Corporation's LP Store, and a character's available LP. |
| Mail | 9 | All actions related to viewing, sending and deleting in-game mail for a character. |  |
| Market | 6 | 5 | Market orders and histories, as well as a character or corporation's specific orders. |
| Planetary Industry | 1 | 3 | Details on a character's planetary colonies and their layouts, as well as public information on PI Schematics. |
| Routes | 1 | Use the game's algorithms to calculate a route between two systems |  |
| Search | 1 | Perform a search on the provided string against the chosen categories. If for a character, will also search private things the character can see. |  |
| Skills | 3 | Information on a character's attributes, skills and skill training queue. |  |
| Sovereignty | 3 | Lists of sovereignty campaigns, systems and structures. |  |
| Status | 1 | Status of the game: Whether it's running, what version, and how many players are logged in. |  |
| Universe | 29 | 1 | Just about all general public, static data in the game. |
| User Interface | 5 | Allows opening certain UI windows for a character if they are logged in to the game. |  |
| Wallet | 6 | Character and Corporation wallet balances and transactions. |  |
| Wars | 3 | Details on all wars that have happened in the game, including their killmails. |  |

1. # Examples
To get a list of all alliances in EVE, the  <code>alliances</code> endpoint can be used. It lists the alliance ID of all alliances. Since it is a public endpoint, it is even possible to a look at it in the browser, although the data comes is in machine-readable JSON: https://esi.evetech.net/alliances

Some endpoints also support parameter in the URL. For example the type endpoint <code>universe/types/{type_id}/</code> returns information about a type ID. The rifter has type ID 587. To look up information like its description, the <code>{type_id}</code> part in the URL is replaced with the type ID. The full URL would then be https://esi.evetech.net/latest/universe/types/587/  https://esi.evetech.net/universe/types/587

If possible, CCP requests that users add a descriptive user agent to any ESI request, including a contact email, so that they can be contacted instead of being banned for e.g. causing too much load on the ESI servers. 

1. # Tips & Tricks
ESI endpoints use a Token system for rate limiting [Tokens on a Sliding Window refresh](https://smudge.ai/blog/ratelimit-algorithms#sliding-windows) - each hit on an endpoint uses up a token, and if attempted too often (usually at a rate faster than the cache time of the endpoint), the caller will be limited until the next window refresh passes and tokens are returned.

More information on the rate limiting can be found in the [documentation](https://developers.eveonline.com/docs/services/esi/rate-limiting/).

EVE uses a lot of 'ID's, that are unique for things. Ships, players, corporations, systems all have unique IDs.  Most IDs are arranged in 'Ranges' as well. Comparing IDs against these ranges to find out what type of ID it is.  https://developers.eveonline.com/docs/guides/id-ranges/ has these ranges listed out. Figuring out what an ID is can answer many questions of what ESI to find out what it is. There are two very fast ways to find Names for IDs as well. Linking a thing in chat, then hit enter, then right click, and copy. This will put the URL code in the clipboard.  Alternately, go to a site like https://zkillboard.com/ and the ID will be at the end.  Ex: https://zkillboard.com/ship/22460 the Eris id is 22460. See also **How to get ID**

1. # Resources For Developers
There are a number of resources online for developers looking to begin using ESI, many of which also cover SSO for authenticating endpoints.

| - | https://developers.eveonline.com/docs/ | Community-maintained documentation for ESI. |
| :--- | :--- | :--- |
| https://developers.eveonline.com/api-explorer | CCP's front-end User Interface for "playing" with ESI and discovering what the various endpoints can do. |  |
| https://github.com/esi/esi-issues | Official Git Repository for tracking issues and requests for ESI. |  |
| https://github.com/esi/esi-issues/issues/1103 | A specific issue on the above repository, that compares ESI to the information available in SDE. |  |
| https://community.eveonline.com/news/dev-blogs/introducing-esi/ | Original Announcement introducing ESI. |  |
| <s>https://github.com/devfleet/awesome-eve#developer-tools-resources-and-apis</s> | ARCHIVED (2025-06-20) Community-maintained list of resources and tools to work with ESI. |  |
| https://developers.eveonline.com/docs/community/ | Community tools and Services |  |
| https://forums.eveonline.com/t/3-3-0-gesi-google-sheets-esi-library/13406 | GESI - A library for working with ESI in Google Sheets |  |
| https://www.fuzzwork.co.uk/2017/03/14/using-esi-google-sheets/ | A different guide on working with GESI (see above) |  |
| https://web.archive.org/web/20190310221844/https://wiki.zansha.space/index.php/SSO_Authentication_in_Microsoft_Power_Query | Information on working with ESI in MS Excel with Power Query (archived webpage) |  |

1. # Patch History

1. # External links
- Dev blog: [EVE Evolved: The Future of EVE’s API](https://www.eveonline.com/news/view/eve-evolved-the-future-of-eves-api) (2025-02-27)
- Dev blog: [ESI Delivered: The Next Chapter](https://www.eveonline.com/news/view/esi-delivered-the-next-chapter) (2025-08-26)

1. # References
