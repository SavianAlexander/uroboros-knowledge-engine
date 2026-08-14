# Improvements and Bug Fixes

- **Date**: 2003-12-17T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/improvements-and-bug-fixes-34
- **Tags**: #patch-notes

## Overview
Bug Fixes and Improvements Manufacturing: Tech Level 2 (TL2) Tech Level 2 (TL2) introduces new possibilities into the world of EVE for manufacturing and researching. Various new TL2 blueprints will be available for manufacturing TL2 items. TL2 items are generally more complex items than TL1

---

**Bug Fixes and Improvements**

**Manufacturing:**


- Tech Level 2 (TL2) Tech Level 2 (TL2) introduces new possibilities into the world of EVE for manufacturing and researching. Various new TL2 blueprints will be available for manufacturing TL2 items. TL2 items are generally more complex items than TL1 items, and as such contain different ingredients than just minerals. The blueprints will be introduced via Research Agents. TL2 blueprints may also have extra requirements for when you are trying to manufacture, copy, or research them. The requirements can be looked up by using the Info window. You may discover that in order to manufacture using a TL2 blueprint you require extra skills or tools. Tools are items that may needed to complete a manufacturing or research activity. You may find that tools get damaged when they are used in a research or manufacturing job, and subsequently need repairing from time to time. When manufacturing a TL2 item you will probably find that you need other items to manufacture it besides the items that it is composed of. Due to this you may notice that when you recycle a TL2 item that the results differ from the manufacturing requirements.
- Minerals needed to build standard Afterburners and MicroWarpdirves has been decreased, it will be cheaper to build them than before.


**Missions/Agents:**


- The agent system is now standing based. This means players will generally find it a lot easier to aquire agents than before. To be able to receive missions and use agent services for agents, you will need to have the appropriate standing towards that agent, his corporation or his faction. For example, if you have 0 in standing towards Lai Dai corporation, then you will be able to access all level 1 agents of a certain quality and below belonging to the Lai Dai corporation. Once you have raised your standing by an X amount, then you will be able to access a higher quality level 1 agent, until finally you will be able to access a level 2 agent. We believe this is a much better and more flexible agent system, which allows players to build up a network of high level agents much more quickly than before.
- All players standings have been halved over the board. However, if you had access to a level 3 or 2 agent in the old system, then you will automatically receive enough personal standing to him to be able to retain this agents services. If you don't remember what agent(s) this was, then check your standings table in your Character Sheet, you will see what agents you have a good standing towards there.
- A player standing towards an agent, faction or corporation will slowly decay, if nothing is done to maintain it. The best way to maintain your standing is by doing missions. Research jobs do not benefit your standing, nor does declining or quitting them penalize your standing.
- The Jovian Empire and Concord factions have closed the services of their agents, for now. The people who finished loads of missions for either of these factions will receive adequate standing with another agent of a faction that is open. High personal standing allows the player to use them despite a low corp/faction standing. To find them, check your standings table in the character sheet.
- All missions are now declinable and quittable.
- Ignoring the missions your agent offers you will now result in a standing loss, as will declining or quitting them.
- Research agents have been implemented. The only way to aquire Tech Level 2 original blueprints is through these agents (or other players who have received them through these agents). The research agents are basically there to help the player research a technology and eventually discover a blueprint. Blueprint discoveries are a fairly rare and random event, but players with a high amount of research points are much more likely to make a discovery. Research points are gradually acquired while the research process has been activated by the players agent. Skills (skill of the player), standings (player standing towards his agent or agents corporation/faction) and level + quality of the agent affect the rate at which the player receives research points. Research can also not be started unless the player has the required skills. Players with advanced scientific skills will obviously have a big advantage, as they should.
- While doing your research, your agent may occasionally ask you for help, for various reasons. When the agent is in this sort of state, the player will still be eligible for making a discovery, but he will no longer receive research points, until you have either declined to help your agent or completed the mission. Completing the mission greatly increases the yield of research points for that day, but is not necessary to continue the research.
- The so called "blueprint" missions no longer give out original (master) blueprints. To recieve originals you will need to use the research service which the agents in the research (R&D) divisions have.
- Offered missions must be accepted or they will be viewed as having been declined.
- The agent mining missions have been tweaked so that they no longer give out absurd amounts of money for a small amount of minerals, i.e. their difficulty has been upped. The higher the quality of the agent + the players standing towards him and his corporation + the players skill will raise the payment for these missions to make them more lucrative. At the same time, mining missions are more rare for non-mining corporation related agents.
- Agents are now slightly more jovial to the player on average when he is doing missions for them if his standing is high.
- Agent NPC kill missions are now usually dished out only by agents in military type of corporations, especially the hard ones. Players who wish to avoid the mundane courier or mining missions are encouraged to build up a network of agents in military corporations to satisfy their barbaric desire for combat. Please do not confuse "corporation type" with the division the agent is in.
- A few scenario missions are in which use a new feature which spawns the item that your agent wants you to retrieve in the cargo container out in space once you open it. This is to prevent incessant camping of mission scenarios which prevent players from completing their scenario mission. The player is not allowed to buy these items off the market to finish the mission. This does not mean that all scenario missions use this feature, but most will.
- Courier and kill missions which required the player to retrieve or deliver certain data sheets or reports now have a specific ItemID on the item in question. This means that if your agent wants you to bring him certain data sheets, you cannot simply buy any old data sheets off the market and return them to him.
- Most agent missions now have a standard time bonus reward, which is in the form of money, commodities or tech level 2 tools/skill packs/ingredients.
- Agent root texts have been modified a bit, so that they are no longer generic over the board, and are now standing based as well.
- Agent kill mission difficulty has been raised for level 2 and 3 agents. Level 3 though in particular. Mission npcs drop better loot on average though as well.
- Most trade missions changed to courier. Most non-combat oriented missions are now configured purely for the agents in non-combat oriented corporations.
- Lots of new pirate and faction based missions added into the mission database.
- The agent messages have been tweaked a bit. They should be less rude now, and friendlier as you aquire higher standing towards them or their faction/corporation.


**Market:**


- The market will now always purchase at the selected location when you right-click->buy on the table or map view of the market, instead of sometimes at a nearer location or lower price.
- Order prices now have an accuracy to a hundredth of an ISK
- NPC orders now have a maximum volume that they will show and process. They will also now change slightly on each transaction, to reflect the percentage of the desired supply or demand.
- Equivalent orders are now handled in a strictly 'first-in, first-out' manner
- For a given match, the price of the newer order is chosen. For example, if an item is for sale at 10 ISK and someone enters a buy order at 20 ISK, the order will be matched at 20 ISK
- Lack of funds when matching an order will result in a 10% fine
- Players with unpaid fines will not have buy access to the market
- Price of NPC orders vary continuously as a function of availability
- NPCs put in their orders in chunks
- Many of these (Market) changes will dramatically change the bidding strategies that player need to use, we have thus decided to cancel all outstanding bids during the patch. Also note, that with these changes many popular methods, sometimes known as 'market griefing', become impossible.


**Navigation:**


- Mining drones are now faster to load and faster to render.
- Mass has been tuned for all ships in order to fit the changes to Afterburners and MicroWarpdrives, cruisers and battleships now have more mass and frigates and industrials are lighter, this will how ever not affect the agility of the ships, most ships will even act more agile than before.
- If you successfully warp scramble someone who is in the warp alignment stage, their warp will be cancelled.
- The restriction that prevents ships from docking or jumping if they have been involved in recent aggression now no longer applies if the ship is a capsule.
- Ship emerging from warp now stop
- You now become invisible before jumping through gates and emerge at the other gate invisible. You become visible either by navigating or waiting a few moments.
- You are invisible after reconnecting having been disconnected for a while. You become visible either by navigating or waiting a few moments.
- Stargate jumps are now gate-to-gate so that you now emerge beside the gate to the system you are coming from.
- Stargates now light up at both ends when they are used, so you see when someone has jumped into a system you are in, despite them being invisible
- Autopilot can be set to avoid systems where someone has recently been podded in.
- Autopilot now avoids < 0.5 space better when you select "safe route".
- Autopilot tries to stay in 0.0 space and avoids > 0.4 space at all costs when you choose "less safe route".


**NPC´s:**


- Amarr Military and Police fleets have been removed from the Sanctum constellation, including the solar system Yulai. This area is controlled by CONCORD military and police officials.
- Bounty price handed out by CONCORD for killing NPC pirates has been increased for most pirates, mostly the low level pirates.
- Bigger pirates have entered game play, there will now be cruiser pirates wandering in Empire Space in 0.0 - 0.4 security systems and battleship pirates will now been seen in deep space. Battleships pirates are much stronger than average battleships of players, we warn all players wanting to take them out by themselves.
- Station and stargate sentry guns are now invulnerable to damage. They will still respond in the same way to direct damage done to them, but splash damage to them will be ignored for the purposes of aggression considerations.
- Entities now have the ability to use afterburners/MWDs if they are configured to do so.
- If a stargate or station could not be matched to a race whose sentry guns it should deploy, it would possibly deploy none. In this case, all the types of sentry guns are made available to it to chose from.
- Fixed sentry gun response so that they only attack people that get a loss in faction standing from the faction that owns the solarsystem if that faction is one of a selected range - as it was, it was leading to situations where a player might kill a pirate entity who belonged to an NPC corp which was in the faction that owned the system and the result was that the player would be attacked by the concord sentry guns they were beside.
- The description for a few NPC security vessels had information on the ship they were flying, this has been fixed.
- Targeting speed of NPC cruiser pirates has been made longer to reflect to the player ship level.
- Faction police now always attack people who enter their solarsystems with less than -5.0 faction standing, before the faction standings they attacked at varied based on security level.


**Ship Management:**


- Armor Repairer has been moved from medium slot to low slot. It will stay fitted in medium slots on ship and players will be able to activate them, but once it gets unfitted it can only be fitted into low slot after that.
- ECCM Projector I has been increased in duration and in the scan strength it gives to targets.
- All Industrial ships now have special ability: "5% bonus to cargo capacity and max velocity".
- Apocalypse special ability "5% increase in Capacitor Recharge rate" has been changed into "5% bonus to Capacitor Capacity", this bonus will both enhance the Capacitor and also the Capacitor Recharge rate since the time it takes to recharge does not get altered with increased Capacitor Capacity.
- Industrials have been increased in power output so that they can be fitted with cruiser sized afterburners and microwarpdrives.
- Apocalypse, Armageddon and Megathron have been boosted in capacitor recharge rate.
- Industrials ships: Badger Mark II and Mammoth have gotten an extra low slot open for players to fit into.
- All Industrials have been increased in cargo capacity to compensate for the changes to Afterburners and MicroWarpdrives.
- Afterburners and MicroWarpdrives have partially been size and ship classed, they will now take mass of the ship into count when giving speed boost to favor lighter ships more than slots. Blueprints for the new modules have been added to the market.
- Speed changes for cruisers: Moa has been increased in speed to 160, Caracal has been decreased in speed to 165, Blackbird has been decreased in speed to 160.
- Warp Core Stabilizer I has been moved to low slot and is now passive as well (activation not needed). Players will have to unfit the module from their medium slot at a station and fit it to low slot so that it works for them again.
- Targeting Speed has been removed as a single attribute, ships now have Scan Resolution that calculates targeting time with Signature Radius of object being targeted. A progression bar has also been added for players to see the targeting time.
- Scorpion was reduced in base speed from 125 to 115, it's mass was also increased a little bit. Scorpion will act a little bit slower and less agile than before.
- The Blackbird cruiser had incorrect mass value and has been corrected, it was much too agile compaired to the design of the cruiser class and the ship itself.
- Capacitor Booster charges got a little update, Cap Booster Charge 300 was changed into 400 and Cap Booster Charge 400 was changed into 800. Cap Booster charges also had some volume changes so players will be able to carry bit more of the bigger charges with them.
- Large sized hybrid weapons had incorrect capacity for hybrid ammo, the 425mm railgun can now be fitted with less and the ion blaster cannon can now be fitted with more ammo.
- Large sized projectile ammo and hybrid ammo has been decreased in volume and the large turrets in capacity, players will only be able to carry more projectile ammo and hybrid ammo in their cargo hold.
- The Merlin Frigate had incorrect bonus description, it said it should give 5% to hybrid turret damage but does give 5% max shield, description has been changed.
- If the capacity of a charged measure (capacitor or shield charge) is lowered and the amount of charge present is greater than the new capacity, now the charge is immediately lowered to that level rather than remaining the same and discharging over time to the new level.


**Combat:**


- missile bracket disappears immediately upon impact.
- Improved performance in big missile battles.
- Defenders flight path looks slightly more beautiful, and they use the correct explosion.
- No more missile to missile collisions (except for defender missiles)
- Area range of splash damage for missiles has been decreased.
- Projectile AutoCannons have been increased in damage multiplier and in fall off range.
- Hitpoints for missiles has been lowered for smartbombs being able to take them out. Small smartbombs will now be able to take out all missile types but torpedoes. Damage of defender missiles has been tuned with these changes.
- A players combat drones should no longer attack him when he launches a mine.
- Missile Launchers decreased in speed: M-12 Standard Launcher now has 14 seconds base speed and H-50 Heavy Launcher & S-110 Siege Launcher have 20 seconds base speed.
- Combat drone lag is now really fixed.
- You can now cloak if you are targeting others as those targets are automatically dropped rather than the cloak itself failing with an error.
- Low end projectile ammo and hybrid ammo now have bigger range bonus to be in synch with crystals; Carbonized Lead, Nuclear, Photon - Iron, Tungsten, Iridium have all had slight boost in range bonus.
- Crystals were out of synch with projectile and hybrid ammo in range penalty on the high end crystals, Ultraviolet, Xray, Gamma and Multifrequency now have bigger range penalty.
- Many crystals were out of synch with the other turret charges types in damage, Infrared, Microwave, Radio and Multifrequency crystals were slightly downgraded in damage.
- Hybrid Railgun turrets have been increased in damage but slowed instead, they do not do much more damage over time, instead they will get heavier shots but shoot slower.
- Optimal Range, Fall Off and Tracking Speed for all Hybrid Blaster turrets has been increased.
- Capsules no longer self-destruct immediately. There is a now a 2 minute delay before the capsule explodes. Bystanders now get informed about ship/capsule self-destruction so that there is no confusion about why ships in combat that self-destruct explode.
- Added more detail to the emails CONCORD sends out when your ship is destroyed, now it includes who laid the final blow, what type of ship they were in, what weapon they used, their corporation and their security status. Also what system it happened in and the security level of that system.
- Missiles can't push ships around so much anymore.


**Other:**


- Unfitting a module into your cargo hold or fitting a module from your cargo hold will now result in a correctly updated cargo capacity in the UI window.
- Notification text for when ship does not have enough turret or launchers slots left has been changed to a better description.
- Cargo containers now show their anchored state in a green-yellow-red fashion. Green is unanchored, yellow is anchoring or unanchoring and red is anchored.
- Can no longer jettison things that give the option to be launched.
- The security status displayed in the character selection screen and the character sheet is now truncated rather than rounded to give a more accurate number.
- Enforced anchoring distance. Can no longer anchor objects on top of other objects.


**Skills:**


- New specialized ore refining skills have been added to the market, they will lessen the waste factor when refining specific ores.
- Smart bombs are now also affected by the weapon upgrades skill.
- The scout drone skill now gives range bonus per level for drone usage as it should have been doing, the bonus is set to 5000 meters per scout drone level.
- The Caldari Battleship skill said under attributes that it gives 5% shield recharge rate per skill level. No ship command skills are supposed to give bonuses by themselves, the description has been edited.
- The skill Weapon Upgrades now affects CPU usage for missile launchers.


**Game sounds:**


- There is now an environment sound when you are cloaked ( invisible ).


**World map:**


- Single factions can now be highlighted when Map is set to display stars by sovereignty.
