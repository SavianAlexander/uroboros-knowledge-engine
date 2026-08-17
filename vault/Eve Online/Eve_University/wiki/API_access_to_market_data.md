---
title: "API access to market data"
url: "https://wiki.eveuniversity.org/API_access_to_market_data"
pageid: 17838
source: "EVE University Wiki"
categories: ["Deprecated pages", "Guides", "Trade"]
harvested_at: "2026-08-16 23:22:25 UTC"
---

# API access to market data

Out-of-game EVE data access is provided by CCP through the **EVE Stable Infrastructure** (ESI). However, this access method is not convenient for casual use. Fortunately, third-party services have arisen to provide better access for the casual player. EVE Market data can be accessed through an API provided by [EVEMarketer](https://api.evemarketer.com/ec/). This service replaces a previous service provided by the defunct EVE Central. EVEMarketer API access methods are very similar to those used by EVE Central but different enough that previous calls will not work. These API calls can be used in a spreadsheet (e.g., Google Sheets, Excel) to provide programmatic access to Market Data even for casual users.

1. # API Call construction
[EVEMarketer](https://api.evemarketer.com/ec/) provides an endpoint accepting POST or GET methods and returns data in either XML (/marketstat) or JSON (/marketstat/json) formats. The call requires an item identifier (typeID) and has optional parameters to limit data to either a system (usesystem) or a region (regionlimit). A single call can contain up to 200 different items. By default, the data returned is XML and for all of Singularity. The following method describes how to use the GET access method. The GET call method produces a URL that can be directly entered into a web browser to provide data without any additional tools or knowledge. Users interested in the POST method should be able to construct the request given the GET method construction.

  - GET Examples**
- https://api.evemarketer.com/ec/marketstat?typeid=215 returns the market data for Iron Charge S (typeid 215).
- https://api.evemarketer.com/ec/marketstat?typeid=215,216 returns the market data for Iron Charge S (typeid 215) and Tungsten Charge S (typeid 216).
- https://api.evemarketer.com/ec/marketstat?typeid=215&typeid=216 is an alternative form that also returns the market data for Iron Charge S (typeid 215) and Tungsten Charge S (typeid 216).
- https://api.evemarketer.com/ec/marketstat?typeid=215&usesystem=30000142 returns the market data for Iron Charge S (typeid 215) for Jita (usesystem 30000142)
- https://api.evemarketer.com/ec/marketstat?typeid=215&regionlimit=10000068 returns the market data for Iron Charge S (typeid 215) for Verge Vendor (regionlimit 10000068)
- https://api.evemarketer.com/ec/marketstat/json?typeid=215 returns the market data for Iron Charge S (typeid 215) in JSON format.

  1. # Obtaining the typeID
TypeIDs are unique identifiers specifying an item. There are several ways to get access to this information. Here are a few:

- Use CCP's ESI site. See **How to get ID** for details.
- Fuzzworks hosts a [csv](https://www.fuzzwork.co.uk/resources/typeids.csv) containing all typeIDs and item names
- Fuzzworks hosts an [API lookup for item names](https://www.fuzzwork.co.uk/tools/api-typename-to-typeid/)
- Most websites providing EVE Market data use typeid to reference the specific examples ([EVE Marketer for Iron Charge S](https://evemarketer.com/types/215))

  1. # Obtaining the system and region IDs
The other two parameters, systemID and regionID are also unique identifiers specifying a singular region or solar system in EVE. There are several ways to access this information. Here are a few:

- Use CCP's ESI site. See **How to get ID** for details.
- Adam4EVE hosts a [list](https://www.adam4eve.eu/info_locations.php)
- [Google Docs Spreadsheet](https://docs.google.com/spreadsheets/d/1HkBZ_KvCYQeFf3awm91fmoPdHTBWugvVKpcwZUv7gXM)
- EVEMarketer can specify specific regions or systems. The identifier is available in the url.(Example: [Iron Charge S in Domain](https://evemarketer.com/regions/10000043/types/215))
- main trade hubs: Jita usesystem=30000142, Amarr usesystem=30002187, Rens usesystem=30002510, Dodixie usesystem=30002659

  1. # Constructing the GET API Call
Once you have a typeid and have chosen your area of interest (all of EVE, system, or region), you can place them into a call:
- <nowiki>Basic call form: https://api.evemarketer.com/ec/marketstat?typeid=<typeid><&regionlimit=<regionid>|&usesystem=<systemid>></nowiki>
- Example call for Iron Charge S for all EVE data: https://api.evemarketer.com/ec/marketstat?typeid=215
The complete url can then be entered into a standard web browser, see above for further examples.

1. # XML Market Data Structure
The returned data object contains Market Order information for both Buy and Sell orders. The relevant fields available are:
- volume: Volume of buy or sell orders
- avg: Average buy or sell price
- max: Maximum buy or sell price
- min: Minimum buy or sell price
- stddev: Standard deviation of buy or sell prices
- median: Median buy or sell price
- percentile: 95th percentile buy or sell price

1. # Importing API Call into Spreadsheet
The following instructions are for API calls in Google Sheets, but should be readily transferable to other spreadsheet programs (e.g., Excel).
  1. # Google Sheets Method
Google Sheets uses the IMPORTXML function to make API calls and process XML. This function requires two parameters, the API URL and the XML field to retrieve. The API URL was constructed above (e.g., https://api.evemarketer.com/ec/marketstat?typeid=215). The XML fields available are described by the Data structure above and are specified by the form //<sell|buy>/<field>. The IMPORTXML function can be used in conjunction with cell functions (e.g., CONCATENATE, INDEX, LOOKUP, etc) to automate market data retrieval based on cell references.

  - Examples**

- <nowiki>=importxml("https://api.evemarketer.com/ec/marketstat?typeid=215", "//buy/median") Median buy price for Iron Charge S </nowiki>
- <nowiki>=importxml("https://api.evemarketer.com/ec/marketstat?typeid=215&usesystem=30000142", "//sell/min") Minimum sell price for Iron Charge S in Jita </nowiki>
- <nowiki>=importxml(CONCATENATE("https://api.evemarketer.com/ec/marketstat?typeid=", A1)), "//sell/volume") Volume of sell orders for the typeid in cell A1</nowiki>
- <nowiki>=importxml(CONCATENATE("https://api.evemarketer.com/ec/marketstat?",typeid&JOIN(typeid,$B2:B201)), "//sell/median") Median sell price for each typeid provided in cells B2 through B201. Remember that the API limits you to 200 items per call.</nowiki>
- =importxml(CONCATENATE("https://api.evemarketer.com/ec/marketstat?usesystem=30000142","&typeid="&JOIN("&typeid=",$B2:B201)), "//sell/median") Same as above except looking at Jita specifically and if you aren't using the named variables referenced in the Market Data Spreadsheet linked below.
