# The Future of Force Projection with FC Okami

- **Date**: 2026-07-17T14:45:00.000Z
- **Category**: dev-blogs
- **Author**: FC Okami
- **Source**: https://www.eveonline.com/news/view/the-future-of-force-projection-with-fc-okami
- **Tags**: #future-updates, #nullsec, #dev-blogs

## Overview
Force Projection has been the topic of some debate within the EVE community, and steps are being taken to address those concerns. In this dev blog, game design director FC Okami goes over the past, present, and future of Force Projection.

---

Hello folks, it’s time for another Okami Game Design DevBlog! This time we’re going to focus on everyone’s favourite topic… Force Projection!

But before we go any further, I want to take a little bit of time to think about and define Force Projection. This is important because there may be some people reading this who aren’t privy to what Projection is and I also want to make sure that we’re all thinking about it in the same way.

Force Projection is the combination of mobility, reach, and response time that determines how much military power a group can apply to a location outside its immediate area of operations.

Over the last few expansions, this has become the number one most talked about issue in EVE Online so far as it makes it up to us via CSM and various player feedback channels.


## Why is Force Projection a problem?


It’s a problem because it means that these powerful groups can respond to activity in a space outside of their operations *too quickly,* effectively intervening in smaller-scale conflicts and making it nearly impossible for newer groups to get any meaningful foothold in areas of space like nullsec.

This leads to a number of hypothesized knock-on issues such as the primary means of survival for smaller groups is for them to join the larger groups which leads to more mega-scale organizations with mono-cultures and goals.

*Ansiblex Coverage as of July 17th, 2026*

We firmly believe that a healthy and thriving EVE is one where new and smaller groups have an opportunity to be competitive and that is not the case today.

We also understand that there are many factors that lead to Force Projection. Everything from how Alphas are used to Wormholes, Filaments, and Ansiblex jump networks.

In a coming update, we want to begin addressing long range Force Projection via Ansiblex jump networks first because we have a few solutions at hand that we are ready to try and we believe that this will have a fairly significant impact on the issue.


## Why are we doing this?


In a recent conversation with CSM20 they asked if I could be clear about what our goals and intentions with Force Projection changes are and I’ll do my best here.

Making space for smaller and newer groups to flourish is absolutely one of our primary goals. That also means that we need to create additional logistics challenges and pressure for larger organizations.

In addition to this, I see long-range Force Projection via Ansiblex gates as a solved systemic puzzle. EVE Online is at its pinnacle when you all haven’t fully figured out the universe's logistical puzzles, and it’s time for this one to get a refresher.

We’ve always believed that it’s *super cool* that large corporations and alliances are able to overcome the challenges that the universe thrown at them, but there should be a certain amount of logistical friction needed to maintain a large empire.

In the way Ansiblexes are currently implemented, we believe they are too strong and not applying enough tension in interesting and meaningful ways - that can be overcome, but provide unique opportunities and logistical puzzles, with opportunity for expansion, play, and counter-play.

We recognize that people use Ansiblexes for other things beside projecting force; such as navigating the day-to-day jobs required to live in Nullsec and maintain an Empire. With that in mind, we also have a goal of ensuring we don’t impact that day-to-day as much as possible, while placing tension on long-range projection.

This also represents a paradigm shift in organizational scale. Force is a product of scale and this will now begin to shift groups towards potentially optimal sizes - both on the small and large scale - and we are intentional in this decision. We’re eager to watch and see how groups acclimate and solve for these changes.

As it stands, Ansiblexes are too powerful and we want to see fundamental and dramatic paradigm shift in how they are used with a strong reduction in their capabilities from where they are in their current implementation.


## Why now?


EVE is in one of the best states it’s been in, in a while. We’re getting regular balance updates with inputs from our players and the CSM. We’re hitting a confident stride in our ability to deliver regular, interesting expansions and new ships. We’re seeing the community thrive.

And while a number of issues persist that we will begin to knock off one-by-one, Force Projection continues to rise to the top and it’s clear that we can’t keep *only* making small tuning adjustments. It’s time for us to commit to a bigger change.

It’s also time for us to be bold and we’re ready to commit to a bold solution. If we wait to try and solve every item on the Force Projection checklist all at once, then nothing will ever happen. We have a cool idea that we back and we’re ready to iterate on - and now’s the time to do it.

We’re eager to commit to something that will have an impact on the topology of New Eden, test organizational logistics, and put some new tension on the overall layout of the universe leading to new opportunities, shake ups, wars, and alliances.


## How do we plan to do it?


But Okami, why not just delete Ansis and start over?

Believe me, it’s super tempting! I’ve honestly thought about going this route a few times, but that seems like the easy way out.

The reality is that Ansis are a really cool idea and they belong in the fantasy of EVE. It’s also something that you’ve all become quite used to and I think completely removing them isn’t the way to go.

So let’s take the harder path.

Let’s take a look at how the idea I’m about to share with you started, where it’s morphed, and what we’re about to do.


## It All Started with Jump Fatigue


We started with an initial proposal by the CSM over the last few cycles that used Jump Fatigue. It wasn’t a bad idea!

Basically, the idea is that Fatigue would be applied as you jumped through Ansis and the amount applied would increase the further you jumped from your sov capital.

What I liked about it was that it leans on an existing mechanism and is fairly straightforward for us to implement and it touches on some of the goals around putting logistic tension on large organizations, centered around capitals.

However, this is not my ideal solution for a few reasons.

First of all, I personally don’t love gameplay systems that prevent individuals from taking actions. (i.e. things like stun-locking) and Jump Fatigue somewhat falls into this category for me.

Another reason it’s not my favourite is that the user experience around this is really difficult. Since fatigue is calculated differently for every individual based on distance they traveled, that could mean that many different members of a fleet could end up with different fatigue timers after every jump depending on where they were coming from. Imagine trying to manage when your fleet could jump and needing to know where every member's fatigue was at each time, or having to decide if leaving your staging might keep you from joining a roam later on. 

There is some historical precedent and learnings around fatigue as well. [Jump Fatigue was first introduced in the Phoebe](https://www.eveonline.com/news/view/long-distance-travel-changes-inbound)release, and we’ve remembered and learned a lot from that time. It did put some tension on Projection but didn't solve for it. We also found it to be overly punishing and generally prevented people from moving around in space because they didn’t want to miss the next fleet.

So what else can we do?


## Ansiblex Capacitor


Every structure in EVE has a capacitor but it’s not something we really expose or use mechanically very strongly at the moment. But we thought… why not lean into another systemic element that exists and is already broadly understood and used in EVE Online?

Our current design is that when a ship jumps through an Ansiblex Gate, it uses some of the Ansiblex’s capacitor. The bigger and more powerful a ship is, the more capacitor it uses. When the capacitor hits 0, no ships can jump through it until it replenishes and has enough capacitor to facilitate the jump of the ship.

The Ansiblex capacitor replenishes over time as it does on a ship.

This is interesting to me is because it removes the burden of managing fatigue off a large group of individuals and instead moves the logistical thinking to a single point - the Ansiblex capacitor itself.

Additionally, this solution opens such a vast design space for systemic improvements, play and counterplay. For example, since it’s a sov structure, we could introduce new types of upgrades that can impact Ansi cap (ie. recharge rates, totals, etc…). We even have the ability to explore more traditional play and counterplay such as cap draining as an alternative strategy to taking down structures.

We’re also introducing a new attribute to balance this cost so we don’t impact the entire ecosystem if we need to make changes to it (such as if we had decided to use mass and needed to re-balance ship mass).


## Zoning


We also want to both affect organizational scale based off the sov capital and also make sure we’re not impacting the immediate day-to-day of the majority of line members.

In this design, we will be adding “zones” that affect the Ansiblex capacitor “fare” cost when you jump through it.

Zone 1 will be centered around the sov capitol and reduce the “fare” cost to 0, meaning ships can fly freely around capital regions. It will be 0-5ly from the sov capital space.

After that, there will be 4 additional zones (zones 1-5), that radiate outwards and increase the fare cost of an Ansiblex jump based on distance.

This specific system element exists to solve for long range projection and give us effective tuning levers that we can adjust in the future or expand on in interesting and meaningful ways.


## Separate Travel Design Spaces


Furthermore, capitals and supercapitals will no longer be able to traverse Ansiblex jump bridges.

We are making this change because they have their own traversal mechanics and powers and this more neatly divides the responsibility and impact of each design space and allows us to tune them separately and build features around them more cleanly in the future.

As this elevates the importance of capital jump systems in strategic play, we’re also going to reduce the number of anchorable cyno jammers in a system from 3 to 1. This will put importance on the placement of jammers and shift advantage away from defenders, elevating the importance of capital ship jump systems being used in warfare.


## The Question of ACLs


We will be changing Ansiblex Access Control Lists (ACLs) to be alliance-only. This will give alliances control over which of their members can traverse through Ansiblex Gates but constrain usage to the organizational unit of an alliance.

ACLs are another design element that has introduced a lot of convenience in EVE but has made some elements of the game too unrestrained and effective.

In trying to mitigate the scope of organizational size, this is an easy restriction on Ansiblex gates that will introduce new logistic tension.

No other structures related to navigation will have ACL or restriction changes at this time.


## Other Changes


With this design we will make a few other design changes to adjust to the new environment this creates.

One is that we will be removing the need for there to be liquid ozone in Ansiblex usage (we’ll watch the market and adjust sinks/faucets as needed and redistribute their value). Since ansiblexes will have a baked in “jump rate limit” mechanic, we no longer see the need for this extra piece of complexity.

We’re also removing tolling from ansiblexes since they will only be applying to an alliance.


## In Summary


Ansiblexes will have their capacitor consumed when ships jump through them and jumps can only be taken if they have cap. Cost will increase by zone, radiating from sov capitals.

They will have their ACLs made alliance-only and capital+ ships will be restricted. We have the agency to allow for exceptions and in our first iteration will also allow Rorquals to pass through.

All of these elements work together to put logistic tension on huge, sprawling empires. While we fully believe that empires can exist in EVE, we feel like the dominance that larger organizations demonstrate should come with increased tension and that those points of tension can and should create opportunities for smaller groups.

We are doing as much of this design as possible for the September 2026 Major Update, but things may change along the way - I’ll stay in touch and keep you informed if they do.


## Economic Adjustments


We are aware that this will have significant impact on the economic zoning of alliance and specifically sov capital spaces. We’ll monitor this impact and be prepared to make adjustments along the way.

In fact, we foresee one of our next steps after releasing this will be to do a readjustment of sov resources in particular, and plan to readjust these as well.

We will give you all at least a 1-month heads up to the new planned numbers before releasing these changes so you can make those changes as necessary.

Additionally, we will explore options like rig amnesty (as we did during Equinox) for those who may want to move their organizations elsewhere.


## Addendums, Disclaimers, Future Considerations


I’m going to be as honest, transparent, and open as I can with this process. Things may change due to development resources and timelines along the way, so I’ll stay in touch and make updates here and on Discord as they progress, so you can stay informed.

We’ve spent a lot of time aligning this with CSM20 and have a majority approval that we’re content with. That said, of course we will listen to feedback and concerns along the way and adjust accordingly.

Once this is live, I will commit (just like we did during the Equinox mining era) to check in bi-weekly and we’ll keep our hand on tuning. Everything here is flexible and we’ll be open to adjusting along the way based on feedback and data.

That said, we really believe in this design and think it will make a more interesting and healthy game ecosystem. I’d like to see this up and running in some tuned version for at least 6 months before we make any broader changes to it. I know it takes at least that long for a change like this to begin hitting the meta and affecting the whole ecosystem and we need to give it time to steep.

I also want to call out that this will not come out with the perfect UI/UX. It will be functional, but we’re being a bit scrappy on the implementation side. This is something we will work on in future iterations.


## Thank You!


And finally thank you for your patience, your feedback, and interest in this project. I’m really excited to see how this impacts the EVE ecosystem and the new puzzles and opportunities it creates. We are committed to impacting Long Range projection and exploring what system and logistical tension on large organizations feels like in meaningful ways.

I believe this will fundamentally change the landscape of EVE and usher us into a new era. I’m tremendously honoured and excited to go along with you on this ride and see the politics, drama and warfare that is to come.

We’re in this together.


- [Forum Link](https://forums.eveonline.com/t/devblog-the-future-of-force-projection-feedback-thread/514961)
- [Discord Post](https://discord.com/channels/940573867192221696/1527683412821934111)


o7 and see you in space,

FC Okami
