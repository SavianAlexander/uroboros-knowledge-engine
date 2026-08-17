---
title: "Horde-Multiboxing 101"
url: "https://wiki.eveuniversity.org/Horde-Multiboxing_101"
pageid: 24274
source: "EVE University Wiki"
categories: ["Guides"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Horde-Multiboxing 101

This guide was created on 2022-01-05 by The Legi0n while in Pandemic Horde.

  1. # SET UP
Firstly, to set up for Multiboxing, there are a set of setup and setting steps that are required. Multiboxing is more APM intensive than single boxing, and requires a series of keybinds, but also a set up of your overview, locked targets, windows, and chat boxes to present you with as much information as you can receive in the smallest amount of space.

Also, this is developed from the perspective of a right handed person - A left handed person would have to customize these keys, but please use the similar principles.

For Twitch Steam Recording of live class, go to:

https://www.youtube.com/watch?v=nTGe1HIBepI

  1. # Why Multibox?
Eve is a game of scale, and a game of “N+1”

Who would win in a fight, you and four of your friends? Or five of the other guys, who also brought an alt each? Its possible, but much more likely that the 10 characters in ships will often beat the 5. Additionally, if you enjoy mining as a profession, and can make 30-45mil an hour, adding a second toon will bump that to 60-90 mil an hour. Adding multiple toons often scales your income, PVP effectiveness, and other benefits.

  1. ## A Word of Caution:
Multiboxing is allowed within Eve Online, but there are several exceptions that break EULA. If you follow this guide, you will not be in violation of EVE’s EULA.

Two things specifically that come up:

Input Broadcasting,

Alpha Clone Multiboxing.

Both are EXPLICITLY banned by EULA, and will result in banned accounts and other punishments. The key way to avoid breaking these rules:

One action, one keypress. No Macros, physical or otherwise allowed in any instance. Additionally, no pushing a button on one account and having it “broadcasted” to your other accounts. One action, one keypress.

Secondly, NO ALPHA CLONE MULTIBOXING In ANY way, shape, or form. No you may not use a laptop and a desktop and have the laptop run an alpha clone. That is against EULA. If you have any more than one account logged in that you are using, they must ALL be omega.

  1. # EVE-O Preview SET UP:
I won’t cover the intricacies of Eve-O Preview in this guide except for a suggestion of rewriting code in the configuration file that is required to meet the burst APM Multiboxing requires.

<nowiki>https://github.com/EveOPlus/eve-o-preview</nowiki> is the link for the download, read through the install instructions<syntaxhighlight lang="actionscript">
},
"ClientLayout": {},
"ClientHotkey": {
"EVE - The Legi0n": "1",
"EVE - Secondary In A": "2",
"EVE - DEF Mining Corp": "3",
"EVE - Solaire of Astora": "4"
},
</syntaxhighlight>This piece of the code is inserted near the bottom of the “EVE-O Preview” JSON file, where you will find a similar code. Be sure to copy and paste this into the file. You must change the name of your characters to your own characters, and you must leave the space between the “-”. This is CAP and Spacing Sensitive. Note, I have 4 characters listed - only do this for characters you will be multiboxing.

The correct phrasing of the character name will match the EVE-O Preview name for the character and be in the format below:

“EVE - XXXXX” Where you replace ONLY The X’s with the correct spelling, numeralization, and capitalization of your character names.

The 1, 2, 3, and 4 relate to the keybind for the characters window - being the number bar above the main keyboard. I specifically recommend going with these keybinds for your preview, and rebinding the “Tag Item As” keys in Eve.

  1. # EANM SET UP:
EANM allows you to set up your windows once, and then copy the windows on one character to ALL characters that you select in the editor. I will again not go into the details of setting this up - it is presumed that you know the basics of multiboxing. Use EANM to place windows and chats similar to the picture below. <nowiki>https://github.com/FontaineRiant/EANM</nowiki>

Specific locations are preferential, but I would HIGHLY suggest a layout similar to the one in the picture. The key points in the image for layout purposes are:

1) Broadcasts are near your watchlist - easier to see and to watch over a smaller area.

2) Modules are near your target (the Basi and Kirin are moved up one level, more on the in-fleet setup later)

3) Chat Channels are layered in level of importance. It is also near broadcasts to not need to move my eyes much and to utilize peripheral vision.

4) On the Second screen (preferred) I have my 4 accounts open in EVE-O Preview, nice and large and visible (Easier to notice yellow boxes). I edited out the rest of the second screen, but if preferred, you can blow the windows up larger on the other screen.

5) ALL WINDOWS ARE PINNED

6) Locked targets are closer to the rep buttons, to make it easier to move reps around and localize vision near your modules.

6) Pinning your windows prevents moving them around during combat, and screwing up the system and taking time and APM to fix. Make sure to pin your windows once, and never move them. Will make other actions significantly slower, and speed is life.

  1. # MISC. KEYBINDING STUFF:
Broadcasting for Shield - “X”

This places the broadcast for shield button on the left hand, and close but not too close to the remainder of the shortcuts that we will be using

Make sure your standard keybinds for navigation are correct:<syntaxhighlight lang="actionscript">
Approach - Q
Orbit - W
Keep At Range - E (ensure this is the anchoring distance for your doctrine)
Align - A
Warp To - S
Dock/Jump/Activate Gate - D
</syntaxhighlight>

Rebind to a mouse key of your choice: `Toggle Lock Target`

Radial Menu helps with APM as well, being able to instantly see brackets also helps with APM.

  1. # SHIP SET UP:
Additionally to your keybindings, your ships need to be set up similarly.

I prefer to have the targetable modules on one line, the MWD immediately underneath those in the first position, Refer to the set up picture for an example. Once you have a preferred set up, copy the module set up to your other ships on other characters. This is customizable, but keep the targetable modules in the F1-F5 position

Keep any modules that pose a significant risk to the fleet or yourself, FAR AWAY.

Bombs, Smartbombs, Bubbles, Hictor Bubbles, ETC. All should be on a hard to reach hotkey, so that you won't accidentally fat-finger them in combat while swapping clients,

You also want to pre open up your cargo hold/drone bays and ensure they are in an easy to access position as well for taking drugs.

All of this setup is to help us achieve several things.

1) Reduction in Input Time as your hand should be close to the keys required

2) Reduction in target acquisition time, as you are not looking around the screen

3) Reduction in decision making time, as you can practice the inputs in the guide below

4) Present Intel as clearly as possible. By condensing the intel you need into concise places

  1. # WATCHLIST SET UP:
Set up your watchlist per the doctrine standard. If you have additional space in your watchlists on your characters, start adding your alts to the watchlist as well. This can help give you more intel on where they are and how their health is - if you are switching screens fast, it can be harder to see small damage or if they are getting locked. Also, use color coding on each of your accounts, to help see the FC, and important targets.

  1. ## Potato Mode:
Depending on your PC/graphics card, you may need to downgrade your graphics settings, and disable sound to allow multiboxing on your PC. Generally, when you start to notice frame rate drops, or disconnects during heavy graphical fights and other CPU intensive fights with large groups, this may be a signal for you to downgrade your graphics.

Ideally, you will be able to optimize for memory - which will enable effects, allowing you to see bubbles, turret effects, and other important visual cues, but if your FPS remains unstable, optimize for performance.

Additionally, Eve typically has a lot of performance tied into its sound. If you must, disable sounds. If you can run with some sounds, some key tips and advice.I would suggest keeping alarms, gate sounds, and reload cues.

  1. ## Adding Accounts:
When learning to Multibox, add accounts slowly. Make sure you learn a role while singleboxing before moving on to multiboxing the role. Learning each role well will help you when multiboxing, as it will be familiar, and will not take as many mental cycles to figure out what to do.

  1. ## Tunnel Vision:
When multiboxing, it is imperative that you avoid tunnel vision to preserve the life of your ship or the fleet. This generally means focusing on all of your characters to keep them alive and combat effective, and when running eyes, regularly touching in on each of them to ensure you do not miss critical intel. Getting into the habit of regularly swapping screens will help reduce the tunnel vision, and prevent you from “home-ing” on one character, and letting your eyes alt or cyno alt die to rats on a gate when you were supposed to be moving it to an important destination. Regularly swapping characters and assessing their threat/making sure they are following fleet orders and tasks is paramount.

  1. ## Other Notes and Tips:
To help differentiate your accounts, it can help to change the color associated with the account. Some people chose colors based on the alts role, while others keep them separated by position “Red is alt 1, Green is alt 2” or “Red is sabre, Green is logi”

Because of the dangers, it is imperative that you do not tunnel vision on one character - your “main” while you are multi-boxing. You MUST be consistently going through the views of your other accounts while your reps are cycling, and you MUST be prepared for target swaps and to broadcast being targeted.

Also, you must be AWARE of which account is doing which thing, which again necessitates awareness of the fleet and where your character ship is inside of those blobs. Communication is key here, and being able to say which character you are viewing in voice comms is also imperative.

Another Strong word of caution: it is highly advised that you do not multibox logi. Logi is very APM intensive, and failing to execute it perfectly can hinder more than you are helping while making the attempt.
