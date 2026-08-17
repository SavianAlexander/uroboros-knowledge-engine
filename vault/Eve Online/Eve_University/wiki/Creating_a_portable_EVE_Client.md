---
title: "Creating a portable EVE Client"
url: "https://wiki.eveuniversity.org/Creating_a_portable_EVE_Client"
pageid: 17770
source: "EVE University Wiki"
categories: ["Applications", "Guides"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Creating a portable EVE Client

Having a portable version of your EVE Client with all accounts logged in and ready to play, can give you a time-efficient and bandwidth-saving advantage. Whether you are traveling or do not want to leave traces of your computer activity, or just like to have an "EVE To Go" on a portable medium of your choice, this tutorial might be for you.

1. # Hardware

- EVE Online requires 20GB, often more, so it is strongly recommended to have at least 32GB free space on your storage device.
- It is strongly discouraged to use a USB 2.0 interface for playing EVE via pen drive because load times and overall performance drops to almost unplayable.
- Use a USB 3.0 or better interface for outstanding performance that allows you to play stable 60fps on full details (of course other hardware requirements must be met).
- Proper drivers (graphics card drivers, DirectX 11) must be installed on the machine. Without them, the game will not start.
- System Requirements are published at https://support.eveonline.com/hc/en-us/articles/5885219196828-System-Requirements

1. # First installation

Legend (recommended names for easiness of explanation. You can name all things however you like):
- C: - your computer system's drive letter
- X: - your pen-drive's drive letter
- .user. - your username

# Navigate to your plugged-in disk and create a directory to store all your EVE data, for example, "EVE Online".
# Inside the newly-created directory, create folders called "Documents", "Local" and "EVE".
# Open EVELauncher installer from [eveonline.com/download](https://www.eveonline.com/download).
# Select the installation location as your newly created "EVE" folder and install EVE.
# Do not forget to delete the desktop shortcut and start the menu entry in "C:\Users\.user.\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
# When your launcher is downloading data, make sure to set the SharedCache folder inside "X:\EVE Online\EVE\EVESharedCache" folder.
# Navigate to "C:\Users\.user.\AppData\Local\eve-online". This folder is hidden, and can be found by Win-R and entering the command "%appdata%". The "Local" folders can be found by navigating to "AppData" and opening "Local". The "eve-online" folder contains the actual EVE Launcher application. Move the entire folder from "C:\Users\steph\AppData\Local\eve-online" to "X:\EVE Online"
# This step is optional but can make a difference in terms of game client performance. In the EVE Launcher, selecting "Download full game client" will have the computer download the entire game library into the drive. This will result in better game performance, as the client will not be downloading game files while you are playing. 
# Log into all accounts you want to save for your portable client.
# After all data is downloaded, exit EVE Launcher (make sure it was not just minimized into the system tray).

Now, there are two different approaches you can choose. One is manual, and the second is more automated but requires a minimum knowledge of Windows

  1. # Manual
Navigate to "C:\Users\.user.\Documents" and cut the folder named "EVE" and paste it into "X:\EVE Online\Documents"
Navigate to "C:\Users\.user.\AppData\Local" (this is a hidden folder) and cut the folder named "CCP" and paste it to "X:\EVE Online\Local"

  1. # Automatic
WARNING, ONLY FOR PEOPLE WHO UNDERSTAND XCOPY AND RD COMMANDS
# In "X:\EVE Online" create a text file named "clean.txt" and paste the code below:xcopy /E "%userprofile%\Documents\EVE" "Documents\EVE"  /Yxcopy /E "%userprofile%\AppData\Local\CCP" "Local\CCP"  /Yrd /S /Q "%userprofile%\Documents\EVE"rd /S /Q "%userprofile%\AppData\Local\CCP"
# After saving the file, change the extension from ".txt" to ".bat". This is done by saving the .txt file as "clean.bat" in the Windows dialogue with the file type set to "All Files."
# Run the script.

Voila! you have portable EVE Online!

1. # Launching the game on a new computer

# Plug in your portable EVE to a new device
# Make sure the drive letter is "X:". If not, change it in Win+X -> "Disk Management"

Now, there are two different approaches you can choose. One is manual, and the second is more automated but requires a minimum knowledge of Windows

  1. # Manual
Navigate to "X:\EVE Online\Documents" and copy the folder named "EVE" and paste it into "C:\Users\.user.\Documents"
Navigate to "X:\EVE Online\Local" and copy the folder named "CCP" and paste it to "C:\Users\.user.\AppData\Local" (this is a hidden folder)

  1. # Automatic
WARNING, ONLY FOR PEOPLE WHO UNDERSTAND XCOPY AND RD COMMANDS
# In "X:\EVE Online" create a text file named "startup.txt" and paste the code below:
xcopy /E "Documents" "%userprofile%\Documents\" /Yxcopy /E "Local" "%userprofile%\AppData\Local\" /Y
# After saving the file, change the extension from ".txt" to ".bat".
# Run the script.

Now you can launch the game and play instantly with all your accounts logged in and all user settings saved.

1. # Cleaning the computer after playing

# Exit the game and close the launcher(make sure it does not still run in the system tray)
# Run "clean.bat"
# If you want to clear more traces of EVE running, navigate to "C:\Users\.user.\AppData\Roaming\Microsoft\Windows\Recent" and remove all EVE-related shortcuts.
# Disconnect your device.
