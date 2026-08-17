---
title: "EVEMon"
url: "https://wiki.eveuniversity.org/EVEMon"
pageid: 2284
source: "EVE University Wiki"
categories: ["Applications", "Candidates for verification"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# EVEMon

In EVE Online, your skills determine what you can fly and do. EVEMon is a third-party standalone application designed to keep track of your character skill progression. It allows you to view current skills and attributes, what you are presently training, your characters' ISK balance, and can track all your characters across multiple accounts. The most commonly cited feature of EVEMon is its skill planning, allowing a user to set up detailed skill plans for long-term progression, letting them gauge the most optimal neural remaps and training times. In this way, you can optimally prepare your character's skills to those of a daring explorer, Marauder pilot, electronic warfare aficionado, mining foreman, and more. There is an excellent skill library with prerequisite trees that shows how many other things would need to be trained before a skill such as  is trainable.  EVEMon also has some other gadgets attached to monitor market orders, manufacturing, research, and clones.

EVEMon is an open source tool (GPL V2).  The software is primarily developed for Windows, but it will work on Linux using Wine, and may work on Macs using Darwine. To use the software, EVEMon needs to be granted EVE ESI authentication, allowing it to correctly monitor skills.

This guide is written with the new player in mind since it is often one of the first **third-party tools** they start using.  More advanced players may find useful information here along with the simpler details.

1. # Starting out
  1. # Install EVEMon

Download EVEMon from [Github](https://github.com/mgoeppner/evemon/releases).

  1. # Set up character
Once EVEMon is installed and running you should have an **Overview** tab telling you to click the File>Add Character. Upon clicking, a second window called **ESI Key Import** will open, prompting you to log into your EVE Online account. In the browser window that opens, follow these steps through to the character selection screen and select the character you would like to add to EVEMon. Finalize the process by clicking **Authorize** for the right character, then clicking **Authorize** again when prompted for access to the ESI scopes EVEMon requires. The browser window will now display an **Authentication successful** message and can be closed. In the EVEMon **ESI Key Import**, the character you have tried to add will be displayed. If this is the character you intended, click **Import**. The character has been imported into EVEMon and will appear in your **Overview** tab, ready for use.

To import more characters, simply repeat the steps above until all the characters you require have been added to EVEMon.

1. # Create plan
With the character overview open you can create a new plan by selecting new from the plans menu and giving this new plan a name.  You can have multiple plans which can be combined to form big plans a year or longer in length.  You can also import plans written in text files by the Plans>Import Plan From File menu.  The new plan should open as a big window with a number of options along the top and left-hand side.

  1. # Adding your first skill
Select the Skill Browser tab.  In the skill tree open Spaceship Command and click on .  A skill tree will appear showing all of the skills you would need to learn in order to learn Amarr Battleship.  Above the tree is a description of the Amarr Battleship skill and times to learn each level of the skill. On the far right just above the tree is an option to "Show what this skill enables."  That will show you modules, ships and other skills which use this skill as a prerequisite.

Right-click on Amarr Battleship at the top of the tree and select "plan to level 1".  Now switch tabs to the Plan Queue.  Here you can see the Amarr Battleship skill I along with all of the prerequisite skills needed.  There are columns showing the time to learn each skill the learning stats such as rank and attributes for the skill and the estimated total **Skill Points**(SP) after learning each skill.  Black skills can be learned immediately.  Greyed skills can be learned once the earlier levels have been trained or once you have purchased the book and injected the skill.  Red skills require another skill as a prerequisite.  At the bottom of the window is a summary of the plan including a total training time. Taken together, this gives you the information you would need to pursue your plan to fly an Amarr Battleship.

  1. # Researching a full plan
If you actually wanted to fly an Amarr Battleship with any success you would have to research a fitting and skills needed to effectively run the ship.  Each of the modules will have required skills.  In order to put the ship together, you will need some basic ship fitting skills to meet the **powergrid** and **CPU** requirements for the ship.  All together these skills will create a much larger plan.

For any plan you will have to do research to figure out all the skills you need and want.  You can use the various guides in this wiki, which often list skills needed for their particular activity.  You can use the Ship Browser in the EVEMon Plan window or just browse the Skill Browser and pick skills you think will help you.

  1. # Remapping and skills
Remapping points can be added in the middle of a plan.  EVEMon can even suggest a mapping based on the skills you are considering.  An excellent detailed discussion of various **skill**s and how they can benefit you can be found elsewhere on the UniWiki.

1. # Advanced features
  1. # Multiple plans
A skill plan including skills from various areas of specialization can quickly get messy.  A plan like that can be good for getting the right remapping points, but lacks flexibility on figuring out exactly what you should be training next.  Making multiple plans solves this problem.  Each plan can have a specific theme or goal.  For instance, all of your drone skills might go in one plan, or the plan could be all of the exploration skills you might need.

Managing multiple plans in EVEMon is simple.  When you add skills the skills go in the currently selected plan.  You can combine plans into a new plan by selecting Plan|Manage on the character window.  Thus you can make one huge master plan from all of your individual plans.  Any duplicate skills will be combined during merging.  You can also set EVEMon to remove skills once they are learned, and the skills will be removed from all plans once you have finished the skill.

  1. # Attribute remapping points
How fast a skill can be learned is dependent on the two character **attributes** the skill is based upon. To optimize the duration of skill training, a **neural remap** can be done for the character. **WARNING:** If you never used the remap function in the EVE client, or you are not entirely sure what its effects will be, get the advice of experienced players; using a neural remap could in the worst case lead to skills being trained slower, thus losing months of training time down the road.

EVEMon allows to add remapping points to a skill plan, so that the effects of attribute remapping can be planned when creating a long-term plan. Just mark a skill in the plan and choose the button "Toggle remapping point" in the left sidebar. Then press "Attributes Optimizer..." from the skill plan's top row, and choose "Use the remapping points I set up" to simulate the neural remapping at this point in the plan. As only one remap per year is available for characters past their starting phase, the remapping function makes most sense to include in a skill plan that covers at least one year of training time.

  1. # Importing and exporting skill plans
Plans can be made and exported, or imported into a new plan.  The export is done by clicking on the Export menu in the Plan window.  To import the same plan you must use the **Plan|Load Plan From File...** menu on the character window.  Exported plans can be imported by any other character or person.

Note that the "Save Settings..." option will create a backup file with all of your EVEMon data, including but not limited to characters and their respective skill plans. You can find this setting in the toolbar, *File > Save Settings...*. Additionally, if you navigate to *Tools > Options... > Cloud Storage Service*, EVEMon provides the ability to automatically synchronize your settings with your cloud storage provider of choice (currently Dropbox, Google Drive, and OneDrive are available). This could serve as a replacement to manually exporting all settings, if you so desire, while at the same time, granting you the flexibility to access your EVEMon account from different computers.

  1. # Skills based on ships
You can build a ship plan and have EVEMon figure out the skills needed to use the ship and all the modules.  The ship plan can be built in **Python Fitting Assistant**, the in-game fitting window, or taken from an EFT format created by another capsuleer.  Import a ship from PYFA by starting up PYFA and creating a ship fitting.  Under the Fit menu on the top bar, there is a "To Clipboard" copy option.  Go to EVEMon and create a new plan with an appropriate name. Once made, select the Loadout Import option from the top right of the plan window.  You can now paste the EFT-formated fit into the new window.  Add to Plan at the bottom will add the necessary skills to your plan. In all cases EVEMon will give you only the skills needed to use each module. You may still need to add some fitting skills so that you have enough **CPU** and **powergrid**, the necessary support skills for weapon and drone application and damage, etcetera.

  1. # Monitoring market orders and manufacturing
EVEMon has the ability to monitor market orders and manufacturing.  It will alert you when either has changed, such as when someone purchases part of a market order, or manufacturing has concluded. This functionality can be enabled when on the character view. Below your total SP amount, press the small "advanced features" cog icon and enable the "market" and "industry" features, as well as any others you may be interested in.

  1. # Minerals worksheet
This is a basic little worksheet found on the character window which will calculate the total ISK value of something based on the ISK value of the minerals.

  1. # Blank character
You can create blank characters to test out plans for new alts.  Go via File -> Manage Characters -> Import -> Use File.  To do this you will need a blank character file like the one below. Copy this text into a file and save it as e.g. BlankCharacterSheet.xml, which you can then import via the above route:
 <code><?xml version='1.0' encoding='UTF-8'?>
 <eveapi version="2">
   <currentTime&gt;2010-03-22 06:24:58</currentTime>
   <result>
     <characterID>545149903</characterID>
     <name>Blank Character</name>
     <race>Gallente</race>
     <bloodLine>Intaki</bloodLine>
     <gender>Female</gender>
     <corporationName>Center for Advanced Studies</corporationName>
     <corporationID>1000169</corporationID>
     <cloneName>Clone Grade Alpha</cloneName>
     <cloneSkillPoints>900000</cloneSkillPoints>
     <balance>5000.00</balance>
     <attributeEnhancers />
     <attributes>
       <intelligence>20</intelligence>
       <memory>20</memory>
       <charisma>19</charisma>
       20
       <willpower>20</willpower>
     </attributes>
     <rowset name="skills" key="typeID" columns="typeID,skillpoints,level,unpublished">
     </rowset>
     <rowset name="certificates" key="certificateID" columns="certificateID" />
     <rowset name="corporationRoles" key="roleID" columns="roleID,roleName" />
     <rowset name="corporationRolesAtHQ" key="roleID" columns="roleID,roleName" />
     <rowset name="corporationRolesAtBase" key="roleID" columns="roleID,roleName" />
     <rowset name="corporationRolesAtOther" key="roleID" columns="roleID,roleName" />
     <rowset name="corporationTitles" key="titleID" columns="titleID,titleName" />
   </result>
   <cachedUntil>2010-03-22 07:24:58</cachedUntil>
 </eveapi> </code>
