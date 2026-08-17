---
title: "Insurance"
url: "https://wiki.eveuniversity.org/Insurance"
pageid: 7951
source: "EVE University Wiki"
categories: ["Game mechanics", "Ships"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Insurance

EVE has a built-in **insurance** system for ships, which helps players hedge against the loss of *some* of the **ISK** invested in a ship. The game will provide a small insurance payout for any ship lost, not to **CONCORD**, and players can choose to spend some ISK in advance to recoup more money if their ship is lost. 

The insurance system is designed, in part, to be a financial safety net for newer players, and people new to the game should strongly consider insuring the Tech 1 ships that they will be using initially. Insurance has its limits, however: it does not provide payouts at the same rate for all hulls, and it covers just the hull, not the **modules** and **rigs** fitted to the ship and not any contents in the cargo hold and drone bay.

== Core mechanics == 
Insurance can only be taken out at a station or **player-owned structure** with relevant services. To insure a ship, either:
- Right-click its hull and select 'Insure' from the drop-down menu
- Open the insurance interface from the station services window, which defaults to the right-hand side of the screen when you are docked up

You can decide what level of insurance you would like to pay for. There are several options:

| Type of insurance
! scope="col" | % of repaid (CCP) value''' |
| :--- |
| No insurance |
| Basic |
| Standard |
| Bronze |
| Silver |
| Gold |
| Platinum |

The insurance interface will list the exact costs and payouts of the options for the hull you are insuring. Once you pay, the insurance stays valid for 12 weeks.

You receive a payout and an EVE-mail noting the payout immediately on the loss of the ship concerned.

  - A word of caution**: you are, in theory, meant to receive insurance expiration EVE-mails, but these may not be sent in a timely fashion. They are usually sent when you open up the insurance tab at a station, and you might therefore find out that you have missed the expiration date at an inconvenient time (i.e. when your ship is lost).

There are also several ways you may lose your insurance (reverting to the basic, default 40% reimbursement), if you:
- Repackage your ship
- Trade your ship to another player
- Sell your ship on the market
- Put your ship inside a contract
- Put your ship into a corporation hangar
- Are destroyed by CONCORD in **highsec** (an important financial factor in the calculations involved in **suicide ganking**).

1. # Reimbursement calculation
The formula for calculating the reimbursement fee is:

> <math> \text{reimbursement fee} = \text{CCP's estimated value of the ship} \times \text{percentage of insurance coverage} \times \text{ship type multiplier}</math>

The only value in the above formula known to players is the percentage of insurance coverage. The other two values are kept secret to reduce possible exploits. 

  - CCP**'s estimated value of the ship is based on the average values of materials used in the building of the hull. Inspecting insurance payouts for several different ships reveals that this value is lower than the average market value of the ship. This prevents insurance fraud.

For example, at the time of writing this article, the average market values for a couple of ships and 100% insurance payouts were:

| Ship | Approximate market value | 100 % insurance payout value |
| :--- | :--- | :--- |
| Rifter | 420.000 | 368.250 |
| Probe | 380.000 | 153.481 |
| Rupture | 9.500.000 | 7.120.000 |
| Retriever | 25.500.000 | 5.714.000 |

The maximum ship type multiplier value is 1. It is usually 1 for basic Tech 1 ships of the sort flown by new players and can be much less for more advanced ships.

The practical result of this modulation of the ship type multiplier is that new players flying T1 ships with basic modules fitted lose little if they are blown up, but players flying T1 ships with full T2 module fits, or T2 and T3 ships with T2 modules, have much less of a financial "cushion" to land on. One of the less obvious factors in the persistent combat viability of T1 ships, in a **New Eden** well populated with more advanced ship types, is that many T1 ships can be flown in riskier ways as they are highly insurable.

1. # Should you insure your ship?
New players should consider insuring every ship: a new player can lose a ship from a single ill-informed decision such as tangling accidentally with Triglavian NPCs, meeting diamond rats without knowing what they are, or simply using autopilot to move a ship carrying valuable cargo, but any ship available to a new player will insure well, protecting them from major setbacks.

More generally, if you expect your ship might well be lost within the next twelve weeks, you should probably insure your ship with platinum insurance. An obvious use-case for this is any ship that you have fitted for **PvP**, and which you are about to undock for a risky roam or battle, or which you expect to fly regularly while looking for fights in the coming weeks.

In other cases insuring your ship requires some thought. Let us analyze the example of **Rupture** insurance:

| Insurance type | Cost | Payout | Profit | # of extensions that ensure profit |
| :--- | :--- | :--- | :--- | :--- |
| uninsured (40%) | 0 | 2.848.093,20 | 2.848.093,20 | unlimited |
| basic (50%) | 356.011,65 | 3.560.116,50 | 3.204.104,85 | 9 |
| standard (60%) | 712.023,30 | 4.272.139,80 | 3.560.116,50 | 5 |
| bronze (70%) | 1.068.034,95 | 4.984.163,10 | 3.916.128,15 | 3,7 |
| silver (80%) | 1.424.046,60 | 5.696.186,40 | 4.272.139,80 | 3 |
| gold (90%) | 1.780.058,25 | 6.408.209,70 | 4.628.151,45 | 2,6 |
| platinum (100%) | 2.136.069,90 | 7.120.233,00 | 4.984.163,10 | 2,3 |

We can conclude that if you need to reinvest in Platinum insurance more than twice (that is if you do not lose your ship in more than 24 weeks), you will have lost money. It might be safer to invest in basic or standard insurance if you don't expect to take this Rupture into dangerous situations.

Once you progress in your **career**, you will probably own tens and then hundreds of ships. Insuring every one is probably not the best idea. For instance, ships that you intend to use in well-understood, controlled **PvE** contexts, which you know and have experienced before, might not need insurance. For some expensively-fit T2 or T3 ships, the insurance payout might be so desultory compared both to the financial loss when the ship blows up and, more cheerily, your income, that wasting time insuring them is a pointless hassle. Nevertheless, it will remain wise to take out Platinum insurance on cheap T1 ships which you are undocking for risky PvP.

1. # External links
- CCP support: [Insurance](https://support.eveonline.com/hc/en-us/articles/212726885-Insurance)
