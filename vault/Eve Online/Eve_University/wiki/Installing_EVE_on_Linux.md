---
title: "Installing EVE on Linux"
url: "https://wiki.eveuniversity.org/Installing_EVE_on_Linux"
pageid: 2410
source: "EVE University Wiki"
categories: ["Applications", "Guides"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Installing EVE on Linux

=== General === 
 
For the Steam and Lutris setup shown on this page we assume Linux Mint 22.2, but every (?) distro will work. Everything might be a bit different in your specific setup, but the steps are always very similiar. In our experience the easiest is to play EVE Online on Steam. Lutris is a bit more work but doable. Multiboxing (running multiple clients) also works great. 

  1. # Steam

- Install Steam through the software manager
  - any distro can use this guide https://www.linuxnest.com/install-steam-on-any-linux-distro-the-complete-2025-guide/
- Open the steam app and Install EVE Online on Steam
- Right click EVE Online in steam and chose "Properties":
  - in General copy the following launcher options: PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 LD_PRELOAD= %command%
  - in Compatibility check "*Force the use of a specific Steam Play compability tool*" and chose "*Proton Experimental*"
- Launch EVE Online in steam which then starts the EVE launcher
- Open the settings of the launcher (gear icon top right):
  - in EVE Launcher disable hardware acceleration
  - in EVE Online we suggest you chose "*Download the full EVE game client*" By default not all game files are downloaded and the client can download when it does not have the file/part.  The launcher can download all files and cache them, update when needed and removes parts when no longer needed. This behaviour can be changed in the launcher and we recommend to do so in order to prevent any lag due to loading.
  - in EVE Online select DirectX version "DirectX 11"

And you are all set. Easy, right?

By standard your settings will be in /home/$USER/.steam/steam/steamapps/compatadata/8500/pfx/drive_c/users/steamuser/AppData/Local/CCP/EVE/c_ccp_eve_tq_tranquility/ and can manipulated the same as in windows if the ingame options are not enough or you want to copy settings.

Credit to cloroken who also made a very recent [video guide](https://www.youtube.com/watch?v=NFVWKN2h2-Y&t=91s)

In case you are encountering any problems, first thing to try is switching your used proton build. You can try any version that comes with steam by selecting a different version in "*Force the use of a specific Steam Play compability tool*" in the properties, or you can switch eg. to the popular Proton-GE (Glorious Eggroll). In order to do so you can eg. install ProtonPlus via the software manager which lists many Proton projects in multiple versions. Downloading and installing them in ProtonPlus makes them available in Steam after a Steam restart.

  1. # Lutris
[Lutris](https://lutris.net/) is a gaming platform for Linux. A setup with Lutris a bit more complex compared to steam but doable. It offers Wine builds that are pre-configured for specific games, and allows for a graphical installation of various games and applications. Those that are unable to roll their own wine prefix, or are weary on the process, may find this solution more viable.

Download [eve-online-1.9.4+Setup.exe](https://launcher.ccpgames.com/eve-online/release/win32/x64/eve-online-1.9.4+Setup.exe)  - stable EVE online excutable

Download [eve-online-1.9.4-full.nupkg](https://launcher.ccpgames.com/eve-online/release/win32/x64/eve-online-1.9.4-full.nupkg) - EVE Online NUPKG

One should always be careful with executables, make sure these links are (still) pointing to ccp games directly. Install Lutris via your package manager, and then ProtonPlus. Start Lutris briefly so ProtonPlus knows about it and then start ProtonPlus and chose Lutris in the top left corner. Chose Proton-GE-latest as version and download it. Now back to Lutris: 

Add a new game with the + sign: 

- add locally installed game
- General Info
  - name the game EVE Online
  - chose runner "Wine (Runs Windows games)
- Game options
  - Game executeable: link the EVE Online executable we downloaded
  - Wine prefix: /home/$USER/Games/eve-online (where $USER is your user)
- Runner options
  - Wine version: Proton-GE-latest
  - uncheck Enable Esync
  - uncheck Enable Fsync
- System options
  - add enviroment variable with KEY: LD_PRELOAD, no value
- SAVE

Now start the newly created item in Lutris and it will start the launcher asking you where to install. CLOSE THAT INSTALLATION PROCESS. DO NOT PROCEED. 

Instead, after closing right click the EVE item in Lutris and chose configure. 

Set a new path for the executable in game options: /home/$USER/Games/eve-online/drive_c/users/$USER/AppData/local/eve-online/eve-online.exe  (where $USER is your user) 

Unpack the NUPKG into a folder. Create the folder /home/$USER/Documents/EveLauncher/ and copy the content of nupkg/lib/net45 to it.  

Create the following bash script as /home/$USER/Documents/eve-prelaunch.sh <syntaxhighlight lang="bash">
1. !/bin/bash
SOURCE="$HOME/Documents/EveLauncher"
TARGET="$HOME/Games/eve-online/drive_c/users/$USER/AppData/Local/eve-online"
GOODVER="app-1.9.4"
ls -d  $TARGET/app-* | xargs rm -rf
cp -R "$SOURCE" "$TARGET/$GOODVER"
cp "$SOURCE/eve-online_ExecutionStub.exe" "$TARGET/eve-online.exe"
</syntaxhighlight>This can be done by copying the above into any text editor and save as the filename given above. Make sure the target line in here actually points to your prefix location. 

Right click the .sh file and in the properties chose 

- permissions
  - check run as executable

Back to Lutris. Right click and configure the EVE item. In system options turn on advaned mode. Scroll down to the prelaunch script and enter the /home/$USER/Documents/eve-prelaunch.sh we created. Enable wait for pre-launch script completion. Save.

Pheewww. Done!

You now be able to start the EVE launcher with the Lutris item created.

Open the settings of the launcher (gear icon top right):

- in EVE Launcher disable hardware acceleration
- in EVE Online I suggest you chose "Download the full EVE game client"
- in EVE Online select DirectX version "DirectX 11"

Credit to cloroken who also made a very recent [video guide](https://www.youtube.com/watch?v=NFVWKN2h2-Y&t=212s)

  1. # Discord Server: EVE on Linux
Join the growing community that plays on Linux. You can get eg. ditro-specific help there easily.

https://discord.com/invite/eKMEVeC7SQ

  1. # EVE on Linux Resources

- Manage GE Proton Version: <nowiki>https://davidotek.github.io/protonup-qt/</nowiki>
- Fix audio crackling/stuttering: <nowiki>https://steamcommunity.com/sharedfiles/filedetails/?id=3214697797</nowiki>
- EVE Online Linux Forum: <nowiki>https://forums.eveonline.com/c/technology-research/linux/</nowiki>
- OBS Vk Capture Plugin: <nowiki>https://github.com/nowrep/obs-vkcapture</nowiki>
- pyfa works with .appimage: <nowiki>https://github.com/pyfa-org/Pyfa/releases</nowiki>
- Hotkey Daemon (for client switching purposes): <nowiki>https://github.com/baskerville/sxhkd</nowiki>

  1. # Client slowing down / high CPU usage
Behavior like lagging is reported, a solution for this behavior is to disable **Esync** & **Fsync**. In the installation steps given above we already took care of that.

- Lutris: In the runner options disable **Esync** & **Fsync**
- Steam: Start the launcher with the launch options
<syntaxhighlight lang="bash">
PROTON_NO_ESYNC=1 PROTON_NO_FSYNC=1 LD_PRELOAD= %command%
</syntaxhighlight>

- Try switching the Proton build you are currently using
- As of now (09/2025) our recommendation is that you are using DirectX11. Its being emulated and this is just very stable by now, DirectX12 not so much. But both can work and results might differ, feel free to experiment.
>
