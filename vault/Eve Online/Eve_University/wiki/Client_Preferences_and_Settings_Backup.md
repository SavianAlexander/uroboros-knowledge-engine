---
title: "Client Preferences and Settings Backup"
url: "https://wiki.eveuniversity.org/Client_Preferences_and_Settings_Backup"
pageid: 3653
source: "EVE University Wiki"
categories: ["Applications", "Candidates for cleanup", "Guides"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Client Preferences and Settings Backup

User Settings are not stored Server Side. If you move computer or there is a client crash, preferences may be reset to default, carefully constructed **overview**s gone, the Contacts and Bookmarks organization wiped (though the actual contacts and locations remain). 

It is recommended when you are satisfied with your user settings you back them up in case you need to restore at a later date.

  1. ### How to back up Settings
To keep these settings and preferences for future use or backup, users can make a copy of the cache and settings folders. Locate the folder based on the system below. Within there you will find a <code>(c_program_files_ccp_eve_tranquility)</code> folder or something similar. Back up the contents of the folder. 

  1. ### Windows
Press  +  and paste the respective line into the Run window, then click 'OK'.

- Client settings and cache are located in:
 %LOCALAPPDATA%\CCP\EVE\

- Overview settings, screen shots, and logs are located in:
 %USERPROFILE%\Documents\EVE\

  1. ### Older Versions of Windows
- Windows XP: %USERPROFILE%\Local Settings\Application Data\CCP\EVE\
- Windows XP Steam: %USERPROFILE%\Local SettingsLocal Settings\Application Data\CCP\EVE\
- Windows Vista: %LOCALAPPDATA%\CCP\EVE\
- Windows Vista Steam: %LOCALAPPDATA%\CCP\EVE\y
- Windows Vista 64bit: %LOCALAPPDATA%\CCP\EVE\
- Windows Vista 64bit Steam: %LOCALAPPDATA%\CCP\EVE\
- Windows 7: %LOCALAPPDATA%\CCP\EVE\
- Windows 7 64bit: %LOCALAPPDATA%\CCP\EVE\
- German OS will be a variation of %USERPROFILE%\Lokale Einstellungen\Anwendungsdaten\CCP\EVE\

  1. ### Mac
- On macOS Monterey (v12.6) and newer, the location is:
MacintoshHD/Users/<username>/Library/Application Support/CCP/EVE/_users_<username>_library_application_support_eve_online_sharedcache_tq_eve.app_contents_resources_build_tranquility

- On older macOS versions, settings are stored here:
MacintoshHD/Users/<username>/Library/Application Support/EVE Online/p_drive/Local Settings/Application Data/CCP/EVE/SharedCache/wineenv/drive_c/users/<username>/Local Settings/Application Data/CCP/EVE/c_tq_tranquility/

  1. ### Linux
- Steam

- Lutris will create a wine prefix, inside this prefix the settings are stored here:
[lutris installation directory]/drive_c/users/[user]/AppData/Local/CCP/EVE/c_ccp_eve_online_tq_tranquility

The directory *settings_Default* has the settings part the client needs. 
The directory *cache* has some cached account info, mail, pictures of characters, can be large.

[lutris installation directory]/drive_c/users/[user]/Documents/EVE

1. # References
