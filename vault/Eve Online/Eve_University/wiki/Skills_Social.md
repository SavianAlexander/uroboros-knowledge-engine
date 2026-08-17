---
title: "Skills:Social"
url: "https://wiki.eveuniversity.org/Skills:Social"
pageid: 1704
source: "EVE University Wiki"
categories: ["Skills"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Skills:Social

# Overview
Most **Social skills** provide modifications to your **standings** or rewards from NPC corporations. They are of most value to **mission runners** but are also of use to those seeking access to specific services from NPC controlled corporations and factions. (**lower costs for reprocessing/refining**, **Trading**...) The Freelancing skill is an exceptions as it increases the number of concurrent Freelance Jobs a character can accept.

As you do missions for NPC corporations, your standings with them will go up. As you do **storyline mission**s, your faction standings will change for the faction a particular NPC corporation is part of.

Gaining faction standings via storyline missions or **data center missions** carries "Derived Modifications", meaning that standings will also go up with friends of that faction and down with enemies of that faction. For example, raising your faction standings with the Gallente Federation will also raise it slightly with the Minmatar Republic while lowering it slightly with the Caldari State and Amarr Empire. The reverse also being true - raise Amarr, lose some Gallente faction standings. (**Epic arcs** do not carry derived modifications; they only affect the standings of one faction, depending on mission choices made during the epic arc.)

These changes are where some of the social skill effects come into play. Others are specific to **mission runners**.

Increasing the Charisma and Intelligence attribute scores increases the rate at which Social category skills are trained.

The social skills affect 3 different areas of your interactions with NPC entities (meaning Factions, Corporations, and Agents):

  - Standings Modifiers** (all modifiers are per level trained)
- - 5% improved standings gains for all missions.
- - 4% effective standings increase with NPC entities you have negative standings with.
- - 4% effective standings increase for non-criminal NPC entities that you have positive standings with. (Note that the in-game description for this skill neglects to mention that it doesn't apply to criminal entities.)
- - 4% effective standings increase for criminal NPC entities that you have positive standings with.
- - 5% bonus to effective **security rating** increases. (CONCORD sec status)

In the above, "criminal" refers to the NPC pirate factions, or the member corporations and agents thereof. The NPC pirate factions have negative standings from (and towards) CONCORD. Diplomacy, Connections, and Criminal Connections do NOT have overlapping validity conditions; only one of the three will apply.

  - ISK Reward Improvements**
- - 5% improved ISK payout from agents (per level trained).

  - Loyalty Point Reward Improvements** 
''Loyalty Point (LP) reward improvements are broken down by corporate divisions. All are 10% gains, per level trained, in LP rewards while working for an agent from their specific division.
- 
- 
- 

The following are the skills in the Social section (in alphabetical order):

| Skill (Multiplier) | Purpose | Alpha Limit |
| :--- | :--- | :--- |
| Connections|mult=yes}} | Boosts standings from NPCs (agents, corps, and factions) if above 0.0 standing. | Connections}} |
| Criminal Connections|mult=yes}} | Boosts standings from NPCs with negative CONCORD standing. | Criminal Connections}} |
| Diplomacy|mult=yes}} | Boosts standings from NPCs if below 0.0 standing. | Diplomacy}} |
| Distribution Connections|mult=yes}} | Improves loyalty point gain when working for Agents in the Distribution Division. | Distribution Connections}} |
| Fast Talk|mult=yes}} | Faster security standing increases. | Fast Talk}} |
| Freelancing|mult=yes}} | Increases the number of concurrent Freelance Jobs a character can accept. | Freelancing}} |
| Mining Connections|mult=yes}} | Improves loyalty point gain when working for Agents in the Mining Division. | Mining Connections}} |
| Negotiation|mult=yes}} | Increases ISK rewards offered by mission agents. | Negotiation}} |
| Security Connections|mult=yes}} | Improves loyalty point gain when working for Agents in the Security Division. | Security Connections}} |
| Social|mult=yes}} | Boosts the size of standings increases with NPCs, NPC corporations and NPC factions. | Social}} |

# Skill Details

{{Skill
|skill=Connections
|desc=Skill at interacting with friendly NPCs. 4% Modifier to effective standing from friendly NPC Corporations and Factions per level. Not cumulative with Diplomacy or Criminal Connections.
|1=Charisma
|2=Intelligence
|pre=
|notes=Your effective standing is calculated using the following formula:
Effective Standing = Unadjusted Standing + ((Maximum Possible Standing - Unadjusted Standing) * Connections Modifier * Connections Skill Level)
So if your current base standing is 0.9 and you have the connections skill at level two your effective standing will be:
0.9 +(10-0.9)*0.04*2=1.628
}}

{{Skill
|skill=Criminal Connections
|desc=Skill at interacting with criminal NPCs. 4% Modifier per level to effective standing towards NPCs with low Concord standing. Not cumulative with Diplomacy or Connections. 
|1=Charisma
|2=Intelligence
|pre=
|notes=Namely Pirate factions:
- **Angel Cartel**
- **Guristas Pirates**
- **Sansha's Nation**
- **Serpentis**
- **The Blood Raider Covenant**
}}

{{Skill
|skill=Diplomacy
|desc=Skill at interacting with hostile Agents in order to de-escalate tense situations as demonstrated by some of the finest diplomats in New Eden. 4% Modifier per level to effective standing towards hostile Agents. Not cumulative with Connections or Criminal Connections.
|1=Charisma
|2=Intelligence
|pre=
|notes=
}}

{{Skill
|skill=Distribution Connections
|desc=Understanding of the way trade is conducted at the corporate level.

Improves loyalty point gain by 10% per level when working for agents in the Distribution corporation division.
|1=Charisma
|2=Intelligence
|pre=; 
|notes= * Distribution Connections is purchased with **Loyalty Points** (LP) from NPC stores, so the price may vary wildly.
}}

{{Skill
|skill=Fast Talk
|desc=Skill at interacting with Concord. 5% Bonus to effective security rating increase.
|1=Charisma
|2=Intelligence
|price=90K 
|pre=
|notes=
}}

{{Skill
|skill=Mining Connections
|desc=Understanding of corporate culture on the industrial level and the plight of the worker.

Improves loyalty point gain by 10% per level when working for agents in the Mining corporation division.
|1=Charisma
|2=Intelligence
|pre=; 
|notes=*Mining Connections is purchased with **Loyalty Points** (LP) from NPC stores, so the price may vary wildly.
}}

{{Skill
|skill=Negotiation
|desc=Skill at agent negotiation. Improves agent effective quality. 5% additional pay per skill level for agent missions.
|1=Charisma
|2=Intelligence
|pre=
|notes=
}}

{{Skill
|skill=Security Connections
|desc=Understanding of military culture.

Improves loyalty point gain by 10% per level when working for agents in the Security corporation division.
|1=Charisma
|2=Intelligence
|pre=; 
|notes=*Security Connections is purchased with **Loyalty Points** (LP) from NPC stores, so the price may vary wildly.
}}

{{Skill
|skill=Social
|desc=Skill at social interaction. 5% bonus per level to NPC agent, corporation and faction standing increase.
|1=Charisma
|2=Intelligence
|pre= 
|reqI=; 
|reqII=
|reqIII=; ; ; ; ; 
|reqIV=
|notes=
}}
