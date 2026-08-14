# It’s All About Spaceships

- **Date**: 2025-02-13T13:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/its-all-about-spaceships
- **Tags**: #eve-evolved, #development-updates, #news

## Overview
Deeper ship immersion and a foundation for the future.

---

Capsuleers,

EVE Online uniquely allows players to explore the vastness of space, engage in a complex and ever-evolving community, and carve out a place in a living universe. At the heart of that experience is your ship – your identity in New Eden.

As part of EVE Evolved, changes have been made recently to elevate ships beyond other items in the inventory, overhauling how they are presented and interacted with. These updates are not just visual improvements - they enhance usability, refine how ships are represented in the game, and lay the groundwork for further improvements.


## Cards Against Monotony


The first baby step toward improving ship interaction and giving your vessels the spotlight they deserve was the introduction of ship cards in the hangar. This goal is to bring more information to the forefront, making it easier to see ship types at a glance, and providing quick access to traits and fitting details for owned ships.

While developing ship cards, it became clear that there is a lack of a central authority for ship groups and classifications which presented development challenges. Improvements are needed to streamline ship categorization, but as this is a large undertaking, it was not addressed in this update. However, refining these systems in the future will be highly beneficial.

While not a particularly complex feature, ship cards add a great deal of clarity and usability to ship interactions. Further enhancements to hangar interaction are planned, as many areas of inventory management still have room for improvement.


## The Ship Info Overhaul


The Ship Info window was a much bigger project and greater challenge. Unlike ship cards, which introduced a new way to display ships, this was about rebuilding one of the most used windows in the game – one of the cornerstones of EVE Online!

The most important priority was preserving functionality while ensuring any changes elevated the experience. The approach taken was to frame the new Ship Info window as though it were a manufacturer’s technical brochure, reinforcing the concept that each ship is a real, physical object within the EVE Universe.

A game in continuous development for over 20 years inevitably accumulates technical debt, and the Ship Info window was no exception. Originally implemented early in EVE Online’s development, it had never seen a dedicated overhaul. As new features were added over time, its structure became increasingly difficult to maintain.

A major part of this update involved restructuring the various services and components that the old window relied on. The first step was extracting all necessary functionality into a base class, allowing the new window to be built upon a more stable and maintainable foundation.

One of the more unexpected challenges involved rendering the 3D scene in the background. The existing renderer is primarily designed for objects in space, so additional work was needed to integrate it smoothly into a UI environment. A solution was developed that not only worked for this window but also sets the stage for more 3D rendered UI elements in the future.

The result is a more immersive and functional Ship Info window, improving how ships are viewed in the ship tree, in hangars, and in space.


## The Community Response


A change of this scale was bound to generate strong reactions. Some were a bit more vocal than others, and some, let’s say, interesting bug reports were submitted. Despite some particularly passionate opinions being voiced, most of the feedback gathered was constructive, thoughtful, and quite valuable. 

The support is greatly appreciated and was very useful in refining the final product.

The Ship Info window is only the beginning. Many ideas surfaced during development, both internally and from community feedback, for example compact mode which was added recently. Some other great ideas also surfaced but didn’t make it into the first release. These include further improvements to the 3D view, triggering warp animations, further improving the fitting panel, and more that will be explored in the future. With the new framework in place, these and further refinements will be easier to develop and roll out and might lead to more specialized UI elements as well.


## The Boarding Cinematic


Ships are the heart and soul of the EVE experience. They represent investment, progress, and identity. In a game built around acquiring and piloting different vessels, boarding a new ship should be an exciting experience, not just a menu action. The goal was to make boarding a ship for the first time feel like a milestone. It should be visceral, satisfying, and feel like an achievement.

With hundreds of ships and multiple hangar types, a universal solution was needed. The challenge was to create a system that worked across all ships without requiring individual animation work for each one. 

The answer was to add anchor points to ship models, allowing the camera to follow predefined paths. Ships were grouped based on size and shape, ensuring smooth transitions while maintaining consistency.

Some ships, such as titans and other uniquely shaped vessels, required custom camera movements. For the majority, however, a system based on broad groupings worked to create a seamless and immersive experience without hand-crafting sequences for every single ship.

This feature, while not directly impacting gameplay, strengthens immersion and reinforces the connection between capsuleers and their ships. The groundwork laid here also opens the door for more dynamic cinematics in the future.

There are still multiple factors that can be added and improved, and as ever, this will continue to evolve along with EVE Online. These are strong foundations to inform future enhancements to the UI for a deeper immersion than ever before.

Fly safe.

o7
