---
title: "Overview manipulation"
url: "https://wiki.eveuniversity.org/Overview_manipulation"
pageid: 9383
source: "EVE University Wiki"
categories: ["Guides", "User Interface"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Overview manipulation

Information on what's possible to manipulate when it comes to the **overview** in EVE Online as well as some practical examples. The overview is essential in showing you what's happening around you. More information about how to set it up according to EVE University standards can be found on the **Installing the EVE University Overview** article.

1. # What can you manipulate?
  - thumb|Most people edit the overview file to change the appearances of the **tabs** and the **labels**.**
While you can make any number of changes to the overview through the .yaml file, almost all of the things that can be changed is much easier and more reliable to change in-game, with the exception of changing colors, font sizes, styles etc of the tab names and the ship labels / brackets in space.

  1. ### Tab appearance
The *Overview Tabs* settings in-game will allow you to add HTML-formatting, but most people prefer to edit this outside the client anyway due to the highly restrictive input fields. It's much easier to edit those values in a proper text-editor than trying to do it in a tiny little window that shows but a few letters at a time.

  1. ### Ship labels / brackets in space
Whenever you select a target or hover over a bracket in space you'll get some information about the entity. By manipulating the .yaml file you can customize this to show the information in different colors, font sizes or even with personalized line breaks etc. These changes will affect your combat notifications as well and show the parts regarding players and player owned entities appropriately formatted, which is an added bonus that leads to improved readability of onscreen combat messages. If you decide to add manual line breaks or other formatting code, be sure to check that the onscreen combat messages are still readable.

You can only change the appearance of players and player items (like mobile depots) this way, celestials, anomalies, NPC ships etc will have their default appearance no matter what you do.

1. # How do you go about manipulating the overview?
  - thumb|Access your overview settings with your [[Keyboard_controls#Modifying_Shortcuts|shortcut**, chat-channel command or through the regular right-click context menu.]]
  - thumb|**Importing** and **exporting** settings is done by clicking the buttons at the bottom of the *Misc* tab in the overview settings window.**

The easiest way to manipulate your overview is to save your current overview and then export it into your documents folder. Then you can open the overview file in a text editor and quickly view your changes in-game by saving the file and importing the new settings. That way you can easily tinker with your overview until you have it just the way you like it.

  1. ### Managing your overview settings while docked in a station
You can set up your initial overview while still being safely docked in a station. To open your overview settings without being in space you can use the channel-command  or by setting up a **shortcut** for your **Overview Settings** window (you'll find it in the escape menu's **Shortcuts** tab under **Window**).

You will still need to undock in order to verify and get used to your new overview settings, but this way you can avoid actually being in space while alt-tabbed or fiddling with your game menus.

  1. ### Exporting your current settings
Open your *Overview Settings* window and go to the *Misc* tab. At the bottom of the tab you'll see two button, *Import Overview Settings* and *Export Overview Settings*. It's **highly recommended** that you start by making a backup of your settings by exporting them into one file first, before making another export with another name, with the intention of using the second copy as a work-in-progress file.
  1. ### Location of your overview files
The files will end up in your personal Documents folder along with screenshots, chatlogs etc (not to be confused with the application data folder where your other settings are stored). The folder is created automatically the first time you export your settings, so normally you won't have to do that yourself.

Where this folder is depends on your operating system.

| - style="background-color: var(--background-color-warning-subtle);"
! OS
! Location of the folder |
| :--- |
| 38px]] |
| 38px]] |

1. # Editing the overview file out-of-game
The overview is saved in the .yaml file format and can be edited in pretty much any kind of text-editor, like the commonly used [Notepad++](https://notepad-plus-plus.org/), but of course the standard notepad editor that comes with Windows works as well. Simply right-click the file and open it with your favorite text-editor to start editing. The majority of the changes you're likely to make (tab and label edits) will be at the very end of the file.

  1. ### File structure
The overview is stored in .yaml files where you can write plain HTML-code and it'll be parsed just fine. Attributes and values are split across individual lines, with  markups identifying and grouping the variables. Here's an example with changes  and comments in :

</includeonly> style="font-size: 90%; max-width: fit-content;">
tabSetup:  
- - 0  
  - - - bracket
      - null
    - - name
      -   
    - - overview
      -   
- - 1  
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 

shipLabelOrder:  
- ship type  
- pilot name  
- corporation
- alliance
- ship name
- null
shipLabels:  
- - null  
  - - - post  
      - ''  
    - - pre  
      - '['  
    - - state  
      - 0  
    - - type  
      - null
- - alliance  
  - - - post
      - '>'  
    - - pre
      - '<'  
    - - state
      - 1  
    - - type
      - alliance  

</includeonly>>

  1. ### Reloading settings while in space
You can easily purge or load new settings while, but in order for the new settings to take full effect (especially ship labels) you'll need to load a tab that doesn't have ships or player owned entities on them (to sort of "purge" them from memory) and then swap back to a tab that does show them. Once you do that, the new settings will be in full effect.

The **podsaver** tab is excellent for this, as it shouldn't contain any player entities, so swapping to the podsaver and back everytime you reload your settings should be enough.

1. # Modifying the tab appearance and ship labels ingame
By opening up the **Overview Settings** page and going to the various tabs you can quickly change some of this directly. The **Tab Name** text-field on the **Overview Tabs** page will only show you a maximum of 17 characters at a time and the text-fields for the **Ships** tab is even worse, only showing a maximum of 3 characters at a time. This is why why many prefer to edit this directly in the overview file, where there are no limits or restrictions.

  - thumb|320px|In the **Overview Tabs** you can quickly edit the name and formatting of your tabs.**

  - thumb|320px|In the **Ships** tab you can change the pre- and post-formatting for ship labels and brackets in space.**

# Format and style
The overview supports a video variety of style formatting in plain html-code.

****:
> You can use simple HTML-coding such as normal  and  tags, but also things like line breaks , bold , italic  etc.

****:
> For colors, either use the simple **color name** or the **HEX-based**  format, so if you wanted the color  you could either do  or .

****:
> You can also use various ASCII- and HTML-codes, like rooks ♜ ♖, kings ♚ ♔, horses ♞ ♘, airplane ✈, skull ☠, yin and yang ☯, stars ★ ☆ or whatever else you might find. Not all symbols will work, or even turn out the way you thought they would, but you can easily just check that out in a chat window beforehand.

See **w3schools**' [text formatting](https://www.w3schools.com/html/html_formatting.asp) or [color names](https://www.w3schools.com/colors/colors_names.asp) pages, or **wikipedia's** **Web colors** page if you're new to HTML-coding.

For a list of symbols that work in EVE you can check **Cassiel's Symbols** page. It's possible there are more symbols that might work, so feel free to check out [ASCII Codes](https://www.theasciicode.com.ar/) or [Symbols](https://copypastecharacter.com/symbols) for inspiration, but remember that some of those symbols won't work in EVE.

1. # Example
This is an example of one of the pre-saved overviews that were available at the time of writing this guide. On the left is the unedited version of the overview, on the right is the code with the changes  that enables the color-coding and font-changes.

  1. ### Tab appearance
These changes are possible to do in-game, albeit tricky since the window and editing fields are extremely limited. But the game will accept and change these values from inside the game, so there's technically no need to export and edit the files if this is all you want to edit.

In this example I removed the bolding and simply made the font a little larger, because I have my interface scaled to 90% and my context-font set to 11 (which the tabs won't use for some reason). I also added some colors and removed the dots and just used regular space to widen some of the shorter-named tabs and rearranged the tab order itself.

| Original version | Modified version |
| :--- | :--- |
| 
tabSetup:
- - 0
  - - - bracket
      - null
    - - name
      - <b>.  PvP  .</b>
    - - overview
      - 1a - pvp + drones
- - 1
  - - - bracket
      - null
    - - name
      - <b>.  PvP Travel  .</b>
    - - overview
      - 2 - pvp travel
- - 2
  - - - bracket
      - null
    - - name
      - <b>.  Situational  .</b>
    - - overview
      - 3 - missioning
- - 3
  - - - bracket
      - null
    - - name
      - <b>.  Fleet  .</b>
    - - overview
      - 7 - fleetmates
- - 4
  - - - bracket
      - null
    - - name
      - <b>.  Pod Saver  .</b>
    - - overview
      - 5 - pod saver | </onlyinclude>>
tabSetup:
- - 0
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 2 - pvp travel
- - 1
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 7 - fleetmates
- - 2
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 3 - missioning
- - 3
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 5 - looting
- - 4
  - - - bracket
      - null
    - - name
      - 
    - - overview
      - 5 - pod saver
</onlyinclude>> |

  1. ### Ship labels
The format of this is pretty straight forward. The  tag marks the beginning of the settings for labels and the  indentations breaks up the various attributes. The  attributes add stuff before the label while the  attribute add stuff after the label. The  attribute is a simple integer showing if it's enabled (1) or disabled (0) while the  attribute is the name of the attribute. The value for each attribute ends up on the line below, after the  indentation. Text doesn't have to be wrapped in s, but can if you feel that makes it easier to read.

Depending on the order of these labels and the fact that some labels might not show all the time (not all corporations belong to an alliance and not all players will have a corporation tag), take a few minutes to decide if and where you'd your space. In this example, I moved the space from after the player name to before the corporation ticker, so that if the player isn't in a player corporation I won't get a superfluous space added.

| Original version | Modified version |
| :--- | :--- |
| 
shipLabels:
- - null
  - - - post
      - ''
    - - pre
      - '['
    - - state
      - 0
    - - type
      - null
- - alliance
  - - - post
      - '&gt;'
    - - pre
      - '&lt;'
    - - state
      - 1
    - - type
      - alliance
- - corporation
  - - - post
      - ']'
    - - pre
      - '['
    - - state
      - 1
    - - type
      - corporation
- - pilot name
  - - - post
      - ' '
    - - pre
      - ''
    - - state
      - 1
    - - type
      - pilot name
- - ship name
  - - - post
      - **
    - - pre
      - **
    - - state
      - 0
    - - type
      - ship name
- - ship type
  - - - post
      - ')'
    - - pre
      - '('
    - - state
      - 1
    - - type
      - ship type
 | </onlyinclude>><nowiki>
shipLabels:
- - null
  - - - post
      - ''
    - - pre
      - '['
    - - state
      - 0
    - - type
      - null
- - alliance
  - - - post
      - ')</nowiki><nowiki>'
    - - pre
      - ' </nowiki><nowiki>('
    - - state
      - 1
    - - type
      - alliance
- - corporation
  - - - post
      - ']</nowiki><nowiki>'
    - - pre
      - ' </nowiki><nowiki>['
    - - state
      - 1
    - - type
      - corporation
- - pilot name
  - - - post
      - ''
    - - pre
      - ''
    - - state
      - 1
    - - type
      - pilot name
- - ship name
  - - - post
      - '</nowiki><nowiki>'
    - - pre
      - ' </nowiki><nowiki>'
    - - state
      - 0
    - - type
      - ship name
- - ship type
  - - - post
      - '</nowiki><nowiki> '
    - - pre
      - '</nowiki><nowiki>'
    - - state
      - 1
    - - type
      - ship type
</nowiki></onlyinclude>> |

  1. ### End result
The above mentioned example will end up looking like this:
