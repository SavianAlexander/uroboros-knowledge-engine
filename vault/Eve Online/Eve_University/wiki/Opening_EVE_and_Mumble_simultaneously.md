---
title: "Opening EVE and Mumble simultaneously"
url: "https://wiki.eveuniversity.org/Opening_EVE_and_Mumble_simultaneously"
pageid: 8512
source: "EVE University Wiki"
categories: ["Applications", "Candidates for merging", "EVE University History", "Guides"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Opening EVE and Mumble simultaneously

A step-by-step guide on how to create and setup a shortcut to open EVE Online and **Mumble** simultaneously on Windows using a batch file.

This technique can theoretically be utilized with other programs, but note that such programs may require different/additional configuration for overlays or other features to function correctly.

1. # Why should I do this?

It can be useful to not need to remember to open Mumble whenever you wish to play EVE. Also, the Mumble overlay often does not work unless Mumble is loaded *before* EVE, and a batch shortcut can preempt the need to close and reopen the EVE client to get the Mumble overlay to function correctly.

1. # Will clicking the shortcut again open more windows?

The shortcut will not open another instance of Mumble, but it will reopen the EVE launcher if it has been closed.

1. # Setup

  1. # Step 1

  - Create a separate copy of the original EVE shortcut.**

There are two reasons for this:
1. You are going to alter your shortcut. In the case where you do not want to launch Mumble as well, you will retain the original shortcut.
1. Easily copy the EVE icon for the new shortcut.

  1. # Step 2

  - Modify the shortcut.**

Right click on the shortcut and select properties,
- In the Target: field replace everything with
- In the Start in: field replace everything with
(The start in line must be set to your EVE installation, this is because the launcher outputs a debug.log file. If you do not set this is will dump the log wherever your shortcut is.)

The shortcut can also be renamed if desired.

  1. # Step 3

  - Create the batch file.**

The batch file can be placed anywhere, just remember to alter your "Target" field in the shortcut to match where you place it.

You will need to go to the folder <code>C:\Program Files\CCP\</code>, create a new text document in the folder and rename it to **Start.bat**.

Once done, right click the batch file and open it in a text editor such as Notepad.

Add the following, altering the paths to where you have EVE and Mumble installed:

@echo off
start "" "C:\Program Files\CCP\EVE\eve.exe"
start "" "C:\Program Files\Mumble\mumble.exe"

If you are using Windows 8 and your overlay does not work, you will need to add <code>nod3d9ex</code> to the end of the Mumble line like so:

@echo off
start "" "C:\Program Files\CCP\EVE\eve.exe"
start "" "C:\Program Files\Mumble\mumble.exe" -nod3d9ex

Save and close the file to finish. You can now use this new shortcut to launch both your EVE Client and Mumble at once.
