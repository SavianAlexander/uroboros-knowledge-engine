---
title: "SingularitySetup"
url: "https://wiki.eveuniversity.org/SingularitySetup"
pageid: 19746
source: "EVE University Wiki"
categories: ["Applications", "Candidates for merging", "Guides", "Needing updates"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# SingularitySetup

This is a guide to simplify getting your character set up on the **Singularity** test server. A lot of this was taken from other sites and simply compiled in one place. There are a few things you should know up front if you have never used Singularity before. 

- If you have a relatively new character (or account), it may not exist on Singularity. This can be true even for characters that are three months old or more. If you recently went Omega and your character exists but is still an Alpha on Singularity, you can buy PLEX (very cheaply) and activate Omega on Singularity.
- There are some general rules of conduct for the public test servers found [here.](https://community.eveonline.com/support/test-servers/test-server-rules/) (e.g. "Combat by consent only, except in the designated combat system (M-OEE8).")
- Markets are seeded in every constellation. Nearly everything is priced at 100 ISK and is in bountiful amounts.
- Players living in wormholes on Tranquility will be moved to k-space. Their assets will be impounded at a station. But you can instantly travel to and buy everything cheaply in Thera or M-OEE8 (the main combat system).
- Stargates are sleepy. Often when traveling you will get a traffic control message delaying your jump. You will have to request your jump a second time. But you can move to the main systems instantly and shouldn't need to use stargates.
- Your skills will not be current but you can instantly update them. Skill injectors are not seeded in markets and orders are often placed at exorbitant prices, far higher than Tranquility. However, using skill injectors means you will not be able to update your skills instantly using the slash command (see below) for a period of two weeks.

1. # Connecting to singularity
- Start EVE Launcher
- Once EVE Launcher loads, it will show the current server at the bottom right:

- Click the down arrow to the right of where it says Tranquility, and you will have a drop down server list:

- Select Singularity, the server name at the bottom right should now have changed
- Click the play button to the left hand side of the account that you wish to play as. This will load the snapshot of this account from when the server was last mirrored.

Important Notes:
- You may have to add your account if this is your first time connecting to this server
- If you have changed your password fairly recently, then the mirror might expect your OLD password
- If you have a fairly new character, then it might not exist on Singularity if it was created after the last snapshot was taken
- Make sure to change it back to Tranquility when you are finished testing so you don't accidentally load the wrong server, later <https://wiki.eveuniversity.org/Singularity#Connecting_to_Singularity_via_Steam>

1. # Copying your UI from your EVE character
(This works for game windows but not everything in the UI - keyboard shortcuts and broadcast settings appear not to copy, e.g.)
  1. # TQ, Log in/Log Out
Log into the character you want to copy the HUD/UI *from* on Tranquility. Log back out.

  1. # Finding the TQ folder
- On Windows, some directories will be hidden (like AppData) so you may need to set Folder Options to 'Show hidden files...' to be able to view the folder.
- Your EVE config files may be in a different location, see possible locations below.
- Navigate to the **settings_Default** folder which is located in your Windows user AppData folder. The exact location will depend on where your  is, so you'll have to adapt accordingly.

Possible locations ... 
 C:\Users\<NAME>\AppData\Local\CCP\EVE\_sharedcache_tq_tranquility\settings_Default (if EVE is installed in )
 %localAppData%\CCP\EVE\_sharedcache_tq_tranquility\settings_Default (if EVE is installed in )
 %localAppData%\CCP\EVE\_sharedcache_tq_tranquility\settings_Default (if EVE is installed on your {Co|#FF1493|D: drive through Steam}})
 %localAppData%\CCP\EVE\_sharedcache_tq_tranquility\settings_Default (if EVE is installed in )

  1. # Copying the UI data
Sort by date modified and the most recent core_char_#####.dat is your [copy from] character UI file. Make a copy of this file.
 core_char_#####.dat

  1. # SISI, Log in/Log Out
Log into the character you want to copy the HUD/UI *to* on Singularity. Log back out. This will ensure you have a UI file for Singularity in 
  ..._sharedcache_sisi_singularity\settings_Default

Refresh and the newest core_char_#####.dat is your [copy to] character UI file.

  1. # Copy from TQ folder to SISI folder
Now copy the [copy from] file, and change the ##### to match the [copy to] character. If you are copying from the same character the number ##### should already match.
 copy from: ..._sharedcache_tq_tranquility\settings_Default 
 copy to:   ..._sharedcache_sisi_singularity\settings_Default 

Your UI/HUD is now copied. Note that you can make copies with (charname) so that you have a record of which ##### goes with which character--as that is always the same, even on other machines.<https://forums-archive.eveonline.com/message/6802455/#post6802455>

1. # Copying your overview settings
 ]] 
On Tranquility, using the hamburger menu on your overview window:
- Open Overview Settings > Misc tab
- Export Overview Settings
- Check All
- enter a filename you'll remember and click 'Export' (e.g. charname_date)

On Singularity, using the hamburger menu on your overview window:
- Open Overview Settings > Misc tab
- Reset All Overview Settings
- Import Overview Settings
- select the filename you just saved
- make sure to select "Check All" *after* selecting the filename
- refresh brackets as desired

1. # Updating your skills and moving to combat system
There are several special slash commands available for players on Singularity, to make it easy to test something without having to spend too much time with setup. To use these commands, just type them with a leading / into any chat channel. <https://community.eveonline.com/support/test-servers/singularity-player-commands/>

The main commands you will need are:
- /copyskills (to update your skills)
- /moveme (A window will pop up asking where you'd like to move - for example, select M-OEE8 or Thera. This will put you in warp in the target system, then you can dock up at the main market, e.g. "M-OEE8 - Singularity Testing Keepstar" or "Thera XII - The Sanctuary Institute of Paleocybernetics")

1. # References
[CCP Singularity page](https://community.eveonline.com/support/test-servers/singularity/)

[More information about slash commands](https://community.eveonline.com/support/test-servers/singularity-player-commands/)
