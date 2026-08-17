---
title: "Horde-Complex Reactions"
url: "https://wiki.eveuniversity.org/Horde-Complex_Reactions"
pageid: 24295
source: "EVE University Wiki"
categories: ["Guides"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Horde-Complex Reactions

This guide was created by KenGeorge Beck on 2018/05/05.  I BELIEVE it is still up to date as of 2024, thanks to a patch.

tl;dr: Check out the Reactions Spreadsheet https://docs.google.com/spreadsheets/d/1QOhyKNNNwUot_0Yh_9ulpb64InpXAXHjMOaeNgwvElY/copy?usp=sharing, which walks you through getting involved with reactions! Any questions? Just ask here.

Spreadsheet:

Composite Reactions v2.3.4 https://docs.google.com/spreadsheets/d/1QOhyKNNNwUot_0Yh_9ulpb64InpXAXHjMOaeNgwvElY/copy?usp=sharing

@Dr Pfizer brought the new composite reactions into the Composite Reaction spreadsheet. Thank you for your work!

Composite Reactions Tracker:

Composite Reaction Tracker v0.6 https://docs.google.com/spreadsheets/d/1vU4rgWFGAIUVR-H6mog4KXJqMqRK2VJEmvsYW3eTbZs/copy?usp=sharing

- @Makr Alland has created a spreadsheet that can be used for tracking purchases and locking in prices for the reactions you're currently running. Thanks to the efforts of @Dr Pfizer, this sheet has been updated to fix issues with ESI.*<blockquote>Editors note: There was a change to the Cost Index and taxes:

yes - but the change is very simple to do yourself as well:

in the "Configuration: Reaction Systems" tab, in Cell C2 change the formula to this:

Code:

=ARRAYFORMULA(IF(A2:A<>"",D2:D+0.04+G2:G,""))

and set the correct tax values for the system(s) you are using in column G.

edit: updated the SCC surcharge to 1.5% from 0.75%

edit2: updated the SCC surcharge from 1.5% to 4% as of Patch 21.06 on 2024-02-01</blockquote>

  1. # Summary
Up until October 24th with the Lifeblood release, reactions have always been this highly-technical venture that required a fair amount of know-how and lots of clicking, as well as quite a bit of up-front capital.

With Lifeblood, however, reactions have been moved into the Industry interface of new Refinery structures. You can read about them a little bit in Eve's Dev Blog https://community.eveonline.com/news/dev-blogs/reactions-redefined-new-industry-opportunities-for-you/. This also means that many more people can get involved, with the only prerequisites being a bit of skill training and some startup capital.

  1. ## Skills
There are four new skills that affect reactions. These are:

- Mass Reactions / Advanced Mass Reactions: Each level increases the number of reaction slots your character has by 1 per level, up to a max of 11 reactions total
- Reactions: Reduces the amount of time it takes for reactions to run by 4% per level, providing a 20% reduction in time at level 5.
- Remote Reactions: Lets you start and deliver reaction jobs remotely, which helps if your reaction characters move around a lot (for instance, as cyno alts)

  1. ## Skill Plan

# Reactions IV
# Mass Reactions V
# Advanced Mass Reactions IV
# Remote Reactions III (optional, best if you're not going to be in the reaction system all the time)
# Reactions V

- This will take you between about 19 days with optimal remap and +3 implants and 31 days with an off-map and no implants. If you're tight on time, you can skip Reactions V, though I highly recommend training it as the goal with reactions is to squeeze as many into a set timeframe as you can.*

  1. ## Refineries
All reactions must take place in refineries. These are Athanors and Tataras, with Athanors being the medium structures (equivalent to Astrahuses and Raitarus) and Tataras being the large structures (like Fortizars and Azbels). These are anchored throughout Horde space, currently in the following systems:

- RQOO-U (T2 Tatara)
- R1O-GN (T2 Tatara)
- GQ-7SP (T2 Athanor)

  1. ## Reaction Steps:
In my spreadsheet, I've outlined four steps for getting started with reactions. These are as follows:

  1. ### Step 1: Configuration
Before getting started with the sheet, first make a copy of it by going to File > Make a copy... When this is done, navigate to the Step 1: Configuration tab and configure settings appropriate for your installations. The default settings are generally reasonable, with the following exceptions:

- Total Reaction Slots: Be sure to set this to the total number of slots you have available across all your toons. This is determined by the Mass Reactions and Advanced Mass Reactions skills.
- Build System: Set this to the system you're reacting in (most likely RQOO-U or R1O-GN). If your build system is not in the list, navigate to the Configuration: Reaction Systems tab and add it!
- Days Per Cycle: Determine how often you would like to sell the Complex Reaction. Shorter is typically better, with the default of 7 days being fairly sufficient. Shorter cycles let you respond to market trends more rapidly, longer allow you to be lazier with the process.
- Buy or Sell: Determine if you will be using buy orders or sell orders for both your inputs and outputs
- Shipping: Determine if you will be shipping your inputs, outputs and fuels

Review the other settings under configuration as well, along with their descriptions, and post here with any questions.

  1. ### Step 2: Pick Reactions
After configuring the sheet, navigate to the Step 2: Pick Reactions tab and review the reactions available. These are all Complex Reactions, as they're the most straightforward and most-used reactions. There are also boosters and T3 reactions, but those are not handled at this time:

The big takeaways with the above chart are the Profit % line an the Investment lines. Recurring Investment is what you should expect to pay for each cycle, and Profit % is the expected percentage of profit for your reactions. Recurring Profit, of course, is what you're expected to make after selling all your Complex Reactions.

With this sheet, what you want to do is enter the number of instances of a reaction you want to perform in the right-most column. When you do, the section further to the right will update to reflect how many more slots you have available:

You can see a running total of how much it'll cost you to set up, as well as what your expected profit is. You will be told if you don't have sufficient slots to complete your reactions, at which point you should update your selection.

  1. ### Step 3: Shopping!
After picking your reactions, navigate to the Shopping tab to review what you need to purchase. The left-most column shows you what you will have to purchase for the reactions you've selected and the right column lists off all the Reaction Formulas you need to buy to run the reactions. The reaction formulas are infinite-use, so are a one-time purchase after you have them.

IMPORTANT: It is recommended that you buy 2x the Materials when you first start reactions, so that you can run through the Build-Up Phase and then continue onto the Full-Chain Phase without needing to purchase more.

To the right of the One-Time Purchases is a summary of all the predicted costs and overall volume for shipping:

Step 4: React

After you've acquired all your inputs, the next step is to do your actual reactions. There are two phases for reacting. The first phase builds up all the intermediate inputs for your complex reaction, and lasts one full cycle:

After that, you'll enter your normal recurring cycle (the Full-Chain Phase), which includes the Complex Reactions you'll be selling:

I tend to recommend purchasing all the inputs for your next cycle a day or so before your current cycle ends, so you have enough time to account for shipping inputs in. However, if there is a bit of a delay (even a couple days into your next cycle), that should be fine as your initial build-up cycle covers you for a while. Here's a screenshot of the rough process outline:

There are additional appendices in the spreadsheet showing a breakdown of the complex and simple reactions, as well as displaying a list of all Complex Reactions by their moon goo inputs, and moon goo's by their complex reaction outputs.

I will be updating this as I get feedback, and attempt to keep the latest versions in this thread. Please message here or on Discord if you have any questions!
