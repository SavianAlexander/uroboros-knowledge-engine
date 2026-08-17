---
title: "EVE API Guide"
url: "https://wiki.eveuniversity.org/EVE_API_Guide"
pageid: 3447
source: "EVE University Wiki"
categories: ["API", "Deprecated pages"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# EVE API Guide

This is a quick guide to using the EVE API in your own applications, scripts, and utilities.

This is *not* a guide to programming, setting up and using a webserver, or XML - there are enough of those floating around the internet.  You will need to make sure you understand these before reading this guide.

1. # Introduction to the EVE API

The EVE API is basically a set of calls to web pages on a CCP server that allow you to retrieve information from the EVE game servers, most often something related to a character, corporation, the game map, or the game server status.

Using the API, you can query the server from your own program code. This could be a desktop application, a dynamic web page, or even a command-line script.

As the API uses nothing but HTTP calls and XML responses, you can use pretty much any language you like as long as there's a way to return the source of a web page in it.  This guide will focus primarily on scripting web pages in PHP, as this tends to be the simplest method and is available to just about anyone with access to some webspace (if you don't have access, you can always install a local copy of Apache and PHP on your desktop computer)

  1. # Security

In order to prevent unauthorised access to private character/corporation data, the API uses an *API Key*.  This is a randomly-generated string that essentially works as a password for API calls.  Account owners generate their own API keys through [this page](https://community.eveonline.com/support/api-key/).  That page also informs you of your unique numeric user ID, which is used in API calls instead of your username.  This allows a degree of trust with third-party applications, in that they neither need to know your login name or password.

Note that at time of writing, a new API Key system allowing more granular access permissions was in development, and is discussed [here](https://www.eveonline.com/devblog.asp?a=blog&bid=912).

1. # API Functions

You may also find http://wiki.eve-id.net/APIv2_Page_Index to be a useful third-party reference.

1. # Using the API - Simple Examples

  1. # In Browser

They way to access your account or character information using a web browser, is with the API URLs. CCP is changing the API Keys access format, so the new way to access is as follows. (This will show you how to access, but not how to use it at the moment)

You will need first an API Key with the proper access mask, it depends on what information you want to access to. For example, to access your Account Information use the next URL (Copy and paste, change the XXXXX fields with your information). You need the keyID and vCode.

 https://api.eveonline.com/account/characters.xml.aspx?keyID=XXXXXX&vCode=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

That will return something like this.

 <eveapi version="2">
 <currentTime>2012-03-20 20:21:17</currentTime>
 <result>
 <rowset name="characters" key="characterID" columns="name,characterID,corporationName,corporationID">
 <row name="YourCharactersName" characterID="YourCharactersID" corporationName="EVE University" 
 corporationID="CorporationID"/>
 </rowset>
 </result>
 <cachedUntil>2012-03-20 21:18:17</cachedUntil>
 </eveapi>

Now if you want to access to you Assets List, then use the follow URL.You can get your characterID using the previous example.

 https://api.eveonline.com/char/AssetList.xml.aspx?keyID=XXXXXX&vCode=XXXXXXXXXXXXXXXXXXX&characterID=XXXXXXX

This will return a big list, that looks like this.

 <eveapi version="2">
 <currentTime>2012-03-20 20:39:17</currentTime>
 <result>
 <rowset name="assets" key="itemID" columns="itemID,locationID,typeID,quantity,flag,singleton">
 <row itemID="1005838069096" locationID="60003493" typeID="34" quantity="1" flag="4" singleton="0"/>
 <row itemID="1005922778803" locationID="60004279" typeID="606" quantity="1" flag="4" singleton="1" 
 rawQuantity="-1">
 <rowset name="contents" key="itemID" columns="itemID,typeID,quantity,flag,singleton">
 <row itemID="1005922778804" typeID="3640" quantity="1" flag="27" singleton="1" rawQuantity="-1"/>
 <row itemID="1005922778805" typeID="3651" quantity="1" flag="28" singleton="1" rawQuantity="-1"/>
 <row itemID="1005922778806" typeID="34" quantity="1" flag="5" singleton="0"/>
 </rowset>
 </row>

itemID is a general ID, and it can change in time i.e if items are packaged. TypeID is a unique identifier of the kind of item.

  1. # PHP

A number of third-party libraries are available for PHP programmers, which will do the bulk of the work for you.  For the purposes of these examples, we will be using [Ale](https://sourceforge.net/projects/eve-apiphp/) - make sure you have downloaded this and placed a copy on your webserver.

  1. # C#

Get [EveAI.Live](http://wiki.eve-id.net/EveAI#Downloads) from here

  1. # Visual Basic.NET

Get [EveAI.Live](http://wiki.eve-id.net/EveAI#Downloads) from here

  1. # Python

Get [EveApi](https://github.com/ntt/eveapi) from here. The [apitest](https://github.com/ntt/eveapi/blob/master/apitest.py) file also serves as quite comprehensive documentation on how to use the library. This library is open source and available under the [MIT License](https://en.wikipedia.org/wiki/MIT_License).

1. # Something A Bit More Complicated

1. # Sites of Interest

http://wiki.eve-id.net
