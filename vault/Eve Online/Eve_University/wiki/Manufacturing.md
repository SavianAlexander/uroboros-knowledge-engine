---
title: "Manufacturing"
url: "https://wiki.eveuniversity.org/Manufacturing"
pageid: 321
source: "EVE University Wiki"
categories: ["Candidates for cleanup", "Industry"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Manufacturing

In the EVE universe, the vast majority of items are manufactured by player characters and traded in a relatively free way in the marketplace. Students of economics will note that these markets are neither perfect nor efficient in the technical senses; volumes of many items are low enough that the market can be (and is) manipulated, and the supply of materials and modules is partly provided by loot drops in missions, which can be adjusted without warning by the game developers. Similarly, the developers may adjust the requirements for a manufacturing process, or increase the availability of ore, or otherwise mess in the sandbox.

Nonetheless, manufacturing and selling items can provide interest and ISK profit for the careful and canny player. The player must be aware, however, that there are plenty of items that destroy value - that is, there are a great number of Tech 1 items, modules especially, that are worth **less** than the cost of manufacture. Many more items can be sold at a profit, but only in a limited volume in certain markets. Manufacture in these cases may simply be an alternative to hauling stuff between markets.

1. # Skills
The following skills are useful or required for all production that can be done.

- - 4% reduction in manufacturing time per skill level.At least level 1 is required to use most blueprints, and level 3 is required for further manufacturing skills. The speed bonus increases the rate at which you can produce items (and therefore, produce profit).
- - 3% reduction in all manufacturing & research time per skill level.This skill adds not only a fairly substantial further time reduction in manufacturing but also a time reduction in all **research** and **invention** jobs. Whilst less noticeable when building small items individually, these time-savers add up when doing multiple runs and building large ships.
- N.B When manufacturing an item you will want to consider that the items themselves can require prerequisite skills in order to make it in the first place, not just to fit it. So if the START button is still greyed out then check the item blueprint's skill requirement to find out why the manufacturing job won't run.

Increase the number of concurrent jobs:
- - Allows 1 additional job per level. By default, all characters can run 1 manufacturing job at a time. Training this skill lets you run additional jobs simultaneously from 2 jobs at I up to 6 jobs at V. Any industrialist who wants to create things will need to train this to IV or V fairly early in their plans.
- - Allows 1 additional job per level. Once you train Mass Production to V, you can then train Advanced Mass Production, for a further increase in concurrent jobs. Having this skill at IV gives you 10 manufacturing lines (1 + 5 + 4), which is enough for most people. Training to V takes around 28 days, making it only of interest to dedicated manufacturing characters.

Allow remote management of jobs:
- - Allows starting jobs remotely. +5 jumps per level. Without training this skill, you can start jobs anywhere in the current system. Each level in this skill gives you the ability to start manufacturing jobs an extra 5 jumps away, to the maximum of 25 jumps at level V (this may include other regions).This skill is more of a convenience skill than a must-have for a budding industrialist - allowing you to manage your production lines for a distance. If you invest in this skill, training to level III or maybe level IV would offer the most return on time investment. Note that you still have to haul the materials and blueprint to the relevant station.

1. # Basics of production
Production of Tech 1 items - ships, modules, ammunition, rigs, or even components - is the simplest of manufacturing tasks, within reach of even the newest player to EVE. However, whether they will be able to make a profit is another question entirely. Very few skills are needed for Tech 1 production, and the materials are often fairly easily acquired. 

All Tech 1 manufacturing jobs require a blueprint. These come in two forms: originals (BPOs) with infinite runs and copies (BPCs) that can only be run a limited number of times. For most blueprints, a single run of a blueprint will produce a single item, but there are some exceptions - most obviously ammunition, which produces 100 units per run.

Many manufacturers use BPCs, copied from a BPO, to manufacture, for a variety of reasons, including security and the ability to run multiple production lines. For more details, see **Why should I copy my BPOs?**

See **Blueprints** for more details on blueprints.

  1. ## Selecting the item to produce
Tech 1 BPOs are seeded by various NPC traders, with costs varying from 100,000 to 75 billion ISK. This can be a significant cost, especially to new players. Also significant is the amount of research time that may be spent on the blueprint. Selecting a good one versus a bad one is important!

A good item will have these characteristics:

- **Inexpensive Materials** - The material cost should be such that you can reasonably expect to manufacture a decent number of items, and you won't be bankrupt if you lose them while trying to sell them. There isn't a rule on how much cost is too much, but if you need a number then keep the cost of an item below 1% of your net worth. This will not be a problem for players with a large wallet but can be an issue for new players starting out in manufacturing. Loading the potential BPO into the Industry window will provide an estimate of the material cost.

- **Good Profit Margins** - The difference between the selling price and the cost to manufacture should be worthwhile. Be sure to compare the absolute profit (ISK) and percent profit (% of selling price) and make sure both are worth your time. What makes it worth your time? It is up to the individual, but strive for at least 10% per item. Profits of 80% have been witnessed by players as young as 2 months to EVE, but they are rare and tend to disappear.

- **Good Transaction Volume** - If you find an item that is extremely profitable but is only sold once per week, then it has poor transaction volume. There is no guarantee that you can capture all (or even most) of the sales of a particular item! To check the volume of an item, use the Market window. If you choose an item, click on the Price History tab. If it shows a graph, you can see daily sales volume by clicking the Show Table button in the bottom of the window. This will show you how many of an item were sold each day in the region over the past year.

Many items do meet all three requirements. Finding them is a matter of a lot of research time looking for items that meet your criteria. Typically it is easiest to search through the market tab looking for items with sufficient volume, then go to the BPO research calculator to compare the prices to selling volumes. Once you choose a blueprint, the BPO Research Calculator will also tell you what faction sells the BPOs you have chosen.

=== Total job cost === 
Raw materials are not the only cost of production. The act of installing the manufacturing job costs too and the job installation fee is a factor that cannot be ignored. In choosing where to base your manufacturing operation consider the installation cost of industry jobs. This cost is dynamic, so if a large number of other manufacturers join you in the system, it may save you money to move elsewhere (weighed against the cost in time and effort of moving all your materials to a new system).

> <math> \displaystyle \text{Total job cost} = {\color{green}\text{Estimated item value} } \times ( ( {\color{blue}\text{System cost index} } \times \text{Structure bonuses} ) + \text {Facility tax} + \text{SCC surcharge} + \text{Alpha clone tax} )</math>

The estimated item's approximate value is the cost estimation of the materials for a ME0 blueprint with no bonuses applied. The exact values can be calculated by multiplying the number of items with the adjusted prices of the items (found in ESI [/markets/prices/](https://esi.evetech.net/ui/#/Market/get_markets_prices) endpoint).

> <math> \displaystyle {\color{green}\text{Estimated item value} } = \sum_{\text{all materials}} ( \text{Material quantity} \times \text{Material adjusted price} ) </math>

The system cost index is calculated from the amount of production job hours done in system and the amount of production job hours done in universe.

> <math> \displaystyle {\color{blue}\text{System cost index} } = \sqrt{ \frac{ \text{Work hours done in system in past 28 days} }{ \text{Work hours done in universe in past 28 days} } } </math>

You will also need to pay taxes. The taxes are based on the Estimated item value. The tax is composed of the following elements:

**Facility tax : Fixed at 0.25% for NPC stations. Set by the owner for player structures.**:

**SCC surcharge : Fixed at 4%**:

**Alpha clone tax : Only applicable to **Alpha clone**s, set to 0.25%**:

The maximum tax that can be set for industry services will be capped at 10%.

  1. # Running jobs

Once you have a blueprint and materials ready, and decided which system to manufacture in, it's time to produce your goods. Most of the time you'll be using an NPC station to manufacture goods. 

Engineering complexes and citadels with the appropriate service module online can also be used to manufacture goods. Engineering complexes provide a modest material savings (1%) and significant time savings (15% - 30% depending on size) over NPC stations; these savings can be further increased for certain categories of goods by installing the appropriate rigs to the structure.

Gather the materials and BPO (or BPC) in your station hangar, and open the industry window. You will need to find your blueprint using the drop-down selection boxes. Click the blueprint to install it to the main industry window. Or you can start the job from the blueprint in your hangar.

Simply choose the number of runs, check the input/output locations (most of the time this will simply be Item Hangar, but if you have your own personal corporation or use containers for sorting you may need to change them - note: if the industry window says you are missing inputs that you know you have, check to make sure all input/output choices are from/to the Item Hangar) and press Start. 

While the job is running, you can check on its progress using the same Industry window, in the Jobs tab. Select the Jobs tab, and a list of your currently running jobs will be displayed. You can cancel the job if you want your blueprint back for some reason, but none of the materials used or installation costs will be refunded.

Finally, once the job is completed, job listed in the Jobs tab will contain a large Deliver button instead of a time remaining display; press this and the results & blueprint will be returned to the station.

  1. ## Beware of rounding "errors"!
A particular problem that can quickly cost you a million ISK or two when manufacturing Tech 2 items is the rounding that is applied as an effect of material efficiency. The rounding is done per job instead of per run. a single industry job with 3 runs can use *less* material than 3 single jobs from the same blueprint!

Additionally, the manufacturing job will require at least one item of each type per run. This is most notable when the job requires one item per run. With 100 runs and 10% material reduction, you would assume that you would need 90 items but you still need 100 items.

1. # Storyline production
  - COSMOS missions** and data sites are a source of storyline module blueprint copies. These modules require rare components that can be found in data sites, relic sites, and COSMOS sites.

To manufacture them you will also need few extra skills:

- 
- 
- 
- 
- 
- 
- 
- 

1. # Booster production

Boosters are manufactured from mytoserocin and cytoserocin gas harvested from clouds in **cosmic signatures** found in known space. These signatures only spawn in specific regions of New Eden. These gasses are distinct from the fullerine gasses found in wormholes, which are used to create Tech III ships and subsystems.

Booster production requires the following skill:

- - Required for manufacturing drugs.

If you also want to refine the gas used for drug manufacturing you will need the relevant **reaction** skills.

  1. # Processing gas
Gas must be processed into pure booster material before the final product is created. This is done using reactors at a **refinery** structure.

Pure boosters use Simple Reactions at a Standup Biochemical Reactor I. These structures can only be installed at a refinery in 0.4 or lower security space. Besides the gas, the reactions also require an additional unit, which varies based on the grade of the booster. Synth reactions need Garbage, Standard reactions require Water, Improved reactions require either Spirits or Oxygen, depending on the exact product, and Strong reactions require Hydrochloric Acid.

  1. # Booster creation
Boosters themselves are created as a normal manufacturing job in industry window. This has no security requirements and can be done in high security space. Manufacturing the final booster product requires the pure booster material of the desired grade covered in the above section, megacyte, and an appropriate blueprint.

1. # Tech 2 production

Tech 2 manufacturing requires Tech 2 BPCs, which are 'invented' through the invention process. This is a chance-based process, requiring a lot of skill investment in advance, and you are not guaranteed to get a Tech 2 BPCs at the end of it. Some Tech 2 manufacturers do not invent, but instead merely buy Tech 2 BPC packs from dedicated inventors. See **Invention** for more details on the invention process.

There are also limited number of extremely valuable tech II blueprint **originals** in circulation. These were seeded years ago in the so called "Blueprint lottery" and new tech II blueprint originals will never enter the game.

Tech 2 production also requires a much wider range of materials compared to tech I production.

  1. # Skills required
The main difference between tech 2 and tech 1 manufacturing is the increased skill requirement, and the many more different types of input materials required. Not all Tech 2 manufacturers will have all these skills, some may specialize in (for example) constructing only Minmatar ships, and thus have only those skills.  Most of these skills are the same as those required for invention. Different blueprints require these skills at different levels, but in general: the larger the ship or item, the higher skill level will be required. Most of these skills also give a 1% time efficiency bonus per level.

- 
> Required to build Tech 2 ships of any size & race.

- 
- 
- 
- 
> Required to build Tech 2 ships of the relevant race.

- 
- 
- 
- 
> Required to build Tech 2 ships of the relevant size. These skills are not required for invention, only construction.

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
> Two of these skills are required to build each Tech 2 (non-ship) item. These are the same as the skills required to invent that Tech 2 item. Consult a blueprint to find out which skills at which level are required to build that item. Example (see right): Nanofiber Internal Structure II BPC requires Nanite Engineering and Molecular Engineering.

  1. # Tech 2 required materials
Whereas the majority of Tech 1 production requires only minerals, the range of input materials required hugely expands for Tech 2 production - moons, planets, items and components are all potential sources of materials for Tech 2 production. Not all Tech 2 blueprints require every single source of input material, but one particular additional input required for most Tech 2 manufacturing is a Tech 1 item of the similar type. For example building a Tech 2 nanofiber requires a single Tech 1 nanofiber, some Remote Assembly Modules (Armor/Hull Tech R.A.M.s), extra minerals (Morphite) and some planetary materials (Construction Blocks). 

  1. ## Moon materials
Moon materials are produced via moon mining, which is an activity only possible in 0.5 security space and lower, and requires a Refinery anchored next to the moon mining beacon you wish to mine from and fitted with Moon Drill module. It is also very lucrative, and some moons are fought over regularly, so being able to defend your structure is necessary if you wish to maintain your moon mining operation.  Moon mining is an activity carried out on the corporation or alliance level, and thus generally not possible (to run a profitable operation) as a solo player. 

Moon materials - basic elements such as Chromium, Technetium, and Tungsten, which can be found in the Reaction Materials > Raw Moon Materials section of the market - are mined and then reacted together in the refinery to produce advanced moon materials - such as Tungsten Carbide, Fullerides and Fermionic Condensates. It is possible however to run a profitable reaction only operation: buying the raw moon materials on the market, reacting them together in your refinery (and it does have to be in lowsec or nullsec) and then selling or using the advanced moon materials.

These advanced materials are sometimes used directly in Tech 2 item manufacturing, but more often used in the construction of advanced components, which are then in turn used in Tech 2 manufacturing.

See **Moon mining** and **Reactions** for more details.

  1. ## Components
Advanced components are the most common type, and are manufactured exclusively from moon materials. They are used in the majority of Tech 2 manufacturing, Tech 2 ships in particular using large numbers of multiple different types of components. Components come in Amarr, Caldari, Gallente and Minmatar flavours, with the icon coloured according to which race they 'belong' to. The advanced component manufacturing process is just like any other Tech 1 manufacturing process, except that the inputs are moon materials, and one particular science skill (see list of Tech 2 skills required above) is required for each component.

Tech 2 items frequently use these racial components as well as ships, and the particular racial component(s) they require will be the same as the racial encryption skill and the racial data interface item required to invent the BPC.

  1. ## Robotic Assembly Modules (R.A.M.s)
Robotic Assembly Modules, more commonly known as R.A.M.s, are robotic assembly units that build things for you.  They are manufactured from minerals just like any other Tech 1 manufacturing process. Nine different R.A.M.s exist, for different types of construction: Starship Tech, Ammunition Tech, Cybernetics, etc.

  1. ## Planetary materials
  - Planetary Industry** can be done with the same character you might use for production, and thus save you expenditure on the market (although, just like minerals you mine are not free, neither are planetary materials you produce).

1. # Tech 3 production

Tech 3 ships, also known as Strategic Cruisers and tactical destroyers have their own specialised construction process, which is a combination of **invention** using ancient relics from relic sites, and including datacores gathered from data sites - to discover the BPCs for hulls and subsystems, and then built using those BPCs with materials gathered from within w-space - including gas clouds (which are reacted in a reactor array), **Sleeper** salvage and normal minerals.

1. # Capital ship construction
Capital ship construction can be an extremely lucrative business, although requiring a large initial investment, and, depending on what capital you are constructing, may need to be based in lowsec, or even sovereign nullsec.

- is required to build capital ships or capital ship components. The following levels unlock the following blueprints:
> *Level 1:* all capital ship components, all capital modules, freighters, **Orca**
> *Level 3:* carriers, dreadnoughts, fighters, fighter-bombers
> *Level 4:* supercarriers, jump freighters, **Rorqual**
> *Level 5:* titans

Capital ships are built from capital ship components, which are in turn manufactured from minerals. There is no restriction on where capital ship components can be built, and apart from the increased skill requirement, there is no difference from other Tech 1 manufacturing. Freighters and the Orca can then be constructed in any manufacturing facility using the relevant Tech 1 ship BPO or BPC, from the components previously built. 

Carriers, dreadnoughts & the Rorqual are capital ships that may not enter hisec, and so you cannot build them in hisec either. They can be constructed in any station in lowsec or nullsec with a manufacturing facility, but apart from that restriction, are constructed in the same way as freighters or the Orca.

These ships may also be constructed at a Large or Extra Large size citadel or engineering complex (i.e. Fortizar, Azbel, Keepstar, or Sotiyo) with a **Standup Capital Shipyard I** module installed. This module is installable in lowsec and nullsec only. Engineering complexes, and structures with appropriate rigs, will provide their usual cost reductions as applicable.

  1. # Supercapital construction
Supercarriers and titans cannot even dock in NPC stations, never mind enter hisec, and so you cannot build them in stations either. They must be built at a Sotiyo engineering complex with a Standup Supercapital Shipyard I service module. installed. This module may only be brought online in systems where the complex owner has sovereignty, and has installed a Supercapital Construction Facilities infrastructure upgrade. Supercapital construction takes an **exceedingly long time**).

Note that while appropriately fit Sotiyo engineering complexes can build and launch supercapitals, such ships will not be able to re-dock once launched. The only structures that support supercapital docking are Keepstar citadels.

Because supercapital ship construction must take place in a player-owned structure, this means supercapital ships under construction are vulnerable to attack, unless you can defend your infrastructure effectively. Many titans have been 'aborted' by a hostile force destroying the POS and assembly array during construction.

1. # Useful links
- [ISK Per hour](https://eveiph.github.io/) Very powerful windows program for Tech 1, Tech 2 and Tech 3 production as well as refining.

1. # References
