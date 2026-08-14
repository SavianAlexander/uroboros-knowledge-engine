# EVE Evolved: The Future of EVE’s API

- **Date**: 2025-02-27T13:30:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/eve-evolved-the-future-of-eves-api
- **Tags**: #development-updates, #eve-evolved, #news

## Overview
Enhancing ESI for a better third-party ecosystem.

---

EVE Online has always been more than just a game - it’s a vast ecosystem where player ingenuity thrives. A crucial part of that ecosystem is **the EVE Swagger Interface (ESI)**, the official RESTful API that empowers third-party developers to create tools, apps, and services that enhance the EVE experience. Whether it's market analysis, fleet management, industry logistics, or intel gathering, ESI plays a key role in how players interact with the game - both inside and outside New Eden.


## What is ESI?


ESI is a scalable RESTful API with SSO authentication and read/write capabilities. In practice, it powers thousands of applications, serving as the backbone of EVE’s extensive third-party ecosystem.

The third-party development community has built a powerful suite of tools that extend EVE’s gameplay, foster innovation, and even shape in-game economies. Market and trade tools like [EVE Market Browser](https://evemarketbrowser.com/region/0/type/44992) and [Janice](https://janice.e-351.com/) help traders track market trends, optimize logistics, and compare buy/sell orders in real time. Corporation and alliance management platforms such as [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) automate recruitment, permissions, and access control for player organizations, ensuring smooth functionality for massive alliances. Intel and mapping tools like [DOTLAN](http://evemaps.dotlan.net/) and  [RIFT](https://riftforeve.online/) support strategic movements and enemy tracking, while industry tools like [Fuzzworks](http://www.fuzzwork.co.uk/) and [Adam4EVE](https://www.adam4eve.eu/) assist with blueprints, asset management, and production chains. Even beyond standalone applications, ESI supports integrations like the [EVE Online Excel add-in](https://www.eveonline.com/eve-academy/excel-add-in), which provides seamless access to in-game data for planning and analysis.

ESI is massive in scale. Over 2,350 active third-party applications rely on it, with 42% of active EVE players having at least one character authorized in an ESI-based app. The API handles over 350,000 requests per minute, powering countless player-made resources and dashboards. The sheer volume of traffic to ESI-powered websites is immeasurable - if you’ve ever used a community tool for intel, trading, or planning, you’ve likely interacted with ESI. From trade hubs to war councils, from solo industrialists to massive coalitions, ESI is an essential part of EVE Online’s metagame.

This dev blog takes a closer look at ESI today, the challenges it faces, and the steps being taken to ensure a better future for third-party developers and the players who rely on their tools.


## History Lesson


APIs have been an integral part of EVE Online for over a decade, allowing players to extend the game beyond the client and into a vast ecosystem of third-party tools. The EVE Swagger Interface (ESI) is the latest evolution, replacing its predecessors, the XML API and CREST. ESI provides both public and authenticated endpoints, with the latter requiring login via EVE Single Sign-On (SSO) to access character or corporation-specific data.

The launch of the XML API was groundbreaking. At the time, no other game offered such a deep level of programmatic access to its data. Players used it to build some of EVE’s earliest third-party tools, from character planners to market aggregators. There were significant limitations, however. It was read-only, slow to update, and the documentation was lacking.

To address these issues, CREST was introduced, offering a RESTful interface and faster access to live simulation data. However, CREST lacked consistency and scalability, making it clear that a more robust solution was necessary.


## Enter ESI


Built on Swagger (now [OpenAPI](https://swagger.io/)), [ESI](https://www.eveonline.com/news/view/introducing-esi) aggregates API specifications from multiple Kubernetes services into a unified API, handling routing, authentication, input/output validation, and more.

ESI’s introduction coincided with Project Sanguine and the first iteration of EVE Portal in late 2016. These projects laid the foundation for a more advanced server architecture within EVE Online and introduced a message bus paradigm that improved real-time data flow between services. As usage evolved, a higher-performance protocol was needed, leading to the integration of gRPC for faster serialization and communication.

This shift [paved the way for Quasar](https://www.eveonline.com/news/view/introducing-quasar), a technology designed to [**further modernize EVE’s backend**](https://gdcvault.com/play/1027755/Online-Game-Technology-Summit-Quasar) with gRPC, event-driven messaging, and microservices. From the early days of XML APIs to the modern era of ESI, Kubernetes, and Quasar, EVE Online remains at the forefront of game-integrated APIs.

Support for third-party development continues to evolve, and as you’ll see next, there’s still work to be done to ensure that ESI remains robust, reliable, and future-proof.


## Recent Developments in ESI


As you can imagine, there is a long list of improvements planned for ESI. However, before implementing changes, a thorough evaluation of the platform’s current state is necessary, not just in terms of how it was designed to function but how it actually operates today and where it is lagging behind in the EVE ecosystem. 


## The First Step: Quasar Integration


ESI predates Quasar, and while communication exists between them, deeper integration could unlock significant improvements. Currently, ESI relies on RabbitMQ, which limits it to handling only requests rather than processing real-time game data. For example, location data requests (“Where is character X?”) are cached for five seconds to enable mapping tools to track movement. If ESI could receive real-time notifications when a character changes solar systems, it could invalidate the cache dynamically instead of relying on fixed intervals.

However, integrating Quasar more fully presents challenges. The transition requires migrating remaining ESI requests to Quasar Protocol Buffer (protobuf) requests, a major undertaking that involves remodeling parts of the EVE universe into protobuf messages. Some of this work has [**already been completed**](https://github.com/esi/esi-issues/issues/1225) as part of feature improvements, but further progress is needed to ensure full compatibility.


## ESI Bookmarks: The not-So-Temporary Blackout


When the new bookmark system was launched in 2019, it introduced an ACL-based sharing system that conflicted with ESI. As a result, esi-bookmarks were [“temporarily” disabled](https://developers.eveonline.com/blog/temporary-blackout-of-esi-bookmarks).

Upon further review, it became clear that esi-bookmarks would need a complete rebuild to function within the updated system. Given the scale of this effort, a [decision](https://developers.eveonline.com/blog/the-return-of-the-developers-blog) was made to [shut the ESI bookmark endpoints down permanently](https://developers.eveonline.com/blog/deprecation-and-impending-removal-of-esi-opportunities-and-esi-bookmarks). Future reimplementation remains a possibility, but this is definitely a long-term decision. 


## Market History and Its impact on the Monolith


ESI handles an immense volume of traffic, which is typically manageable. However, the Market History endpoint posed a unique challenge.

The endpoint provides a 500-day history for a single item in a single region, cached downtime-to-downtime. If the data is unavailable in cache, it pulls directly from market nodes in Tranquility (TQ), creating additional strain.

When originally designed, the endpoint’s purpose was to mimic the in-game market history graph.

However, due to the sheer number of non-cached requests – across 70 regions and thousands of items – server load became excessive. Compounding the issue, malformed requests (such as “What is the market history for Fedos in Abyssal Space?”) caused unnecessary database lookups, further increasing load.

Efforts to block abusive requests turned into an ongoing cat-and-mouse game, with some users circumventing restrictions using AWS and Tor. By late 2022, the strain had reached a breaking point, forcing a temporary removal of the endpoint while some of the underlying issues were dealt with.

To mitigate the impact while maintaining functionality, rate limits were introduced, allowing continued access while providing time to explore long-term solutions.


## Character Sheet and Corporation History Endpoints


In addition to the market history endpoints, high request volumes also affected both the [character sheet](https://forums.eveonline.com/t/esi-public-character-data/392063) and character [corporation history](https://forums.eveonline.com/t/resolved-esi-characters-corporation-history/391132) endpoints. 

For the corporation history endpoint, a solution similar to the market history fix was implemented. Since most results were the result of data scraping by third-party applications, a low rate limit was applied to ease server load.

For the character sheet endpoint, a different approach was necessary. This endpoint is used by many applications for user authentication, making rate limiting an impractical solution. Instead, caching adjustments were made to reduce direct backend queries.

Caching functions similarly to rate limiting by reducing unnecessary requests, but rather than blocking excessive queries, it increases the likelihood that previously requested data is served from cache. Since players often log in to multiple applications, increasing cache duration raises the chance that multiple systems will reuse the same stored data, significantly reducing backend strain.


## Toward the Future


The aim is to reintegrate ESI into the EVE Online development and expansion cycle, and so several key improvements are planned to ensure better performance, reliability, and scalability.


## Observability Enhancements


EVE Online’s backend uses [Honeycomb](https://www.heavybit.com/library/podcasts/o11ycast/ep-40-player-experience-with-nick-herring-of-ccp-games/), a monitoring tool that provides real-time visibility into incoming requests, whether from the EVE Client or ESI. This system tracks request duration, system impact (Quasar or Monolith), and metadata, offering valuable insights into performance bottlenecks. 

Previously, tracing only began after a request entered Quasar or Monolith, leaving a blind spot on HTTP requests themselves. A recent update now allows tracing to begin the moment a request enters ESI, providing crucial data on:


- Which applications are making requests at exactly five-minute intervals.
- How effective caching is, including whether cached responses are being utilized efficiently.


Although the information was available before, it was difficult to correlate. These enhancements help make requests more useful, optimize performance, and prevent unnecessary strain on the backend. In other words, setting your User-Agent will now be helpful!


## Static Data Export Improvements


A Static Data Export (SDE) is created roughly once per month, containing essential game data that rarely changes, such as ship types, solar systems, NPC stations, agent locations, etc. While some of this information is available through ESI, many developers prefer to use SDE for efficiency.

Currently, SDE generation is a manual process, for a variety of reasons, leading to delays and inconsistencies between the SDE and live game data on Tranquility. To address this, work is underway to automate updates and ensure that exported data remains current.

Several approaches are being considered, including:


- Generating a new SDE after every Tranquility update.
- Updating the SDE every Tuesday, aligning with weekly maintenance.


Multiple considerations must be taken into account, such as developers using conversions of the SDE, and so on. Additionally, some expected files are missing from the SDE, requiring developers to source them from alternative locations, and addressing these gaps is on the radar as well.


## Transitioning to the Data Hub


Many ESI requests are still sent directly to the Monolith, which can create performance bottlenecks and impact Tranquility. The long-term goal is to transition most read requests to the Data Hub, an internal system designed to store all game activity for analysis and monitoring. Importantly, it contains the information that ESI frequently queries. By shifting ESI’s read requests away from Monolith and Quasar and toward the Data Hub, system stability will improve, as load from third-party applications will no longer affect the game’s core infrastructure. In other words, even if ESI crashed the Data Hub (which is not meant as a challenge!), there would be no impact on the game itself. This separation would allow for increased flexibility and scalability as more third-party applications continue to rely on ESI.

Additionally, more game data is becoming available via the EVE launcher and web-based services such as [Frontlines](https://www.eveonline.com/frontlines), which was recently updated with detailed Pirate Insurgency tracking. Connecting ESI to these additional sources would provide more flexibility in how real-time game data is accessed.

To fully implement this transition, extensive backend changes will be required, and testing will take place with select endpoints before a broader rollout. 


## Rate Limits and Error Handling Improvements


ESI rate limits exist to prevent excessive load on Tranquility, but the current system lacks transparency and provides little feedback to developers. Currently, rate limiting is enforced by the Monolith, meaning that developers only become aware of their request limits once they are exceeded. This lack of visibility makes it difficult for applications to adjust their behavior proactively.

To address this, a token-based rate limiter is being explored. Under this model, each ESI request would consume a different number of tokens based on the type of response received:


- Successful responses with data would consume two tokens.
- Successful responses with no new data (304 Not Modified) would consume one token.
- User errors (400-499 response codes) would consume ten tokens.
- Server errors (500-599 response codes) would consume zero tokens, removing penalties for backend failures.


Each endpoint would have a set number of tokens, which would be replenished at regular intervals. This system would provide real-time feedback, allowing developers to monitor their usage and adjust accordingly.

Another challenge with the current system is that error rate limits can sometimes penalize users for issues beyond their control. At present, every failed request, whether the issue lies on the client side or is a result of a backend problem, counts against a user’s limit. Under the new system, only client-side errors (400-series response codes) would impact token usage, while server-side errors would not.

These ideas are ambitious and a lot of work is required to get there, but it is definitely worth exploring. This approach would create a fairer and more predictable experience for third-party developers while still protecting Tranquility’s stability.


## Infrastructure Overhaul and New Endpoints


The ESI infrastructure is undergoing modernization to align with EVE’s updated coding standards and to make it easier to develop and deploy new endpoints. 

The goal is to make ESI more resilient, improve uptime for third-party applications, and allow for faster iteration on new endpoints.

Several new endpoints are in development as part of the ongoing improvements to ESI, including.


- [Corporation Projects](https://www.eveonline.com/news/view/viridian-expansion-notes#h2-1) – A new endpoint providing an overview of the corporation-managed projects, including contributions, logistics, and financial tracking. This will allow corporations to better manage their internal objectives and reward top contributors.
- [Sovereignty System Support](https://www.eveonline.com/news/view/sovereignty-updates-transition-and-upgrades) – Updates to sovereignty tracking, including sovereignty hubs, customs offices, skyhooks, and mercenary dens. These additions will support recent and upcoming sovereignty changes and provide more detailed insight into territory control.
- [Paragon Hub](https://www.eveonline.com/news/view/equinox-in-focus-personalized-ship-skins) and SKINR Integration – New endpoints for tracking Paragon Hub listings, SKINR material usage and SKIN license applications. These will provide all the tools necessary for budding SKINdustrialists.


Initially, these endpoints will be read-only. Endpoints with writing capabilities will need to wait, as they are more complex in execution.

Beyond these, additional endpoints will be introduced over time, including support for upcoming expansions and game features later this year. Work will also continue to migrate older endpoints to the updated infrastructure to improve performance and maintainability.


## Conclusion & Community Resources


EVE Online has always been at its best when the player community pushes the boundaries of what’s possible, both in-game and beyond. Third-party developers have built an incredible ecosystem of tools that enhance everything from market analysis to fleet operations. Ongoing improvements to ESI will ensure that developers have the tools, documentation, and support needed to keep innovating.

If you’re a developer looking to get started, or a veteran seeking to contribute, here are some essential resources to help you on your journey:


- [EVE Developers Portal](https://developers.eveonline.com/) – Your primary hub for third-party development. Here, you can register applications, access API & SSO documentation, third-party dev blogs and news ([RSS](https://developers.eveonline.com/feed.xml) feed available), and find additional resources to integrate with EVE Online.
- [EVE Online Excel Add-in](https://www.eveonline.com/eve-academy/excel-add-in) – A powerful integration for players who want direct access to EVE’s in-game data within spreadsheets, making it easier to analyze assets, markets, and industry data.
- [Community Tools and Services](https://developers.eveonline.com/docs/community/) – A showcase of player-created projects that enhance the game experience. Developers who wish to contribute their own projects can submit a pull request to have their work featured.
- [awesome-eve](https://github.com/devfleet/awesome-eve) – Another comprehensive community-maintained list of apps and tools built by EVE players.
- [ESI Issues & Feature Requests](https://github.com/esi/esi-issues) – The principal repository for tracking bugs, reporting issues, and requesting new ESI features. Both developers and players can engage here to help shape the future of ESI.
- [Join the Discussion on Discord](https://www.eveonline.com/discord) – Hang out with CCP devs and third-party developers by joining the #3rd-party-dev-and-esi channel on the official EVE Online Discord server to share ideas, ask questions, and collaborate on new projects. You can also subscribe to the #3rd-party-dev-blog announcement channel to have news delivered directly to your own Discord!
