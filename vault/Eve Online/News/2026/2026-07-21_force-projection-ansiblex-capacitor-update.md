# Force Projection: Ansiblex Capacitor Update

- **Date**: 2026-07-21T17:00:00.000Z
- **Category**: news
- **Author**: FC Okami
- **Source**: https://www.eveonline.com/news/view/force-projection-ansiblex-capacitor-update
- **Tags**: #future-updates, #nullsec, #news

## Overview
The latest information on the proposed changes to Ansiblex Jump Gates coming in the September Major Update.

---

*Game Design Director FC Okami is back with more details on force projection and the coming changes to Ansiblex Jump Bridges in the September Major Update.*

Hey folks, as mentioned in the [dev blog last Friday](https://www.eveonline.com/news/view/the-future-of-force-projection-with-fc-okami), here are the numbers and details of our design as it currently stands. I’m sharing them with you in the spirit of open discussion and understanding but also may change some of these as our implementation details come together and I receive additional feedback on the [official EVE Online forums](https://forums.eveonline.com/t/devblog-the-future-of-force-projection-feedback-thread/514961) and [Discord](https://discord.com/channels/940573867192221696/1527683412821934111).


## Capacitor


Under our current design the Ansiblex capacitor will be tuned as:


- Total Capacity: 1250 TJ
- Average recharge equivalent: ~200 TJ every 60 minutes
- Total recharge time from 0: ~6.25 hours
- The Ansiblex capacitor will use the same [non-linear recharge model](https://wiki.eveuniversity.org/Capacitor) as ship capacitor in EVE. Recharge is fastest around the middle of the capacitor and slower near empty and full.


The use of a capacitor opens up a wide range of potential play and counterplay design space for us in the future but at the time of release **the capacitor will not be impacted by remote cap transfers or neutralizers**.


## Cost


Cost of a jump is calculated by ship class and by the distance in light years (LY) of the end point from the capital system. The distance between Ansiblexes does not affect capacitor cost. These examples use values based on the Zones and Ship Costs tables below.


- **Example #1** - A capsuleer is in a Tengu in zone 2 and is jumping to an Ansiblex in zone 3. The capacitor cost to the Ansiblex at the point of origin would be 78TJ (Strategic Cruiser base cost of 13TJ x zone 3 multiplier of 6).
- **Example #2** - A capsuleer is in a Redeemer in zone 5 and is jumping to an Ansiblex in zone 4. The capacitor cost to the Ansiblex at the point of origin would be 162tJ (Black Ops base cost of 18TJ x zone 4 multiplier of 9).
- **Example #3** - A capsuleer is in an Epithal in zone 2 and is jumping to an Ansiblex in zone 1. Although tech 1 haulers have a base cost of 1TJ, because the multiplier for zone 1 is 0 no capacitor energy is consumed.



## Zones


We intentionally increased the cost as distance from the capital grows in order to place increasing logistical pressure on operating farther from your alliance's center of power.


| **Zone** | **Range from Capital System (LY)** | J**ump Cost Multiplier** |
| --- | --- | --- |
| Zone 1 | 0 - 5 | 0 |
| Zone 2 | 5.1 - 10 | 2 |
| Zone 3 | 10.1 - 15 | 6 |
| Zone 4 | 15.1 - 20 | 9 |
| Zone 5 | 20.1 and onward | 15 |



## Ship Costs


These costs represent the amount of terajoules consumed by the Ansiblex capacitor upon jump based on ship type.

Values in Zone 1 are the baseline from which the following zone costs are calculated. Jumping to Ansiblexes within Zone 1 remains completely free to all ships eligible to use them; the Zone 1 costs for ships shown the table below are simply there to afford us the ability to tune this base cost in the future.


| **Ship Class** | **Capacitor Cost (Base)** | **Capacitor Cost Zone 2** | **Capacitor Cost Zone 3** | **Capacitor Cost Zone 4** | **Capacitor Cost Zone 5** |
| --- | --- | --- | --- | --- | --- |
| Capsule | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Exhumer | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Expedition Frigate | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Freighter | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Hauler | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Jump Freighter | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Mining Barge | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Prototype Exploration Ship | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Shuttle | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Special Edition Yachts | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Corvette | 1.00 | 2.00 | 6.00 | 9.00 | 15.00 |
| Frigate | 4.00 | 8.00 | 24.00 | 36.00 | 60.00 |
| Covert Ops | 5.00 | 10.00 | 30.00 | 45.00 | 75.00 |
| Destroyer | 6.00 | 12.00 | 36.00 | 54.00 | 90.00 |
| Assault Frigate | 7.00 | 14.00 | 42.00 | 63.00 | 105.00 |
| Blockade Runner | 7.00 | 14.00 | 42.00 | 63.00 | 105.00 |
| Deep Space Transport | 7.00 | 14.00 | 42.00 | 63.00 | 105.00 |
| Interceptor | 8.00 | 16.00 | 48.00 | 72.00 | 120.00 |
| Interdictor | 8.50 | 17.00 | 51.00 | 76.50 | 127.50 |
| Command Destroyer | 9.00 | 18.00 | 54.00 | 81.00 | 135.00 |
| Electronic Attack Ship | 9.00 | 18.00 | 54.00 | 81.00 | 135.00 |
| Logistics Frigate | 9.00 | 18.00 | 54.00 | 81.00 | 135.00 |
| Tactical Destroyer | 9.00 | 18.00 | 54.00 | 81.00 | 135.00 |
| Industrial Command Ship | 10.00 | 20.00 | 60.00 | 90.00 | 150.00 |
| Cruiser | 10.00 | 20.00 | 60.00 | 90.00 | 150.00 |
| Heavy Interdiction Cruiser | 10.50 | 21.00 | 63.00 | 94.50 | 157.50 |
| Stealth Bomber | 11.00 | 22.00 | 66.00 | 99.00 | 165.00 |
| Force Recon Ship | 11.50 | 23.00 | 69.00 | 103.50 | 172.50 |
| Heavy Assault Cruiser | 11.50 | 23.00 | 69.00 | 103.50 | 172.50 |
| Combat Recon Ship | 11.50 | 23.00 | 69.00 | 103.50 | 172.50 |
| Flag Cruiser | 12.00 | 24.00 | 72.00 | 108.00 | 180.00 |
| Logistics | 12.50 | 25.00 | 75.00 | 112.50 | 187.50 |
| Strategic Cruiser | 13.00 | 26.00 | 78.00 | 117.00 | 195.00 |
| Attack Battlecruiser | 14.00 | 28.00 | 84.00 | 126.00 | 210.00 |
| Combat Battlecruiser | 14.50 | 29.00 | 87.00 | 130.50 | 217.50 |
| Expedition Command Ship | 15.00 | 30.00 | 90.00 | 135.00 | 225.00 |
| Command Ship | 16.50 | 33.00 | 99.00 | 148.50 | 247.50 |
| Battleship | 16.50 | 33.00 | 99.00 | 148.50 | 247.50 |
| Black Ops | 18.00 | 36.00 | 108.00 | 162.00 | 270.00 |
| Marauder | 19.00 | 38.00 | 114.00 | 171.00 | 285.00 |
| Rorqual* | 19.00 | 57.00 | 104.50 | 171.00 | 285.00 |



## Sov Capital Change Cooldown



- Cooldown to change an alliance capital system will be increased to 90 days to encourage strategic commitment and prevent capital swapping.


As a final reminder, this design is only impacting Ansiblex gates and other means of transport such as stargates, jump portals and filaments will be unaffected and allow folks to travel as normal.

o7 and see you in space,

FC Okami
