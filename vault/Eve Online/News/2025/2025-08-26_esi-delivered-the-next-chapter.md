# ESI Delivered: The Next Chapter

- **Date**: 2025-08-26T11:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/esi-delivered-the-next-chapter
- **Tags**: #development-updates, #eve-evolved, #new-features, #news

## Overview
Corporation Projects, more stability and richer data In this month’s update

---

Earlier this year, we shared **a deep dive** into the technology that powers third-party development in EVE Online: the ESI. As the backbone of EVE’s developer ecosystem, ESI connects creators to the universe of New Eden, enabling everything from fleet management tools to industrial planning apps and killboard integrations. These tools have become essential for capsuleers, and the API that supports them deserves the same level of care and attention as the game itself.

Hear it directly from our devs! Check out the accompanying podcast for this dev blog, here:

That article revisited the origins of the API, explained how ESI functions today, and outlined a roadmap for modernizing the platform. The goals were clear: enhance reliability, retire outdated components, and build the foundation for new features.

Since then, significant progress has been made. Monitoring has been expanded to give a clearer picture of how ESI is used, which applications are making requests, how frequently, and how effectively caching is applied. Deprecated endpoints have been removed, early steps toward rate limiting have been put in place, and error handling has been refined. These efforts have made ESI more stable and ready to support new capabilities.

That groundwork has led to the first major feature release under this renewed approach: the launch of Corporation Projects routes. This marks the debut of Data Hub-powered endpoints in ESI, delivering richer data, more efficient pagination, and fewer round-trips for developers. It’s an example of where the platform is headed, and a sign of what’s possible when stability and modernization pave the way for new functionality.

This update takes a closer look at what’s changed since then: the cleanup efforts, the systems put in place, and a preview of what’s coming next.


## Getting Clear Vision


In our last update, we talked about plans to improve observability within ESI. Over the past few months, that effort has matured into something much more powerful. With the help of [Honeycomb](https://www.honeycomb.io/), we now have full visibility into incoming requests to ESI and where they’re routed. Whether that’s through Quasar or the Monolith, we can trace the entire path from start to finish.

One of the biggest wins from this has been understanding the real sources of 5xx errors. Until recently, a lot of that was guesswork. Now, we know exactly what's happening.

A few examples worth calling out:


- When the Monolith returned a 404, but the API spec for that route didn’t include 404 as a possible response, ESI translated that into a 500. This led to errors where a 404 would have been the correct and expected result. That behavior has been corrected.
- Our HTTP connection timeout was set to just one second of idle time. Unfortunately, the load balancer expected idle connections to remain open for at least 60 seconds. This mismatch caused a number of 504 errors when connections were closed prematurely. That’s now fixed.


These are just two of several issues uncovered and resolved in recent months. The result is a measurable drop in 5xx errors. A before-and-after comparison can be found below.

There are still a few cases left to investigate, and we’ll keep working through them. That said, the current 5xx rate is already very low (roughly one in every 10,000 requests) so most users shouldn’t notice any issues anymore.


## **Cleaning the Ship**


For a long time, ESI supported two different authentication methods: one of which, known internally as “v1”, dates all the way back to the earliest versions of the API. The newer “v2” flow uses [JWTs](https://www.jwt.io/), which allow tokens to be verified locally, without reaching out to the SSO on each request. That might seem like a small detail, but when you're handling thousands of requests per second, the difference is massive. JWTs are faster, simpler, and far less demanding on infrastructure.

Although “v1” was [officially deprecated back in 2021](https://developers.eveonline.com/blog/sso-endpoint-deprecations-2), support remained in place to avoid disrupting third-party tools that still relied on it. Until recently, though, there wasn’t enough visibility to assess how widely it was still in use.

That changed with the improvements to observability. With full request traces now available, it became possible to identify which applications were still using “v1” tokens by examining User-Agent headers and application IDs. Where possible, affected developers were contacted directly and encouraged to migrate. Once that was done, we published a [final deprecation warning](https://developers.eveonline.com/blog/removal-of-v1-authentication-tokens) and followed through with full removal a few weeks later.

A similar approach was taken with the removal of several outdated route versions. First, we reached out to developers directly, then followed up with public notices before any deprecations were enforced. As tooling continues to improve, this kind of process (observe, inform, take action) is becoming the standard. It’s a cleaner, more predictable way to retire legacy components without surprises.


## **Routing the Flow**


In recent months, large parts of ESI’s infrastructure have been rebuilt. The goal has been twofold: to modernize systems using current internal standards like Terraform and Go, and to gradually retire legacy components that were no longer serving a clear purpose.

At the center of this overhaul is a new service known as the API Gateway. Its responsibility is to handle incoming requests: checking authentication, enforcing rate limits, validating paths and tenants, and then passing them on to the appropriate backend. By the time a request reaches its destination, it’s already been vetted. This removes the need for backend services to repeat the same checks and makes the overall system simpler and more reliable.

This new architecture also brings improved visibility. With the gateway acting as the single point of entry, traffic can now be observed in greater detail, both in terms of tracing and metrics. That added insight has made it easier to detect issues early and respond more precisely during incidents.

A more detailed breakdown of the gateway’s design and deployment was shared in an earlier [blog post](https://developers.eveonline.com/blog/the-ship-of-thesius). At the time of writing, the final implementation steps are nearly complete. The main piece still in progress is rate limiting, which will be covered next.


## **Setting Boundaries**


As part of our [continued effort](https://www.eveonline.com/news/view/eve-evolved-the-future-of-eves-api#h2-13) to manage ESI traffic, we have deployed the first steps toward rate limiting in the API Gateway. This currently is in a “monitor-only” mode. This way we are gathering information about what good rate limits will be before we actually enforce them.

Rate limiting has been a recurring topic internally and within the third-party developer community. Until now, ESI lacked good options for handling problematic traffic. While some patterns were clearly abusive, the main response was IP bans - manual, reactive, and not ideal for anyone involved. A more proactive approach is long overdue.

One extreme case is shown below: a single user sending a flood of requests well beyond anything reasonable. That account was banned. Let it be clear: this kind of traffic is not acceptable.

The more common issue is regular traffic spikes, especially on the hour and half-hour. Routes like /assets/ are frequently hit the hardest, with traffic spiking up to five times above normal. Scaling to meet these peaks puts unnecessary strain on the API Gateway, Monolith, and Quasar. There’s a limit to how far infrastructure can be stretched just to handle burst traffic. Smoothing those spikes is essential. 

This mostly applies to larger frameworks and widely used apps. If you’re just getting started or have a small userbase, there’s little cause for concern. But for tools with broad deployment, it’s worth reviewing how requests are scheduled.

Enforcement won’t begin without notice. A detailed blog post will be shared ahead of time to give developers a chance to prepare.


## **Keeping Up with Standards**


A major upgrade rolled out recently is the migration from Swagger 2.0 to OpenAPI 3.1. OpenAPI is the natural evolution of Swagger, addressing limitations that made it difficult to accurately represent some of ESI’s internal structures. Tooling support has also shifted as many modern tools support only OpenAPI, while Swagger support has steadily declined. With that in mind, we made the decision to [migrate all of ESI to OpenAPI](https://developers.eveonline.com/blog/changing-specs-from-swagger-to-openapi). 

Alongside the spec upgrade, we also [changed how the API is versioned](https://developers.eveonline.com/blog/changing-versions-v42-was-getting-out-of-hand). Versions are now date-based and apply API-wide. This provides clearer insight into how recent a version is, and makes it easier for both internal teams and third-party developers to track which version is in use. The transition was made smoother thanks to the new API Gateway, which allowed the new versioning system to be introduced without breaking existing integrations. Developers can adopt the new model at their own pace (within reason) over the course of about a year from July 2025.


## **Corporation Projects – Now Available**


Corporation Projects allow corp leaders to set up collaborative goals for members, like hauling materials, killing hostiles, or contributing ISK, while tracking participation and rewarding members who help. It’s a flexible system for directing group activity without micromanagement. More details on the feature itself can be found in the [**EVE Academy overview**](https://www.eveonline.com/eve-academy/corporation-projects). 

Today, the Corporation Projects routes become publicly available (insert rocket emoji, but web page won't let us)

Developers can now query ESI for the following:


- A list of [**all active corporation projects**](https://developers.eveonline.com/api-explorer#/operations/GetCorporationsProjectsListing)
- Details of a corporation project including its [**current state and reward pool**](https://developers.eveonline.com/api-explorer#/operations/GetCorporationsProjectsDetail)
- A list of [**contributors to the project**](https://developers.eveonline.com/api-explorer#/operations/GetCorporationsProjectsContributors) and [**their contributions**](https://developers.eveonline.com/api-explorer#/operations/GetCorporationsProjectsContribution)



## **For Developers**


As mentioned in the previous EVE Evolved update, the long-term goal is to shift most read-heavy traffic to the Data Hub. These routes are the first to follow that model. They’ve been built in close collaboration with the Data Engineering team and mark a step toward decoupling ESI from the Monolith.

The benefits are already visible:


- Richer listing responses: The new project listing route includes detailed, high-level information such as progress, ISK rewarded, and other live metrics—without requiring a follow-up call for each project.
- [Cursor-based pagination](https://developers.eveonline.com/blog/changing-pagination-turning-a-new-page): Instead of cycling through pages or refreshing every detail view, developers can poll the listing endpoint to see what’s changed. It’s more efficient for applications and easier on the API itself.
- Expanded entity resolution: Where possible, IDs are resolved to names. For example, project creators are shown with both their character ID and name, reducing the need for additional lookups. While this isn’t available for every field, it’s included where practical.


The result is a cleaner, faster integration point that gives developers more upfront and reduces unnecessary round-trips. If the rollout proves successful, this design will serve as the foundation for other new routes in the future.


## **What’s Next?**


The next major addition to ESI is support for Freelance Jobs. Much like Corporation Projects, this system will allow developers to access structured data around jobs available across New Eden—what’s being offered, where, by whom, and what the rewards are.

Development is already in progress. Feedback gathered from the Corporation Projects rollout is being fed directly into the design of these new routes, helping us refine the interface and structure before it reaches public release. Freelance Jobs will also adopt the new patterns introduced with Corporation Projects, including richer list data, name resolution, and cursor-based pagination. This should make it easier to build applications that surface a wide variety of in-game activities capsuleers can engage with at any given time.

More details will be shared in the coming weeks as we fine-tune the specifications.


## **ESI is You**


Behind every third-party tool, fitting app, or custom dashboard is the creativity and effort of EVE’s developer community. Whether you're building tools for your corporation, contributing to widely-used frameworks, or just tinkering to enhance your own gameplay, these contributions shape the experience of countless capsuleers.

If you’re looking to supercharge your own EVE experience, the [Community Tools and Services](https://developers.eveonline.com/docs/community/) page is a great place to begin. And if you want a closer look at the ecosystem itself, check out this [presentation by RIFT developer and EVE Partner Nohus](https://www.youtube.com/watch?v=1fxqAdjTJbQ) for insights into the tools, workflows, and ideas shaping the future of third-party development. Also, did you know we have an [official Excel add-in](https://www.eveonline.com/eve-academy/excel-add-in) for direct access to EVE’s in-game data within spreadsheets?

If you are a developer just getting started or with years of experience under your belt, here are some key resources to explore:


- [EVE Developers Portal](https://developers.eveonline.com/) – Your primary hub for third-party development. Here, you can register applications, access API & SSO documentation, third-party dev blogs and news [RSS](https://developers.eveonline.com/feed.xml) feed available), and find additional resources to integrate with EVE Online.
- [ESI Issues & Feature Requests](https://github.com/esi/esi-issues) – The principal repository for tracking bugs, reporting issues, and requesting new ESI features. Both developers and capsuleers can engage here to help shape the future of ESI.
- [Join the Discussion on Discord](https://www.eveonline.com/discord) – Hang out with CCP devs and third-party developers by joining the #3rd-party-dev-and-esi channel on the official EVE Online Discord server to share ideas, ask questions, and collaborate on new projects. You can also subscribe to the #3rd-party-dev-blog announcement channel to have news delivered directly to your own Discord!
