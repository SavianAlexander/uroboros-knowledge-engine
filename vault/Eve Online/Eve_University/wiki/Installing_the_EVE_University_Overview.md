---
title: "Installing the EVE University Overview"
url: "https://wiki.eveuniversity.org/Installing_the_EVE_University_Overview"
pageid: 9420
source: "EVE University Wiki"
categories: ["Applying to EVE University", "Getting Started", "Guides"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Installing the EVE University Overview

- EVE University** has its own **Overview** Profile set up, which we expect all members to use. This will ensure that all members of the Uni, whether in a fleet or otherwise, see the same Overview settings for Appearance (colortags and backgrounds) with the proper priorities, and are clear as to which targets they are able to shoot and which they may not. It is important that potential members have this Overview set up before joining, even if they are not intending to train their character into combat. It offers a number of presets which are designed to provide our members with a wide variety of possibilities due to the broad scope of EVE University's operations and communities. Once familiar with how to set up their Overview, members are free, and encouraged, to personalize their own presets to suit their needs. The Appearances should not be edited as these are most critical to remain the same for all members.

1. # Import the Overview Pack In Game

This is the recommended method for installing the EVE University Overview:

# Join the **** chat channel in game.
# Follow the instructions in the chat channel's Message of the Day and click the links to import first the Z-S Overview then the EVE University adaptation.

If you are docked, you can still view and alter your overview settings.
- 

To access your Overview Settings you can either add a shortcut or use a **slash command**.

  1. # Command
# Go into any chat window.
# Type in: **/open overview settings**

  1. # Shortcut
# Press *Escape*.
# Go to the *Shortcuts* tab.
# Within the *Shortcuts* tab, go to the *Window* sub-tab.
# Scroll down and you will find an *Overview Settings* option - set any keybind to this command.

Now you can use this keybind even when in a station, and you will open the *Overview Settings* window.

  1. # Assigning the Tabs and Brackets
After importing the overview tab you will still need to select what overview presets are used.

To select overview presets go to the **Overview Tabs** tab in overview settings.

Each row controls the state of one overview tab.

# Set the tab name on the left. This name is shown on the overview window.
# Set the overview preset in middle. This controls what objects are shown in overview.
# Set the bracket preset on the right (or leave as "Show All Brackets"). This controls what brackets are visible in space.

You can have up to eight tabs on your overview. The exact composition will depend on what activities you do and your personal preferences.

1. # Help! I get lots of weird text after changing a setting

    - Note:*** Use this following method only after fully reading it, including the UPDATE at the end.

If you made a change to a Preset (such as adding 'Invading Precursor Entities') and then saved it, you will find the Preset name now has text like <code><color=0xFFFFFF66></code> in front. This is a result of a safety feature built into the EVE Client to strip HTML coding from text entered in-game. But it's fairly easy to fix, and here's how (it can be done while EVE is still running):

# Open Overview Settings in-game, and switch to the 'Misc' tab.
# Click 
# Select 'Check All' at the top, and give a memorable Filename (such as *charactername-month-day*) and click 
# You will receive a message indicating where the file was saved. By default on Windows, this is in C:\Users\[username]\Documents\EVE\Overview\[filename].yaml
# Browse to this directory in your file manager, and open the file in your favorite text editor.
# With your text editor's "Find and Replace" feature, look for and replace the following :
1. # Replace all  with
1. # Replace all  with
# Save the file and return to EVE Online
# Open Overview Settings in-game and switch to the 'Misc' tab again.
# Click 
1. # The Overview Settings window will close.
# Re-open Overview Settings and switch back to 'Misc' tab.
# Click 
# Select the file name you just edited, and be sure to check the 'Check All' box.
# Click 

Your overview colors should now be restored.

Note that you may use this same 'fixed' save file on other characters if you wish them to have the same overview settings.

    - UPDATE:*** There is an issue with the above method that is much harder to resolve than it seems. Following the above process will result in a duplicate entry for the bracket(s) you "fixed". What this causes in game is whichever one is later in the file is the one that is actually shown - and this usually seems to be the one that was NOT changed (e.g. adding the Invading Precursor Entities, they will go away again). There is no reasonably easy fix for this, unless you have a text editor such as Notepad++ that can understand YAML format and allow you to collapse sections. What you must do is remove the older copy of the duplicate section(s).

If you choose to use Notepad++ for this, then BEFORE changing as above, View->Fold All, and look for the two collapsed sections with a similar name (e.g. both have "PvX: Basic (+Neut +NPC)" but one has the  and
 -- expand the copy that has the  and  and carefully delete that section. Be sure to not delete any portion of the adjacent sections! Delete everything from the section heading down to the next section heading and *leave no blank lines in between* (YAML is not a very forgiving markup language).

Once you have done this, then you can fix the  and  as in the above steps.

1. # Faction Warfare and the EVE University Overview

The EVE University Overview has been updated to ensure friendly designations (pilots in your corporation or blue to your corporation) are prioritized over pilots appearing as at war with your militia (orange flashing star).  This ensures that players are not firing on friendly players that happen to be in opposing militias, in accordance with the rules of engagement in EVE University.

If you participate in Faction Warfare, it is highly advised you ensure you have the most recent EVE University Overview settings, or at least check that your overview priorities are set up correctly for it.  See the image below - the right side of the image is how the overview MUST be set up for all Faction Warfare participating EVE University members.
