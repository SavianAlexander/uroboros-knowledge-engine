---
title: "NPC standings"
url: "https://wiki.eveuniversity.org/NPC_standings"
pageid: 14099
source: "EVE University Wiki"
categories: ["Candidates for verification", "Factions", "Game mechanics"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# NPC standings

- Faction standings**, **corporation standings**, and **agent standings** are a measure of how much an NPC entity likes or dislikes another entity. They are most well known in the context of **missions** and **Crimewatch** but they affect some other gameplay systems too. Standings are measured on a real number scale from -10 to +10. A standing of -10 is tantamount to complete and total loathing and conversely, +10 is complete and total adoration.

1. # Faction standings
Faction standing is the strongest NPC standing. Faction standing gives access to **agents** from all corporations belonging to that faction. This includes normal agents, **COSMOS** agents, and **epic arc** agents (L3 for pirate epic arcs, L4 for empire epic arcs). Unmodified faction standing of 0.0 or higher is also a requirement for joining **faction warfare**.

Most agents will accept either faction, corp, or personal standing to fulfill their requirements. That means, for example, even if you have no corp standing with **Caldari Navy**, if you have faction standing with the **Caldari State** then you will be able to access Caldari Navy agents using that faction standing. The exception to this is R&D agents: if you attempt to use your faction standing to access an R&D agent, you must also have the appropriate corp standing up to the agent's requirement -2. Another example, if a **Kaalakiota** agent requires 5 standing and you have 6 standing with Caldari State and 2.5 standing with Kaalakiota, you will not be able to use that agent. COSMOS agents are another exception in that they only care about your faction standing and don't care about your corp standing

Standings **influence the broker's fees** when trading in NPC stations.

The faction standing also has the most serious effect if it gets too low. At -5.00 faction standing navy vessels will chase you down in high security space that belongs to that faction. As long as you pay attention you can travel through their space as they will not point your ship but just attack and web.

| Standing
! scope="col" | Effect |
| :--- |
| -5 modified |
| -2 modified |
| 0.0 unmodified |
| 1.0 modified |
| 3.0 modified |
| 5.0 modified |
| 7.0 modified |

Faction standing is also required for all COSMOS agents. The standing requirements for these agents are different than for normal agents. These agents don't care about your corp standing.

| Standing
! scope="col" | Effect |
| :--- |
| 2.0 modified |
| 4.0 modified |
| 6.0 modified |
| 7.0 modified |
| 8.5 modified |
| 9.2 modified |
| 9.9 modified |

  1. # Overall recommendations
- Judge early in your career whether or not you want to stay friendly with all empire factions. The mechanism of **derived standings** makes this a non-trivial task. There are some benefits to this (freedom of travel mainly), which must be weighed against the rewards of achieving excellent standing with one faction.
- If you do want to keep faction standings balanced, the best way is to not let them drop in the first place. Do not kill faction ships (decline those missions), and have a way to balance the effects of **storyline mission**s once in a while. With good forethought, you can avoid the horrible grinding mess that it can be to recover extremely low faction standings.
- It is not difficult to keep positive standings (all above zero) with all the Empire factions simultaneously, even if running only normal missions. Just run missions for a faction when it approaches or dips below zero, and decline all missions which require you to kill an Empire faction's ships.
- The **epic arcs** and the final mission of each career agent can be used to gain faction standing without losing other standings as a side effect. The SoE epic arc is accessible to newer players and gives faction standing to the empire faction of your choice.
- It's not a good idea to do missions for the Ammatar Mandate if you're trying to keep your empire faction standings balanced. This is because gaining Amarr Empire standing grants more standing to Ammatar Mandate than doing missions for Ammatar directly, while also providing a sizeable improvement to Khanid Kingdom standing.

1. # Corporation standings
Corporation standing does not affect as many systems as faction standings. Corporation standing is used to get access to higher level mission agents and to lower broker and reprocessing fees in NPC station.

| Standing
! scope="col" | Effect |
| :--- |
| -2 modified |
| 1.0 modified |
| 3.0 modified |
| 5.0 modified |
| 7.0 modified |
| 6.67 modified |

1. # Agent standings
  - Agent** standings are the weakest NPC standings but also the fastest one to gain. This standing allows you to take missions from that one agent with whom you have standing even if your faction or corporation standings are not high enough as long as both of them are better than -2.00.

| Standing
! scope="col" | Effect |
| :--- |
| -2 modified |
| 1.0 modified |
| 3.0 modified |
| 5.0 modified |
| 7.0 modified |

1. # Gaining and losing standings
When standings go up or down they do so as a percentage; this is always a percentage decay towards the extreme end of the scale. For example, if someone has 1.0 standing with an NPC corporation and completes a mission that changes standing by +5%, then the current standing is increased by 5% of the difference from 1 to 10; that's a change of +0.45 with an end result of 1.45. However, if someone else with a 4.0 standing completes the same mission under the same circumstances and also gets a 5% increase, then that's 5% of the difference from 4 to 10; that's a change of +0.30 with an end result of 4.30.

If something causes a standing decrease, then it's a percentage decay towards −10. For example, if someone with 1.0 standing suffers a −5% change, then that's 5% of the difference from 1 to −10; that's a change of −0.55 with an end result of 0.45. If someone with 4.0 standing suffers that same −5% change, then it's 5% of the difference from 4 to −10; that's a change of −0.7 with an end result of 3.3. 

The formula for standing increase is
> <math>\displaystyle \text{New standing} = \text{Old standing} + ( 10 - \text{Old standing} ) \times \text{Standing increase} </math>
The formula for standing decrease is almost the same, just towards -10
> <math>\displaystyle \text{ New standing} = \text{Old standing} + ( -10 - \text{Old standing} ) \times \text{Standing decrease} </math>

where *Standing decrease* is the decimal form of standing change. For example, 0.4% would be 0.004.

The consequence of this math is that the higher your standings are, the less effective standings increase become and the more dramatic penalties become. For example, a standing loss of 1% turns 9.0 standing into 8.81 but an increase of 1% would bring 9.0 standing to 9.01.

The equation for resulting standing for receiving the same standing gain multiple times is

> <math>\displaystyle S_n = S_0 + ( 10 - S_0 ) \times ( 1- ( 1 - \text{Standing increase} )^n )</math>

And in a similar style, the equation for resulting standing for receiving the same standing loss multiple times is

> <math>\displaystyle S_n = S_0 - ( 10 + S_0 ) \times ( 1- ( 1 - \text{Standing decrease} )^n )</math>

Corporation and agent standings increase after each completed mission. Faction standings however are gained from certain missions only:
- Doing **Career Agents**: Small increase in faction standing. This falls under the category of storyline missions and may only be done once. This includes the 15 career agents per faction.
- Completing a storyline mission: Small to moderate faction standing increases depending on the level of the mission. Large corporation standing increases.
- Doing **Datacenter missions**: Faction standing increases, with higher level missions granting more standing. These missions require turning in pirate tags, and may only be done once. To access higher levels requires higher standing, L1 can be done at any time.
- Doing **COSMOS missions**: Similar standings gain as a hard storyline mission of the same level. These missions are more complex than normal and may require special attention and research. They may only be done once. To access higher levels requires higher standing, L1 can be done at any time.
- Doing **courier circle missions**: One time faction standing increases only, the first time you do the loop.
- Doing the **epic arcs**: Significant faction and corporation standings increase without a derived decrease in opposing factions' standings. This is the only way to gain faction standings without losing standings with other entities.

Standings can be lost in a few ways. It is recommended that you consider your future before doing these activities.
- Failing a mission results in agent, corporation, and faction standings loss.
- Declining more than one mission every four hours results in agent, corporation, and faction standings loss.
- Fighting **NPC Mining Operations** results in corporation standing loss.
- Destroying ships belonging to faction results in faction standing loss. Not all ships count for this.
- Destroying pods of players in an NPC corporation results in a standing loss with that corporation.

Taking part in faction warfare incurs **various standings gains and losses**:
- Killing enemy militia ship (in NPC corp): Militia corporation standing loss.
- Killing friendly militia: Faction and corporation standings loss without derived standings.
- Killing faction NPC (missions): Faction standing loss and derived standings.
- Capturing complex: Militia corporation standing gain.
- Promotion: Faction standing gain and derived standings.
- Faction warfare missions: Normal mission standings gains and losses.

  1. # Derived standings
Every time you gain faction standing from a mission other than epic arc missions and the final mission for each career agent you will also get derived standings. You will gain standings with factions that like the faction and lose standings with factions that dislike them. The gains and losses depend on the [inter faction relationships](https://web.archive.org/web/20180313111844/http://www.newedenlibrary.net/eon/faction_standings.shtml) and are usually smaller than the original standing increase. This makes it very hard to gain high faction standing with more than two empire factions or both pirate and empire factions.

The derived standing modifier is based on the standing of the secondary faction towards the faction you work with and the ratio of the sizes of these two factions.
> <math> \displaystyle \text{Inter-Faction Standing Modifier} = \text{ Secondary Faction’s standing view of Primary Faction } \times \frac{ \text{Primary Faction Size } }{ \text{Secondary Faction Size } }</math>

If you gain *Gain%* amount of standing with a faction then the derived standing to another faction is
> <math>\displaystyle \text{ Derived Standing }% = \text{Gain }%  \times \frac{ \text{Inter-Faction Standing Modifier } }{ 10 }</math>

For example, you complete a storyline mission to the Minmatar Republic and gain 2% faction standing towards the Minmatar Republic. This will give you -1% derived standing towards Amarr Empire, +1% derived standing towards Thukker Tribe and many others.

When you lose faction standings you will also get negative derived standings with friends of that faction. But you will <em>NOT</em> get positive derived standings with their enemies.

Derived standings are also capped at the standing that factions have towards each other. For example, Amarr Empire standing towards the Minmatar Republic is -5.00 so once you have -5.00 standing with Amarr Empire you will not get any further negative derived standings towards Amarr for doing Minmatar missions.

  1. # Recovering low faction standings
You may find yourself in a situation where you have ruined your standing with a faction. This may be the result of taking missions against that faction or taking part in faction warfare. The first problems arise at &minus;2.00 standing as you can not take higher than L1 missions from the faction. The more serious issue comes when you hit &minus;5.00 faction standing as the navy of that faction will start chasing you in high security space of that faction.

Quite simply, if you are below &minus;2.00, you have very limited options. First, train your Diplomacy skill to as high as you can. This will modify your negative standings upward by a certain percentage. You can do all the tutorials, data center, and COSMOS missions for one time boost to standings, for both that faction and ones that are friendly with it for the derived standings. Remember even if Caldari State is &minus;3.00, if Amarr Empire is &minus;1.00 you will still have access to all the Amarr agents and can even run L4 missions for them which will eventually get you derived standing from storyline missions. If you have no more tutorials, COSMOS, or datacenter missions available, your only recourse are L1 agents (very small faction standing increases with storyline missions), playing the derived standings game, doing the epic arc, or joining Faction Warfare as detailed below. It's a long road to travel. 
- Once you get to &minus;2, you can again access agents with whom you have a high corp standing. Both corp and agent personal standing can be shared in missioning fleets, so this can be the fastest way to start doing high level missions for that faction. You will never gain or lose faction standing from other people's storyline missions when in fleets.
- If you are in a corp, the corp's relationship to each faction is determined by simply averaging all the member's standings together (ignoring members who do not have standing to that faction). This means that even with low faction standing, you may be able to join a corp that qualifies for Factional Warfare and work your way up through the ranks to recover your faction standing.
- Remember that all this work will be hurting the standings of opposing factions, to the point where they tend to balance out between &minus;1 and 1. It is extremely difficult to get high faction standing (e.g. 5 or 6) with two opposing factions. It is almost impossible to achieve standings that high with all the Empire factions simultaneously.

  1. # Unrepairable standings
It is impossible to improve standings with the Drifters and Rogue Drones factions because they do not have any agents in the game or positive relationships with any other faction. You can however still lower your standing with this faction through ship kills.

CONCORD Assembly, Society of Conscious Thought, and Jove Empire are also factions with no agents but they have positive standings to a few other factions, making it possible to increase standings through derived standings.

CONCORD owns the constellation of Sanctum in the region of Genesis. If you go below -5.00 standing with CONCORD Assembly you will be attacked by CONCORD navy in that area (the same mechanics as the normal Empire navy ships, not instakilling CONCORD police). CONCORD Assembly will lower their standing towards you through derived standings if you gain positive standing with any pirate faction. Their standings can only be repaired via derived standings from the four main Empire factions.

  1. # Standing ticks
Standings from rat kills are gained in ticks. The standing tick is 10 minutes long and is tracked on per system basis.

This means that if you, for example, kill three Minmatar sentry towers in less than 10 minutes in same system you would get standing loss from only one of them. But if you instead of kill three Minmatar sentry towers in three different systems you will get standing loss from all of them even if you do it in less than 10 minutes.

1. # Skills
NPC standings are modified by various **social skills**. This results in effective standings that are higher than the unmodified standings. Almost all standings related requirements are based on effective standings. The only confirmed uses of unmodified standings are broker fees and faction warfare.

Skills that modify standings:
- : 4% standings increase, per level, for non-criminal NPC entities that you have positive or 0 standings with. (Note that the in-game description for this skill neglects to mention that it doesn't apply to criminal entities.)
- : 4% standings increase, per level, for criminal NPC entities that you have positive or 0 standings with.
- : 4% standings increase, per level, with NPC entities you have negative standings with.

This increase is calculated over the difference between maximal possible standing (10) and the actual unadjusted standing.

The math
> <math> \displaystyle \text{ Efective Standing } = \text{ Unmodified Standing } + ( ( 10 - \text{ Unmodified Standing } ) \times ( \text{ modifier } \times \text{ Skill level } ) ) </math>

A notable feature of the skills is that with level 3 in (Criminal) Connections brings the effective standing from 0.00 to 1.2 allowing the pilot to skip level 1 missions completely.

There is also one skill that increases the standings gains.
- : 5% bonus per level to NPC agent, corporation and faction standing increase.

1. # No standing versus 0.0 standing
In the beginning, a new player starts without any standings towards any faction, corporation or agent. This is distinctly different from 0.0 standing even if some of the user interface elements show them as same.

There are two key differences between the two:
- Skills do not apply to no standing. This can lead to an odd situation where at no standing you see yourself having 0.0 effective standing but after one failed mission your effective standings increase as your social skills start to apply.
- Corporation wide standing towards NPC entities ignore no standing members.

Once a player has gained or lost standing towards the NPC entity they can never return to the no standing state.

1. # See also
- Support page: [Standings](https://support.eveonline.com/hc/en-us/articles/203217152-Standings)
- [Inter-Faction Standing Relationships](https://web.archive.org/web/20180313111844/http://www.newedenlibrary.net/eon/faction_standings.shtml)
- **Missions**
- **Mission fleets**
