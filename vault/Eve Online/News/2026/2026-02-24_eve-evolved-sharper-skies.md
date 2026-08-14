# EVE Evolved: Sharper Skies

- **Date**: 2026-02-24T11:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/eve-evolved-sharper-skies
- **Tags**: #development-updates, #new-features, #news

## Overview
The third and final EVE Evolved update this month has arrived. This time, the spotlight is on visuals: from an overhaul of New Eden’s resource-rich asteroids to refreshing ORE ship visuals.

---

Visual capsuleers, 

The third and final EVE Evolved update this month continues the ongoing commitment of EVE Forever. EVE Online is renowned for its visuals and graphics, and we remain committed to setting the standard and leading the charge in visual excellence. Therefore, the spotlight is on visuals this time: from an overhaul of New Eden’s resource-rich asteroids to refreshing ORE ship visuals. 


## Visual Foundations


Asteroids, and the resources they contain, are a foundation of New Eden. It is, therefore, a daunting area to bring innovation to. 

The Catalyst expansion introduced new mining destroyers and an epic arc introducing beginners to the world of resource gathering, which got us very excited for the miners of EVE. We decided it was time to look at the foundation of mining and the visuals of standard resource asteroids, which have remained largely the same for a very long time. 


## Fundamental Goals


Starting out, a few fundamental goals were set for the asteroid makeover: 


- Higher visual fidelity, with better models and textures, and more realism
- Model variation between sizes – no more “one size fits all” approach
- More texture variation between different types of ore


The first step was to lay out the old standard resources: rocks, crystals, and ice. We then analyzed their shapes and characteristics, what worked and what didn’t. 

An issue that stood out immediately is that their style could be more realistic. They felt a bit “cartoony.” 

This issue is a side effect of a system that scales asteroids based on the amount of resources they contain. Scaling has the side effect of texture resolution and surface detail decreasing as the asteroid gets bigger, which was combated with tiled textures to give the impression of greater details. Neither the tiling nor the static 1024x1024 pixel texture changes as the asteroids grow or shrink, meaning that asteroids look the same whether they’re the size of a pebble, boulder, or mountain. The model, polycount, and textures remain the same. 

It was clear that this required a completely different approach. 


## New High Poly Source Asteroids


We started by sculpting completely new, high-poly interpretations of the old rock, crystal, and ice assets, keeping the soul and base look of the original asteroids while also meeting our standards for visuals and realism. 

Each type of asteroid gets four visual variations, like the old ones, but to tackle the aforementioned scaling issue, we specifically sculpted unique small, medium, and large variations. That means we end up with four small, four medium, and four large models, resulting in a total of twelve variations for each asteroid type as opposed to only four before. 

The size variations addressed a number of aspects, from general shapes determined by the asteroid’s size to details of crystals and ore that no longer simply scale but change in number, density, and so on. 

For example, on smaller asteroids, crystals will be larger relative to the rock, compared to medium or large ones, and as the scale grows, so will the number of crystals. 

When it came to ice, we decided not to build on the original models, as they didn’t provide a good enough foundation to work from. Based on many references, we went with a more classic iceberg or mountain-ridge look. 

The asteroid models do still scale continuously within a specific ore amount range, but at specific sizes, they are swapped, which helps a lot and prevents crystals and other details like cracks and tiled textures from becoming unnaturally large. 


## High-Poly to Low-Poly and Game Ready


With the new high-poly asteroids in place, we started looking for a practical way to batch-convert them to low-poly in-game assets, including texture UVs, rock/ore material areas, and so on. 

For this, we turned to Houdini, a 3D software package that enabled us to set up a prefabricated mesh-handling process that reduces the polygon count while preserving key shapes and material boundaries. 

In Houdini, we were able to set up preset files to handle all the different asteroid types and defining features. Once we created the low-poly assets, including UVs, we could bake information from the high-poly UVs, such as normals, occlusion, convex/concave maps, etc. 

Following on from the bakes, we can piece together the unique asset textures, which will combine with the surface textures to create the asteroid surface. 

Another cool thing about the new unique size variations is that texture tiling can now be set individually for each size, so both models and textures update as they grow or shrink. 

In the end, we used tiling textures almost exclusively to define the rocky details of the surface, while uniquely baked maps are used to define the overall normal shapes for the rocks and crystals. 

Minimizing the use of asset-specific textures and tiling whenever possible saves memory, which can then be used to increase the resolution of individual textures. This works very well and gives the asteroids a realistic look and feel, from afar and up close. 


## Asteroid Size Logistics


Now we have different asteroid models with varying amounts of ore, which translates into different sizes. So, how do we put them to use? 

Cue the graphics programmers, who sprang into action and authored a new dynamic asteroid type system. 

The old system randomly selected a model from a bucket of four (a graphics ID group) for each asteroid faction (veldspar, for example). Now, we essentially use the same system but expand its functionality, allowing us to add as many buckets as we like. 

These buckets and their size ranges will be set individually for each ore type, and we may be adjusting them a bit in the future. 

Keep in mind that these updates only affect the visuals of asteroids and have no gameplay impact of any kind. 


## VFX & Lighting Pass on ORE Ships


There is also an ongoing effort to modernize EVE’s ship fleet, and we’ve turned our attention to a group of ORE ships. This update focuses on lighting and visual effects, delivering a significant upgrade to the look and feel of these hulls.  

Over the years, the way we build ships has evolved considerably. Many older vessels predate the lighting and VFX standards we use today. 

This latest pass brings these ships closer to current standards while also enabling further standardization of our lighting systems. We applied a similar approach to frigates a while ago, and the process is ongoing. 

Fly safe, fellow capsuleers and miners. 

o7
