---
title: "Reprocessing"
url: "https://wiki.eveuniversity.org/Reprocessing"
pageid: 757
source: "EVE University Wiki"
categories: ["Industry", "Mining", "Needing updates"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Reprocessing

- Reprocessing** (also known as **refining**) allows a player to refine their raw ore into usable minerals that can be sold or used for personal production. However, it is unlikely that new players' skill sets will allow for the efficient use of a reprocessing plant, and large portions of the refined minerals will be lost as "waste", so new players may find it more profitable to sell the raw ore they mine rather than refining it.

1. # Equipment
In New Eden there are two types of reprocessing equipment:
- equipment owned by NPC corporations
- equipment owned by player corporations

If an NPC station is capable of reprocessing your materials, then its equipment will have an efficiency rating between 30% and 50%. Obviously using a station with 50% equipment is better so pilots should take care when choosing a reprocessing station and check this value before use. (You can use third-party map tools like [DOTLAN](https://evemaps.dotlan.net/) to quickly check this)

In addition, NPC stations take a **tax** for using their reprocessing facilities. The tax is based on the player's personal or corporation standings with the station's owner, whichever standing is higher is used. The tax starts at 5% with 0 standings and falls to 0% at 6.67 standings with the station owner. Hence, it's a good idea to reprocess at stations for which you or your corp have the best relationship. See **Equipment tax** below for more detail.

Better processing can be found in player-owned Upwell structures. **Citadels** and **Engineering Complexes** have base rates of 50%, the Athanor refinery has a base rate of 51%, and the Tatara refinery has a base rate of 52%. These percentages can be increased up to 4% through the use of rigging in high-security space, more in low-security space, and even more in null-security space (including **wormholes**).

1. # Pilot skills
There are two generic skills that affect a player’s ability to process raw materials:  and , both of which are available from NPC stations. Reprocessing is the first skill you will need to improve efficiency, and will cost approximately 45,000 ISK. (This cost can be covered by the university's **skillbook program**.) Each level of Reprocessing will increase the pilot's efficiency by 3% for a maximum of 15% increase. Reprocessing Efficiency adds an additional 2% per level, up to 10% at level 5 skill, requires Reprocessing IV to train, and costs 250,000 ISK from NPC stations.

To further reduce waste, there are individual ore skills for each ore type, and a generic ice skill for all ice types—these can be found on the **Resource Processing** page. Each level of that respective skill offers a final 2% increase to efficiency for the corresponding material, 10% at level V. The max possible reprocessing efficiency with all 5 skills, at a 50% NPC station with perfect standings is 70%. Prior to the Lifeblood expansion, the maximum possible efficiency in high-security space was 88% with perfect skills and a +4% **implant** using a fully upgraded citadel. You can never achieve "perfect reprocessing" and there will always be some waste.

For an average player with around 30 days training into reprocessing skills, efficiency yields would typically hover around 63&ndash;65% depending on standings at a 50% station.

| Reprocessing
! rowspan=2 style="width: 14%;" | ReprocessingEfficiency
! colspan=6 | <group> Ore Reprocessing |
| :--- |
| (zero) | I | II | III | IV | V |
| :--- | :--- | :--- | :--- | :--- | :--- |
| (zero) | (zero) | 50.00% | — | — | — |
| I | (zero) | 51.50% | — | — | — |
| II | (zero) | 53.00% | — | — | — |
| III | (zero) | 54.50% | — | — | — |
| IV | (zero) | 56.00% | 57.12% | 58.24% | 59.36% |
| V | (zero) | 57.50% | 58.65% | 59.80% | 60.95% |
| V | I | 58.65% | 59.82% | 60.99% | 62.16% |
| V | II | 59.80% | 60.99% | 62.19% | 63.38% |
| V | III | 60.95% | 62.16% | 63.38% | 64.60% |
| V | IV | 62.10% | 63.34% | 64.58% | 65.82% |
| V | V | 63.25% | 64.51% | 65.78% | 67.04% |

1. # Reprocessing in a station
Before you can process your raw materials you must place the ore in your hangar at a station with a reprocessing plant, or into the cargohold of a player-owned starbase reprocessing array. Batch compressed ores require 1 unit to process, while compressed and non compressed ores require 100 units. You cannot process non batch compressed ores with less than 100 units of a single type, e.g. 75 units of Veldspar cannot be combined with 25 units of Dense Veldspar for processing. Batch compressed, compressed, and non compressed ores yield the same amount of minerals per batch. All ice require 1 unit to process, with compressed ice simply taking 10× less volume (100) than non compressed ice (1,000).

To begin processing, right click the item from your hangar and select reprocess, or drag it to an opened reprocessing window. Once done, you'll have screen that looks similar to this:

In this example, we have 120,000 units of Plagioclase designated for processing. With 69.9% overall efficiency, the processing yield at a glance will give approximately 146,107 units of Tritanium and 58,443 units of Pyerite.

To see more detailed information about exact yields and calculations, simply hover over any item in either the input or output window. For example, hovering over the Plagioclase in the input window shows us the following:
- The base yield from station equipment is 50%.
- With Reprocessing V we have a ×1.15 yield increase. *(1 + 5 × 0.03)*
- With Reprocessing Efficiency V we have a ×1.1 yield increase. *(1 + 5 × 0.02)*
- With Simple Ore Processing V we have a ×1.1 yield increase. *(1 + 5 × 0.02)*
As a result our total net yield is 69.9%.

To calculate this manually, or import into a tool or spreadsheet, you can use the following formula.
> <math>\begin{align}
\mathit{Yield}_\text{total} = \mathit{Yield}_\text{base} & \times (1+\text{Reprocessing }\mathit{skill}\times0.03) \\
& \times (1+\text{Reprocessing Efficiency }\mathit{skill}\times0.02) \\
& \times (1+\mathit{\lang group\rang}\text{ Ore Processing }\mathit{skill}\times0.02) \\
& \times (1+\text{Processing }\mathit{implant}) \\
\end{align}</math>

  1. # Upwell reprocessing formula
> <math> \displaystyle \text{Yield} = ( 50 + Rm ) \times { \color{ProcessBlue} ( 1 + Sec )} \times ( 1 + Sm ) \times ( 1 + ( R \times 0.03 ) ) \times ( 1 + ( Re \times 0.02 ) ) \times ( 1 + ( Op \times  0.02 ) ) \times ( 1 + Im ) </math>

The first three terms define the *"base yield"*. You can use [this calculator](https://docs.google.com/spreadsheets/d/1sydiFz-VXyD37Ehz9wIUcY9m4-bLYiUVbdfAGqsXZHM/edit?usp=sharing) to calculate your reprocessing yield.

| -
! Variable Name !! Meaning !! Valid Values !! |
| :--- |
| <math> Rm </math> |
| <math> \color{ProcessBlue} Sec </math> |
| <math> Sm </math> |
| <math> R </math> |
| <math> Re </math> |
| <math> Op </math> |
| <math> Im </math> |

- Perfect refine in a T2 rigged Tatara in null security space with max skills and an RX-804 reprocessing implant is 90.6%
{{CollapseBox
| The math
| <math> \displaystyle \text{Reprocessing yield} = (50 + 3) \times ( 1 + 0.12 ) \times ( 1 + 0.055 ) \times ( 1 + ( 5 \times 0.03 )) \times ( 1 + ( 5 \times 0.02 )) \times ( 1 + ( 5 \times  0.02 )) \times ( 1 + 0.04 ) </math>

<math> \displaystyle \text{Reprocessing yield} = (50 + 3) \times ( 1 + 0.12 ) \times ( 1 + 0.055 ) \times ( 1 + 0.15 ) \times ( 1 + 0.1 ) \times ( 1 + 0.1 ) \times ( 1 + 0.04 ) </math>

<math> \displaystyle \text{Reprocessing yield} = 53 \times 1.12 \times  1.055 \times 1.15 \times 1.1 \times 1.1 \times 1.04 </math>

<math> \displaystyle \text{Reprocessing yield} = 90.628... </math>
}}

1. # Scrapmetal reprocessing
Scrap metal (module and ship) reprocessing works slightly differently to mineral refining. The user interface is identical, but the calculations are different. Only the  skill affects the output, and is applied directly to the base reprocessing yield of the station or structure. Stations have a base yield of between 30&ndash;50% and structures have a base yield of 50% (this is not affected by structure or rig bonuses). The yield is also not affected by implants, so the maximum possible yield for ships and modules is 55% with perfect skills.

To calculate this manually, or import into a tool or spreadsheet, you can use the following formula:
> <math> \mathit{Yield}_\text{total} = \mathit{Yield}_\text{base} \times (1 + \text{Scrapmetal Processing} \times 0.02 )</math>

To see more detailed information about exact yields and calculations, simply hover over any item in either the input or output window. For example, hovering over the Metal Scraps in the input window shows us the following:
- The base yield from station equipment is 50%.
- With Scrapmetal Processing V we have a ×1.1 yield increase. *(1 + 5 × 0.02)*
As a result our total net yield is 55%.

1. # Ore
  1. # Asteroid ore

 

  1. # Moon ore

Moon ores are separated into five different categories, of which only the Ubiquitous varieties reprocess into regular minerals. Each group has its own reprocessing skill.

1. # Simplified ore chart for in-game notebook

For quick reference, copy the following lines and paste them into your player notes or your notebook. (When you paste them, the lines will close up.)

ORE: MINERAL+AMOUNT (SEC FACTION) +5/10%

Veldspar: Tritanium+400 (1.0 All Space) Concentrated/Dense

Scordite: Tritanium+150 Pyerite+110 (1.0 All Space) Condensed/Massive

Pyroxeres: Pyerite+90 Mexallon+30 (0.9 Amarr, Caldari) Solid/Viscous

Plagioclase: Tritanium+175 Mexallon+70 (0.9 Gallente, Minmatar, 0.7 Caldari) Azure/Rich

Omber: Pyerite+90 Isogen+75 (0.7 Gallente, Minmatar) Silvery/Golden

Kernite: Mexallon+60 Isogen+120 (0.7 Amarr, 0.4 Caldari, Minmatar) Luminous/Fiery

Jaspet: Mexallon+150 Nocxium+50 (0.4 Amarr, Gallente) Pure/Pristine
    
Hemorphite: Nocxium+240 Nocxium+50 (0.2 Amarr, Gallente) Vivid/Radiant

Hedbergite: Pyerite+450 Nocxium+120 (0.2 Amarr, Gallente) Vitric/Glazed

Gneiss: Pyerite+2000 Mexallon+1500 Isogen+800 (-0.4 Amarr, Minmatar) Iridescent/Prismatic

Dark Ochre: Mexallon+1360 Isogen+1200 Nocxium+320 (-0.2 Caldari, Gallente) Onyx/Obsidian

Crokite: Pyerite+800 Mexallon+2000 Nocxium+800 (-0.5 Amarr, Caldari, Gallente) Sharp/Crystalline

Bistot: Pyerite+3200 Mexallon+1200 Zydrine+160 (-0.6 All Space) Triclinic/Monoclinic

Arkonor: Pyerite+3200 Mexallon+1200 Megacyte+120 (-0.6 All Space) Crimson/Prime

Mercoxit: Morphite+140 (-0.8 All Space) Magma/Vitreous

Spodumain: Tritanium+48000 Isogen+1000 Nocxium+160 Zydrine+80 Megacyte+40 (-0.5 Amarr, Caldari) Bright/Gleaming

Bezdnacine: Tritanium+40000 Isogen+4800 Megacyte+128

Rakovene: Tritanium+40000 Isogen+4800 Megacyte+128

Talassonite: Tritanium+40000 Nocxium+960 Megacyte+32

1. # Implants
Furthermore, for pilots looking to get their reprocessing yield even higher, they may wish to look into the Zainou 'Beancounter' Reprocessing RX-series implants. These **Implants** are slot 8 Skill Hardwirings found in the market under Resource Processing Implants. They come in 3 varieties RX-801 (1%), RX-802 (2%) and RX-804 (4%) to provide an expensive but possibly worthwhile investment that will bring a pilot closer to a maximum effective efficiency in their station or POS of choice.

1. # Equipment tax
Stations charge a reprocessing fee, a percentage of the estimated value of reprocessed minerals.

Player-owned Upwell Structures can charge almost any rate for reprocessing, including 0%. If you go to the Structures browser in the Neocom menu, you can hover over the reprocessing icon and see the charge for player-owned Upwell Structures.

NPC corporations charge based on your standings with the corporation. It's a good idea to learn skill **Connections**, to increase your effective standing towards corporation. Even if your real standing with the corporation is close to zero, Connections V will cut your corporation tax by 25%. Note that until you complete at least one mission for the NPC corporation, your Connections skill will not be taken into account when calculating your tax rate.

Also notice that the Connections skill gives diminishing results. The higher your standings, the less benefit you get from it.

1. # References
