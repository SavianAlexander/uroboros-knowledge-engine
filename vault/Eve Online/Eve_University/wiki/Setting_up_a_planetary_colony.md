---
title: "Setting up a planetary colony"
url: "https://wiki.eveuniversity.org/Setting_up_a_planetary_colony"
pageid: 1673
source: "EVE University Wiki"
categories: ["Guides", "Industry", "Planetary Industry"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Setting up a planetary colony

The purpose of **Planetary Industry** is to produce goods from resources that have been extracted from planets. These goods are used in production and can be sold on the market.

To create a colony on a planet, a Planetary Command Center matching that planet's type is needed. These are sold by NPC merchants. To deploy it from the cargo hold of a ship, it has to be in the desired system. Almost all further actions can be done from anywhere in the universe. Only import and export of produced goods must be done from space in the same system as your colony. Picking up exported items must also be done from space near either the Customs Office or a launched canister from the Command Center, depending on how the products have been exported.

A Command Center provides Powergrid and CPU to the entire colony. This limits how many buildings can be put in a colony. Everything takes an amount of CPU and Powergrid, including the transportation links between the buildings.

To build a manufacturing-only colony, **processors** are needed and a way of getting wares from and to the planetary surface. The colony can be placed in a small area, anywhere on your chosen planet. The location does not matter.

To build a resource-extraction colony, resource extractors are needed and a way to get things up from the planetary surface. Processors are optional.

Storage is needed to compensate for varying extraction volumes over time or to store your output for later pickup. Some buildings can be used to store goods. In order of capacity: Planetary Command Center (500 m³), Launch Pad (10,000 m³), or Storage Facility (12,000 m³).

Adjustments to the setup might have to be done over time depending on ever-shifting resource locations. Deeper production chains on one or multiple planets might cause adjustments in the setup. More information is available on the **Colony Management** page.

1. # Your First Colony

- This pictorial guide will show you step-by-step how to set up a basic colony for producing P1 products from locally extracted R0 raw materials.*
We will be going over: 
# The basic setup of a Command Center (CC), an Extractor Control Unit (ECU) and extractor heads, a Launchpad, a Basic Industry Facility (BIF), and links. 
# Routing inputs and outputs to minimize resource loss.
# Exporting via a Launchpad and a Customs Office.
# Exporting via the Command Center.

There are also video guides over at the main **Planetary Industry** page for your perusal.

For more details on structures, see **Planetary Buildings**.

{{ important note box | **WARNING:** The setup shown in this guide requires that you have at **bare minimum**  trained to Level II and  to Level I. Train these skills before attempting to mimic this setup. Training  and  is also recommended for best results when scanning.}}

| left|300px|There are two ways of entering Planet Mode]] | Buy a "XXX Command Center" on the market.  (We are going to a Temperate Planet, so I bought a Temperate Command Center). NPCs sell them for only 81,000 ISK, so they're pretty cheap, even for a new player (until you upgrade them, of course). Fly to the system with the Command Center in your cargo (you need at least 1000m3), and sit in space, preferably cloaked if you are (like myself in this example) in low sec or 0.0. Since The Syndicate, the system's owner, is an NPC corp, there is no player sovereignty blocking my deployment.
Select the planet in the Overview and select View Planetry Industry from either the Selected Item box or via the right-click contextual menu.

  - Scan for Resources**. The **Planets** and **Planetary Commodities** pages are good resources for figuring out what you need to look for to produce what you want. |
| :--- | :--- |
| left|300px]] | Go to the Build Menu and select Command Centers (which we’ll call CCs from now on). Click on “Temperate Command Center” and place it near to where you want to extract resources. In order to build more structures, you’ll need to click “Submit” at the top left. Once you do this, you cannot move your CC or reclaim it. |
| left|300px]] | Time to start extracting! Select Extractor Control Units (a.k.a. ECUs) and select the only option (Temperate ECU) to place it. There will be a transparent circle surrounding the ECU that is not visible in the image to the right because of how far we’re zoomed in. That circle dictates where our ECU can place its extractor heads, which we’ll get to in a moment. Make sure any resource hotspots you want to extract from are within that circle! Then click “Submit" and accept the 45,000 ISK fee to build the ECU. |
| left|300px]] | Once you’ve submitted the changes to place the ECU, you can start surveying for deposits and placing extractor heads. Click the ECU and then click the leftmost button labeled “Install Extraction Program” in the pop-up window. A new window will appear allowing you to install up to 10 extractor heads, adjust the duration of the extraction program, and see a graph showing how many resources each cycle will pull up as well as the grand total. |
| left|300px]] | In order to place all 10 heads, we’re going to need to upgrade our CC so it provides more Powergrid and CPU. Click on the CC and select the leftmost button labeled “Upgrade,” then select the next upgrade level and click “Upgrade.” You actually won’t be charged any ISK until you next click the “Submit” button, so don’t be too worried if you discover later that you have a lot of excess Powergrid and CPU. However, the only way to cancel an upgrade is to click the “Cancel” button next to the “Submit” button which will undo ‘''ALL’'’ the edits you’ve made since you last “saved,” so it’s recommended to only upgrade one level at a time. |
| left|300px]] | Okay, we’ve upgraded our CC and installed and placed all our heads! But what if I don’t want to run a program for just one hour? Let’s set the program to a full day... |
| left|300px]] | Oops! Our extractor heads are now causing interference with each other because the longer program caused their extraction areas to increase and overlap! If we run the program now we’ll lose some materials as indicated by the red percentages in the Survey Window. We can either spread out our heads or reduce the program duration. Since I’m just making a tutorial, I reset the duration to one hour. Note also how the extraction per cycle has dropped. With a one-hour program the first cycle pulled up 30,000 units. With a 24-hour program the first cycle only pulls up roughly 20,000 units. |
| left|300px]] | When we’re done fiddling with our extractor heads, we can start the program by clicking the “Install Program” button and then “Submit.” But now we need to store our extracted materials! Since we’re going to eventually be moving our finished products off-planet, let’s use a Launchpad as our storage unit. Place one using the Build Menu near the ECU. Now we need to link the two buildings.  -  the ECU, then release  and click the Launchpad. You can do this the other way round, too, or use the Links Menu on either building’s pop-up window. You’ve now set up a link over which products can be routed, at the cost of some CPU and Powergrid based on the link’s length, which is why we tried to minimize the distance between buildings. |
| left|300px]] | Now we need to tell our buildings to actually move stuff across this new link. Click the Products button on the ECUs pop-up, or double-click the structure itself. As you see, Microorganisms are currently not routed. We can fix this by clicking on them, clicking “Create Route,” and then clicking our Launchpad, and clicking “Create Route” again. Now all our Microorganisms will be automatically sent there for storage. |
|  |  |
| left|300px]] | You’ll then be taken to the BIF’s Products menu, where it will prompt you to route the Bacteria to a storage facility. Click “Create Route," select the Launchpad, and click “Create Route” again. |
| left|300px]] | 300px]] |
| left|300px]] | As you can see, I set up three BIFs to keep my Launchpad from filling up with Microorganisms. You can check up on your BIFs by clicking on them to view the remaining time on their current order and how much of the necessary inputs they have ready for the next order. Industry Facilities can only hold one run’s worth of inputs themselves to “prep” for the next run. Anything in excess of this will be thrown away, which is why we went through the extra step of routing the Microorganisms to a storage facility first. |
| left|300px]] | left|300px]] |
| left|300px]] | left|300px]] |
| left|300px]] | left|300px]] |
| left|300px]] | left|300px]] |
| left|300px]] | left|300px]] |

- Check out the Competition: While we were waiting, we could have checked out who else is on the planet. Sometimes you just see an extractor here or there, sometimes you see the Command Center.  If you click on the Command Center you can see all the nodes in their network.  Right-click on the background to hide or show other players colonies.  Mostly you can just ignore them, except when they are sitting on top of the juicy deposit that is rightfully yours. If you both drink from the same deposit each gets less, just as if you place your own extractor heads too close to each other.  The below images are taken from the original guide on this page. For more details.
<gallery>
File:PI_YFC-28-Competition.png
File:PI_YFC-29a-InfoOnCompetition.png
File:PI_YFC-29b-Competition_PINs.png
File:PI_YFC-29b-CompetitionNetwork.png
</gallery>
 
- If you're done with this planet, you can tear down your whole colony by deleting the Command Center. You will lose the investment you made in the old Command Center, and all the buildings you built, however, so it's probably best to wait until the colony has paid for itself in products.
