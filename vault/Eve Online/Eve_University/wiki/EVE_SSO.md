---
title: "EVE SSO"
url: "https://wiki.eveuniversity.org/EVE_SSO"
pageid: 17697
source: "EVE University Wiki"
categories: ["Game mechanics"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# EVE SSO

- Single Sign On** (**SSO**) is an authentication service provided by **CCP Games** for EVE Online. This service allows third-party applications and websites to authenticate players using their EVE Online credentials—thus proving their ownership of the character(s) they are logging in to—while keeping players' login details private from third parties. Crudely, EVE's SSO lets third parties check with CCP that people are who they say they are.

1. # Uses
EVE SSO authentication has found numerous uses. Some include:

- Informing third-party tools about characters' skills and/or assets.
  - **PYFA**, for instance, can use SSO authentication to load your character's exact skill profile and give precise details on how different ship fittings will perform in your hands.
  - **EVEMon**, similarly, can make sophisticated skill plans and advise on **neural remaps** once it can see into your character's head.
  - [jEveAssets](https://eve.nikr.net/jeveasset) can simplify the vast and scattered collections of assets that any long-lived character inevitably accrues.
- Verification of applicants' characters by corporations and alliances. Many organized groups in EVE routinely screen applicants' characters to verify claims about character skills and to weed out spies.
- This wiki's login system!

1. # Mechanics
EVE SSO uses a login procedure usually called "OAuth". Technically there are two types, the original OAuth—OAuth1 or OAuth v1—and the newer OAuth2, which is slightly more secure; this article will collectively refer to both as OAuth, as the differences between them primarily affect developers rather than end-users.

OAuth is a web-standard shared login procedure that is well-established and tested. The nature of the login process means that the username and password are never shared with the destination website, so users can rest assured that their account cannot be compromised and that no additional information beyond what they authorized will be released to the third party tool. The OAuth server maintains control of all of the information and validation.

OAuth is very widely used, but rarely known to users by that name. Most major social website services that allow their users to use their credentials for other sites and tools are based on OAuth, including Google, Facebook and Twitter.

  1. # Detailed Process
When a user wishes to authenticate with a website or application (henceforth both referred to simply as a "tool") that uses OAuth authentication, they trigger a multi-step process between all three parties: the User (typically via their browser), the Tool (which serves as the OAuth client), and the OAuth Server (which hosts the user's actual account).

# The User initiates a request to log in via OAuth/SSO to the Tool
# The Tool Redirects the User to the OAuth Server, with added information:
1. * a client-id that identifies the Tool to the Server (provided by server when the Tool registered previously)
1. * a redirect url that the Server will redirect the User to once they are signed in
1. * any Scopes the Tool is requesting access to for the User's information
1. * a 'state' parameter that helps the Tool identify the User when they return to the Tool, and also acts as an additional safety check
# The Server validates the client-id and the redirect url of the Tool against the registered information in its own database
# If the info is correct, the Server presents a login prompt to the User, along with the list of Scopes requested.
# The User logs in to their account and agrees to the scopes
# The Server redirects the User to the redirect URL of the Tool, and passes along information in the Header of the request that includes a Temporary Token

Up to this point, all of the data sent back and forth has been visible to the user in the URL parameters, both in the URL that sent them to the login screen and the return to the Tool. This is considered insecure, as it could easily be compromised or subjected to a "man in the middle" attack. Because of this risk, the Tool does not yet have full authentication with the Server. In the case of EVE SSO, the Temporary Token provided is only valid for 5 minutes. To get a full Authentication token, the Tool must follow these steps behind the scenes, invisible to the user:

# The Tool constructs a request to the Server with the following information:
1. * Client-ID
1. * Client-Secret
1. * Temporary Token
# The Server validates the Client-ID and Client-Secret against the registered client in the database
# The Server creates an Authentication Token and Refresh Token and sends them to the Tool
# If OAuth2 was used, some additional information about the character is included in JWK format (such as character name and character-id)

The Authentication Token the Tool has now obtained is valid for 20 minutes.

1. # Ending authentication
The Refresh Token the Tool obtains is valid indefinitely, but can be invalidated in several ways:

- The User revokes it on their [EVE Third Party Tools Authorization page](https://community.eveonline.com/support/third-party-applications)
- The User changes their account password: this invalidates *all* Tokens on the account
- The User sells the Character on the Character Bazaar
- The Tool revokes it using the individual Token Revocation process
- The Tool developer deletes the tool's registration on [the EVE third-party developer servers](https://developers.eveonline.com/)
- The Tool developer changes the tool's registration on the EVE Servers in a manner that changes the client-id or client-secret
  - Note: Changing the redirect URL does NOT affect Tokens issued.

1. # References
