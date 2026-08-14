# EVE Evolved: Aura Guidance

- **Date**: 2026-02-17T11:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/eve-evolved-aura-guidance
- **Tags**: #development-updates, #new-features, #news

## Overview
Helping rookie pilots learn the ropes.

---

Progressive capsuleers,

Today we released the second of three EVE Evolved instalments coming this month, continuing the EVE Forever initiative. 

A new Aura Guidance system delivers player-generated knowledge based on real Rookie Help questions and answers in an automated, easy-to-digest way, to help reduce confusion for new pilots.

Aura Guidance is designed to complement, not replace, the human guidance that has long defined EVE. As this is a prototype in a **test phase**, we are analyzing its performance to help us determine what to keep, what to discard, what to improve, and whether to shut it down or develop it further. Failure is an option. 


## Addressing Rookie Confusion


EVE Online is a complex game. The complexity is what makes it special but also makes for a harsh first experience. Many players leave before ever reaching the parts of EVE that keep people playing for decades. We know this happens. Understanding exactly where and why has been the hard part.

A decision was made to investigate the use of AI to address this issue, and around Fanfest last year, a dedicated team was formed. The first month was spent purely on identifying problems.

The team’s roots are in healthcare AI, with experience diagnosing diseases from biometric data. Getting those answers wrong has life-altering consequences. 

That mindset carries over into this work: be careful, be honest about what you don’t know, and don’t guess.

A core focus has been questions asked by new players because confusion in the first hours can be detrimental to enjoyment and retention. When a player gets stuck and can’t figure out what just happened, that can determine whether they keep playing or log out for good.


## Lessons From Rookie Help


The in-game Rookie Help channel has long been one of the most important resources for new pilots. It’s social, human, and often remarkably effective. When we started using it ourselves during research, the quality of answers was better than expected, compared to other games.

To understand where new players struggle, we analyzed Rookie Help chat from January through September 2025. The numbers revealed a lot.

**5.8 million** messages were analyzed. **706,000** genuine questions identified. The most frequently asked individual question appeared only **176 times** across the entire dataset. That’s 0.025% of all questions.

There is no meaningful “top 20” list of questions that can be solved with a simple FAQ. There are certainly top themes, but the questions themselves vary wildly depending on where you are, what ship you’re in, what the situation is, and how long you’ve been playing. Two players can ask about the same topic and need completely different explanations because their situations are different.

We also found something revealing in the data. The most common questions in Rookie Help, by far, are things like “How do I do that?”, “What is that?”, and “What do you mean?” These are the top questions overall. Players get an answer and still don’t understand it. Someone tells you about low security space and Concord, but you don’t know what lowsec is yet. The answer is technically correct, but it introduces new concepts you’ve never seen before. The confusion just deepens by one layer.


## Why Aura Guidance?


EVE already has strong guides, tutorials, and documentation. They are accurate, valuable, and not going anywhere. However, every time a new player alt-tabs to read a guide, there’s a real chance they won’t come back.

We want to keep players in the game. When a question gets answered within the client with links to ships and items, players see things they did not know existed. A new player asking about mining might discover a ship they want to fly right away. 

If an answer mentions the fitting window, clicking it highlights it in the client. Rather than just explaining in text, Aura Guidance can guide you through the UI directly. That inspires curiosity, which is a hook, and it only works if the answer shows up where they are already playing.

EVE knowledge is situational. Understanding depends on where you are, what you are flying, and the current situation. Every additional login makes a player more likely to discover the wonders of EVE. We want to help people get to that point.


## How Aura Guidance Works


You may have already seen the purple icon floating around. Some of you already spotted leaked feature toggles and the theorycrafting started immediately. We loved reading those theories.

Here’s how it actually works.

We built a Q&A bank from real Rookie Help conversations. The algorithm goes like this:


1. Identify a question in Rookie Chat.
2. Check if the question is general enough to help other players.
3. Fetch the next 10 messages in the same chat.
4. Determine if the question got properly answered.
5. If both checks pass, clean it up: generalize the question and answer, remove player names, links, and tags.
6. Store the pair in the Q&A bank.


There are tens of thousands of entries in there already.

When a player asks a question through Aura Guidance, we embed their question and match it against this bank. We find the questions closest to player questions with existing answers, from real players and ISD volunteers. Those Q&A pairs are pulled, and a response is synthesized from the retrieved content, enriched with the player’s current context: their location, ship, recent deaths, whether they are docked, and so on.

The player’s actual question is never sent to a language model in its raw form. This is deliberate. It does not stop players from trying to break the system with toxic inputs or prompt injection, but it does make those attempts a lot less effective. We look up similar questions instead and build from those answers.

When the system cannot find a confident match, it does not answer. It redirects players to Rookie Help. This is a feature, and it happens often. 

**Aura Guidance is not a replacement for Rookie Help**. 

We want to push people toward asking other players. Typing questions into a public channel for the first time is scary for many people, and we think Aura can help lower that barrier by helping players figure out what to ask.

Aura Guidance is designed for common rookie questions, but being a new player in EVE is not binary. You may have played for 15 years and still be a complete beginner when it comes to mining or wormholes. We think there is potential here for something broader down the road, but we’re starting with solutions for the newest players.

**What Aura Guidance Doesn’t Do**

Let’s be clear about some things that Aura Guidance intentionally does NOT do: it does not give fleet advice, market strategies, or detailed fitting optimization. It does not help you win fights or earn ISK faster. It does not replace the depth of knowledge you get from experienced players, mentors, or specialized communities. Those limitations are by design.


## Safety and Trust


Aura sees limited information about the character asking the question. Only enough to give context-aware answers. What it has access to will expand over time as we learn what players are actually asking about and where the gaps are.

Our background in healthcare AI shapes how we think about safety here. Responses are gated by similarity and confidence thresholds. When the system is uncertain, it says “I don’t know, ask other players.” We would rather redirect to Rookie Help than give a misleading answer.

**All responses are built from the vetted Q&A bank. No open-ended generation**. No detailed tactical advice. No guaranteed outcomes that could mislead players. And if the system detects questions about exploits or hacks, it doesn’t even attempt to answer.

Have we seen hallucinations? Yes. The system once made up a ship called the Albatross. These things happen with language models. We have tools to retroactively review conversations and catch these issues, and we are using smaller, faster models for detection that keep getting better at flagging problems. This is an ongoing effort, and we are upfront about that.


## On Your Terms


We know AI is a divisive issue among gamers, but to clarify how we see this tool, Aura Guidance does not generate game content, create art, or replace creative work. It is grounded in existing information created by players and ISD volunteers. The responses come from real answers that real people gave in Rookie Help. We are trying to make that accumulated knowledge more accessible at the right moment.

Aura Guidance is optional. You can close it, right-click it away, unpin it from the Neocom, and it doesn’t change how EVE plays. If you prefer to learn through chat, guides, or trial and error, nothing changes for you. 

The system is also very lightweight on the client side. One request goes out when you ask a question. All the heavy processing happens off-client in the cloud. No impact on performance, no effect on other services. We went out of our way to ensure that opening Aura during a fight does not bring everything to a soul-crushing halt.


## A Prototype by Design


This is an early version. It will have gaps. Some questions will be redirected rather than answered, and some answers will feel overly generic. We are launching it this way on purpose. Those gaps tell us where confusion still exists. Learning what the system does not know is as valuable as learning what it can confidently answer.

**How We’re Testing This**

To begin with, we’re running Aura Guidance as a controlled A/B test. When a new player creates their first character, they are randomly placed into one of two groups. One group gets full access to Aura Guidance while the other group gets the standard new player experience without it. 

After a set period, we compare the two groups. Randomization ensures a fair comparison. We are not measuring how much money players spend or how fast they progress. The only question is: does this help new players stick around? 

The results will tell us what to keep, what to improve, and where to go next.

We will evaluate, and if Aura Guidance doesn’t improve retention, we will shut it down and look for other solutions. Failure is acceptable. This is not a silver bullet. The problem we are trying to solve is real, but this particular approach has to earn its place.


## Looking Ahead


EVE has always been shaped by players helping players. Aura Guidance is an experiment that tries to support that tradition by reducing early friction and helping new players reach the point where the opportunities of New Eden open up.

We see potential for this to become a kind of “no stupid questions” space. The privacy of your own screen, where you can ask what docking means without raising your hand in a public channel. Where you can get nudged in the right direction and then go figure it out yourself or go ask a real person with a better question in mind.

If it helps even a small number of players push past early confusion and keep exploring New Eden, that is worth trying.


## A Note on Environmental Impact


We take the environmental cost of running AI systems seriously. Our architecture is designed to minimize it from the ground up.

Aura Guidance is retrieval-first. There is no open-ended generation, no reasoning chains, or self-reflection loops. Each question gets a single, short answer. We only run small language model variants, and we evaluate new models with energy cost as a factor.

To put the footprint into perspective, even under generous assumptions where every active player sends a question every day, Aura Guidance's annual energy usage would be comparable to running a single small European household for a year. That is a rounding error next to the energy consumed by the game servers themselves.


## We want your feedback


We'd love to hear your thoughts on Aura Guidance as we refine it with your feedback. Specifically where it helps, where it goes wrong, and your thoughts in general. 

Swing by the [EVE Forums](https://forums.eveonline.com/t/aura-guidance-beta-feedback-thread/506798) or the [EVE Discord's Aura Guidance thread](https://discord.com/channels/940573867192221696/1473272703271047352).
