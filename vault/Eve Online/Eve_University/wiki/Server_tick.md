---
title: "Server tick"
url: "https://wiki.eveuniversity.org/Server_tick"
pageid: 11165
source: "EVE University Wiki"
categories: ["Game mechanics"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Server tick

"**Server tick**" is a term used to describe the rate at which the EVE Online client and server communicate. The goal of the server is for a tick to run exactly once per second, or at 1 hertz. This relatively slow tick rate creates sub-second gaps between the player's orders to the client and order activations on the server. 

Almost every action is restricted by server ticks. The timings of many mechanics in EVE are rounded up to the full second. For example, a 1.2-second locking time will be rounded up to a 2 server ticks, thus 2 seconds. 

1. # Mechanics
The server tick has some unique limitations: it can’t do anything that would require directly talking to most of the database servers, since those can have long lags. A typical server node handles hundreds of systems, so even though there's a tick every second for each grid, it might only have one hundredth of a second or less to do all the work for the tick for a single grid. That's not enough time to talk to a database!

Most heavy lifting in the code is therefore done by queuing some work to be done on other threads; when that work is finished, the results are reported at the next tick.

However, the client will usually process commands immediately, showing the player the action is currently taking place. Actions won't be actually effective at the server itself until the next tick.

Some tasks are completely disassociated from the server tick and can happen at any time, being subject only to the latency between the client and the server. 

1. # Examples
- If you’re trying to jump through gate, EVE will mark you as "jumping through the gate" the instant that it receives the message, and will send back an acknowledgement right away that you’re jumping. However, everyone else on the grid won’t know that you’ve started jumping until the next server tick.
- If you activate a turret module, it’ll immediately calculate the damage, and immediately apply it to the target. It’ll send back a packet right away, telling you, "I activated this module for you."  However, you won’t receive information about how much damage was dealt until the next tick—and neither will the target. This means you can be dead for up to a second (or up to 10 seconds, in the case of severe **time dilation**) and not know it yet! This is also how EVE handles weapons that can fire more than once per tick: it simulates them properly, and then both shots appear on the next tick.
- If you activate a warp scrambler, it’ll immediately tackle the target. But the "X has warp scrambled Y" global notification won’t appear until the next tick.
- [This example](https://web.archive.org/web/20210111174108/http://eve.501gu.de/misc/travelceptor_vs_instalocker.png) shows the two outcomes of a confrontation between an interceptor fitted for fast alignment and entry to warp ("Travelceptor") and a ship fitted to lock up and tackle targets rapidly ("Instalocker"), one of the most frequently encountered examples of server ticks interacting perceptibly with gameplay.

1. # See also
- **Gatecamps** for the mechanics around gatecamping, a highly tick-influenced activity.
- **Time dilation** for the mechanics that revolve around Time Dilation in highly populated systems.
