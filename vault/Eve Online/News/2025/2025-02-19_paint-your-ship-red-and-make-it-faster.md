# Server Deep Dive – The Power of Pretty

- **Date**: 2025-02-19T15:30:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/paint-your-ship-red-and-make-it-faster
- **Tags**: #development-updates, #eve-evolved, #news

## Overview
Unlocking new possibilities for fleet fights and beyond.

---

Capsuleers,

It’s time to continue the conversation around Quasar, the underlying ecosystem for modern development in EVE Online. Since its introduction at Fanfest 2022, it has become the foundation for several major advancements, including:


| Corporation Projects (2023) | Sovereignty Hub Network (2024) | SKINR (2024) |
| --- | --- | --- |


This journey, a part of EVE Evolved, has touched on set theory, graph theory, and, uh… color theory. Today, however, the focus is on the technology powering capsuleer-created ship SKINs, because it is much more than just a fancy editor and shader wizardry! In fact, it is a key part of unlocking future capabilities for server performance. Brace yourself, though, as a few technical crash courses will be needed to appreciate the ins and outs of what the team has been up to.


## Netcode and Tick Rate


One of the most common challenges in multiplayer games is its network architecture, colloquially referred to as “[netcode](https://en.wikipedia.org/wiki/Netcode)”. Whether striving to ensure a consistent experience for all players or to prevent cheating, the way information is transmitted to game clients plays a crucial role in the overall performance and enjoyment. A key factor here is **tick rate** - the frequency at which the game server updates and sends information to connected clients.

Different game engines approach this in different ways. [**Unreal Engine**](https://dev.epicgames.com/documentation/en-us/unreal-engine/actor-relevancy-in-unreal-engine), for example, emphasizes *relevancy filtering,* sending only the most important updates to each client, while [**Source Engine**](https://developer.valvesoftware.com/wiki/Source_Multiplayer_Networking) focuses on *input prediction*, reducing the number of corrections needed to maintain smooth gameplay. 

Regardless of approach, tick rate remains a fundamental factor in network performance. Most games operate between 20Hz and 120Hz, depending on the number of players online, meaning that updates are sent between 20 and 120 times per second per client. For instance, at 60Hz, the server must process and send updates every 16.6 milliseconds to ensure that 60 updates can happen within one second, and leave room for other players to receive the same information in the same time frame. Assuming a magical latency-free internet connection bringing clients the game state directly on connect (let’s just pretend that exists), a 60Hz server would process game state updates like this:


### Two ticks of a 60hz Server


Input prediction and movement interpolation can create the illusion of near real-time interaction, even without a magical zero-latency internet. But as tick rates drop, delays become more noticeable. Which sounds bad, right? So why would you ever want a lower tick rate?

Well, EVE Online has been around since the days of 56k modems. To keep bandwidth requirements low enough for massive space battles, the server tick rate was set to one second.

More specifically, the tick rate of the physics simulation is 1hz which dramatically reduces the need to send updates to the desktop clients.

Other interactions with elements that don’t affect physics are processed as quickly as the Python hamsters will go. This means that if an input is sent right before a tick, it feels highly responsive. If sent right after, it can feel like it takes a second or even more to see an effect (when factoring in real-world latency – GG, Australia). Technically, therefore, you could get into a good vibe with the server by pressing a key exactly once per second, but of course, for mental wellbeing, it can be *very* important to click “Jump” thirty times per second.

Looking holistically at Tranquility on average over the past year, it’s clear that the number of operations per second is proportional to the number of active capsuleers in the cluster. On average, each session processes around 0.7 operations per second, demonstrating how efficient EVE Online is at transmitting only the data that is necessary.

The numbers fluctuate, of course, and these are all averages. When fleet fights hit processing limits, Time Dilation (TiDi) kicks in. If you’re curious about the nuts and bolts of that, you can look at the [**archive on TiDi**](https://www.eveonline.com/news/view/time-dilation-hows-that-going) to learn more.


## So Where do SKINs Come In?


Almost all cosmetic mechanisms in EVE Online are sent via simulation frames, EVE’s version of a tick. Before SKINR, ship SKIN changes were delivered with the next simulation frame that was sent to all relevant clients. In other words, SKIN updates could only happen once per second. Even without any rate limits on the UI or network requests, no matter how fast you would change SKINs, no one would be able to see more than one update per second, because that’s the limit on simulation frame transmission.

There’s also another issue: **fanout**. (Last crash course, promise.)

When you change your ship’s SKIN, the update needs to be sent to multiple recipients – what is referred to as “fanout”. But which ones need to receive the information? What happens if you are near a hundred other ships? What does “near” actually mean, and who are the other hundred?

Simulation frames handle both problems by only processing updates for ships within the same **bubble** (colloquially **grid** - not to be confused with warp disruption bubbles). This approach comes at a cost, though, as more data per simulation frame means more serialization and fanout for the server simulating that solar system. Previously, Quasar only tracked which solar system a ship was in, but for SKINR to function in real time, it had to track ship movement between bubbles as well.

This was no small feat. It required deep changes to EVE Online’s core simulation engine to allow Quasar to access its state in a way that hadn’t been done before. The result was shocking! A whopping 27x increase in processed data compared to the simple transitions between solar systems. 

Here’s a comparison of events per second between solar system travel and bubble travel – keep in mind that warping traverses multiple bubbles, not just “A to B”. 

And that’s just internal traffic, before even considering the fanout problem!


## Solving the Fanout Challenge


Now, let’s go back to the “one ship changes its SKIN near 100 other ships” scenario. With Quasar tracking all ships across all bubbles, it now understands what “near” means and which clients need to receive updates. Instead of waiting for the next simulation frame, Quasar immediately dispatches SKIN changes to everyone in a given bubble.

This is made possible by messaging from the mighty [NATS](https://nats.io/), which efficiently handles the roughly 10,000 messages being sent out to EVE clients every second. Services like the ones that handle cosmetic state can now serialize and send a single SKIN update, which is then fanned out to all nearby ships, rather than being delayed by the 1Hz simulation tick.

This is demonstrated in this quick clip from a SKINR playtest:

The question becomes: Why is it important that Quasar can track ship locations and send out cosmetic updates independently? Because this technique allows EVE Online to offload a purely cosmetic function from the main simulation engine.

Furthermore, it has broader implications when considering all the other cosmetic effects that need to be serialized and fanned out to clients. Once the conversation moves beyond cosmetics, the natural question becomes: what else could be unloaded to Quasar?


## Pushing the Limits


To put the system to the test, part of the SKINR mass test involved removing the UI limiter on SKIN switching to see what would happen. The result? A rather interesting visible effect:

The fun part was when the real stress test began, with 500 players simultaneously spamming SKIN changes in the same bubble on a potato test server. This resulted in the system hitting a peak of about 45,000 messages per second!

A big thank you goes out to everyone who participates in these kinds of mass tests. It might not always be obvious just how valuable your contribution is, but this clearly illustrates the impact your participation has. 

Going back to the chaotic example above, what exactly did it accomplish?

Looking at the statistics from earlier, Tranquility typically handles roughly 30,000 messages per second across the entire server, giving it a nice average of about one operation per second, or 1Hz. In contrast, the SKINR test reached 45,000 messages per second with just 500 players, meaning Quasar was effectively delivering updates at 90Hz in that scenario. 

If Quasar can provide 90Hz traffic for 500 players on a small-scale test server running just three nodes, what could it do if scaled up to the full power of 230 Tranquility nodes with 30,000 active players?

What happens if simulation frames themselves follow the same paradigm?

What happens if simulation frames no longer have to wait a full second to be sent?

What implications does this have for Time Dilation? Does the meta shift when battles are fought real time at scale?

If the fidelity of the network can be increased 90-fold, what new experiences can the designers bring to the pilots of New Eden?

These are the questions that will shape the evolution of EVE Online, and some may be answered on [**CCP TV**](https://twitch.com/ccp) at 15:00 on 20 February, so make sure you tune in.

o7
