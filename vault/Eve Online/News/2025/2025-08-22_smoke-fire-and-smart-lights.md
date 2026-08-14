# Smoke, Fire & Smart Lights

- **Date**: 2025-08-22T11:00:00.000Z
- **Category**: dev-blogs
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/smoke-fire-and-smart-lights
- **Tags**: #development-updates, #eve-evolved, #new-features, #dev-blogs

## Overview
Delivering a more modern, dynamic and reactive visual experience in New Eden

---

Today, we're diving into what team TriLambda, EVE Online’s Art team has been cooking up behind the scenes in the vibrant world of EVE Online's visual effects, while supporting all the expansion features and updates we continue to deliver.

Hear it directly from our devs! Check out the accompanying podcast for this dev blog, here:

It's no small thing to be working on a game that’s in its third decade of live operation, and to make sure we continue to be able to do so, in an ever improving way each year, then one of our core goals continues to be: delivering a more **modern, dynamic, and reactive visual experience,** an experience that not only looks incredible, but one that reflects *your* impact on the universe. We might not always reach it, but having goals like this, gives us something to continually strive towards, and as always, it's all about delivering the best thing we can, in the time we have.

So here for your enjoyment, and imminent arrival in the game client itself, are a couple of the things currently making their way through our celestial cookery.


## **Lighting the Future: Smarter FX for Smarter Spaceships**


Over the past year, we’ve been reworking the fundamentals of how the base VFX pass given to any given ship looks and behaves in space. You may have noticed our updated frigates, with enhanced lighting and visual responsiveness a while ago, where frigate VFX began to change visually based on context; like entering warp or docking, bringing more immersion and fidelity to the moment-to-moment experience.

Originally, our plan was to extend this reactivity across all ships. However, the existing methods were cumbersome to author and expensive in terms of performance. So, we went back to the drawing board and created something new: “**Smart-Light-System**”

This Smart-Light-System is designed to:


- Be **more efficient** on your system. - As things are batch rendered.
  - As we no longer require legacy systems to trigger an ever increasing amount of parameter bindings (now all that functionality is built in to automatically apply to things in this new system).
- Be **easier for us to implement** on a broader scale. - As for each race/faction we can now author shared recipes with built in (much more performant) logic that can trigger off of whatever triggers we might send to them, for example, “in warp”, “in station”, “in combat” etc.
- Support new **visual storytelling tools** like the ability to animate instanced meshes, which can be used for future improvements to space scenes like adding debris fields, enhanced debris in explosions, or entirely new VFX concepts.


It also does a lot more than just lights, it handles every component required to make a beautiful light prefab, that can be spawned onto the intended locations on a ship.


- Including for example; a flare or two, a pointlight, a cone light, a long stretchy beam etc – and the system being based around plug and play components; whatever prefabs groupings of cool combinations of parts we can think of in the future.
- Then we can share those prefabs, for example what an Amarr lightcaster should look like, across all Amarr ships, once the work is done to position and scale in the locators onto which they should go.


Not only do Smart-Light-Sets lay the groundwork for a new standard in authoring EVE spaceship VFX. Thanks to CCP Hank, part of their foundation is also the basis for the next generation of our VFX propagation tool. The previous generation of this tool is already in use in cinematic experiences, such as the ship boarding sequence introduced last year (see: gas jet emissions across ship surfaces as the ships spool up and down during takeoff and landing in Upwell hangars, and a dozen more implementations around New Eden).


## **The Return of Fire – A Long-Awaited Feature**


Let’s rewind to 2019. When we shared a little dream: ships catching fire when taking hull damage, like they did in the early days of EVE. 

It’s taken us a while to find a way to do this, but we’re happy to say that, after a couple mass tests to test the feature with as many people as possible (as well as to iron out any game crashing edge cases we could find (Who seriously changes skins while in the middle of going through a jumpgate!), this long-awaited feature is now on track to release on 26 August 2025. And thanks again to all of the pod pilots that showed up to our mass tests for this feature, your assistance is invaluable in helping us test these kinds of features.

Here’s what to expect:


- On high shader quality settings**, Fires will explode into existence and trail behind ships** when ships enter hull damage, providing immediate and intuitive visual feedback during combat. - When you go to medium or low settings, this system will not load onto spaceships, this is of course for fleet fight performance when needed, something we are ever conscious of.
- **Fires will respond dynamically** to movement, stretching when speed-boosting, adding drama to your already heightened heart rate.
- **We are also happy to announce that since EVE Fanfest we have also added a structure fire system onto most structures that made sense to start with; **Citadels, Refineries, Moon Miners, Skyhooks, Navigation Structures, Industrial Arrays and Outposts. - Here there are 10 fires per structure, roughly linked to happen at each 10% of hull damage.


*“I've seen things... seen things you little people wouldn't believe. Attack ships on fire off the shoulder of Orion bright as magnesium...”*

Fires across ship classes:


- **Frigates** will show 1 fire effect (much larger in relation to the ship)
- **Cruisers and battleships** get around 2–3, and the larger the ship is, the smaller the fire. These also show up progressively as your ship takes more hull damage
- **Capitals and Titans** will have up to 7, giving a real sense of scale, while not going overboard!


The addition of **smoke and fire effects** on damaged ships isn’t just about visual flair, it’s also about enhancing **situational awareness** and **atmospheric storytelling** during gameplay. In the chaos of fleet battles or fast-moving skirmishes, these effects provide a **clear, intuitive signal** that a ship is in hull damage, without needing to lock it or go through the overview. Not to mention it also being more enjoyable to see your enemies driven before you… on fire.


## **Logical next steps…. What Happens When You Dock While on Fire?**


Well... we couldn’t just let you sit there burning forever, right?

Enter: **fire BOBs**.

These autonomous drones “BOBs” handle all your hangar-based fire emergencies. They'll zoom in to extinguish the blaze upon docking, ensuring your flaming wreck doesn’t compromise the station’s structural integrity (or aesthetic).

Once the fire's out, **lingering smoke** will start to emit from the locations that were on fire, serving as a reminder that while the flames may be gone, the damage remains.

And yes… **if you undock without repairing**, the fires will reignite.


## **A Growing Family of BOBs**


Fire BOBs are joining a growing family of utility drones adding life to New Eden:


- **Technical BOBs** have been seen quietly doing their jobs around Upwell hangars since their release in 2022
- **Inspector BOBs** have already been checking out your ships since December in all hangars
- **Security BOBs **have been spotted in faction warfare stations when suppression levels go up
- And now, with **fire BOBs** on the way, we couldn’t help but think some **repair BOBs **should show up when you fully repair your ship


These repair BOBs come in two different sizes (Large BOBs and Mini-BOBs), as well as a distinct visual look for each faction's hangar.

Contrasting these against the repair BOBs the fire BOBs are all kitted out in the colors of a certain country’s fire trucks (Iceland), and include specialized canisters of fire retardant on their sides (which can also be described as “a repair bob with a fire extinguisher strapped to it”).

These small moments. BOB inspections, fire BOBs coming to put out fires, repair BOBs massing to repair your ship, help add depth and atmosphere to your ship hangars, not to mention that little bit of polish we love to see.

Note:

These changes **don’t affect gameplay timings** at all. If you repair and undock immediately, then you will be fully repaired when you emerge outside the station as before. 


## **Coming Soon**


This next visual update is scheduled for release on 26 August 2025, as part of the Legion Expansion Era. It includes:


- The "**Smoke and Fire"** system for ships in hull damage
- The **"Smoke and Fire"** system for player owned structures in hull damage
- The introduction of **fire and repair BOBs to all hangars**
- The **first batch of ships** equipped with **Smart-Light-Sets**


We're excited to bring this new layer of immersion to EVE Online and look forward to seeing your ship battle-scarred, smoldering or still on fire and alive and kicking in the depths of space.

Fly safe (or don’t… those fires aren’t going to burn themselves).

- **The EVE Online Art Team**
