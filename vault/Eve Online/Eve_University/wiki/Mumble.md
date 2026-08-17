---
title: "Mumble"
url: "https://wiki.eveuniversity.org/Mumble"
pageid: 2919
source: "EVE University Wiki"
categories: ["Applications", "EVE University History", "EVE University Services", "Getting Started"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Mumble

- [Mumble](https://www.mumble.info/)** is a third-party VOIP (Voice Over Internet Protocol) application that allows people to communicate verbally both in- and out-of-game.

Our Mumble authentication for Members and Guests is handled through Alliance Auth.  

1. # Accessing Mumble
Navigate to https://auth.eveuniversity.org/ and sign in using EVE Online SSO - For access to base systems you will only be asked for public scopes:
# Select Services from the toolbar on the left hand side of the screen
# Select the amber tick at the end of the mumble row and you will see your username and password
# Select continue
# Click on the Green arrow *Connect* button to automatically connect to Mumble
# Enter your Mumble password if prompted

After you've successfully connected, you can easily save the server settings in your Mumble Desktop client to reconnect easily in the future.

  - Using the Mumble Desktop Client:**
# Click on *Server* > *Connect* > *Add New*
# Click on the *Fill* button to automatically fill in the server details
# You can modify the Label to anything you like, or just leave it as the default

  - If you are still having problems getting connected, try following the **manual instructions** below setup the connection.**

  1. # Manual connection instructions
After setting up your Mumble account through Alliance Auth in the steps above. You can try using these steps to setup a connection to the **EVE University Mumble** server if the Green **Connect** button isn't working for you.

  - Using the Mumble Desktop Client:**
# Click on *Server* > *Connect* > *Add New*
# Enter the **EVE University Mumble** details below then click *OK*
# Select *EVE University Mumble* in the list then click *Connect*

| EVE University Mumble |
| :--- |
| Address |
| Port |
| Username |
| Password (only when prompted) |
| Label |

Your Alliance Auth username is normally your character name with spaces replaced by underscores. (i.e. Example Member is Example_Member) If you're uncertain, you can see your current username for Mumble on the Alliance Auth [Services](https://auth.eveuniversity.org/services) page.

If you cannot remember your Mumble password, go back to the [Services](https://auth.eveuniversity.org/services) page where you can set a new password using the amber pencil icon or create a new random password using the gray refresh, or circular arrows, icon.

If you're still unable to connect to our Mumble server after trying these steps, feel free to reach out for support in **#alliance-auth** channel on the **EVE University Discord**.

1. # Initial configuration
  1. # Push to talk
There is nothing more annoying than hearing other people type or breathe into their microphone constantly. If you leave push-to-talk off during a fleet op then you are likely to have some very frustrated Corp mates. This is why push to talk is mandatory. To turn on push to talk for Mumble, follow these steps.
# Open up Mumble
# Click the “Configure” option at the top, then click settings
# You should now be in the Audio Input settings area, under the Transmission area make sure the Transmit drop down box is set to “Push to Talk”
# Now you need to assign a key that you will need to press so others can hear you. To do this click the “Shortcuts” button on the left hand side of the Settings dialog box.
# There should be a listing there labeled “Push-to-Talk”, click on the Shortcut column and press the key that you wish to be your push to talk key.

  1. # Whisper key
Some of our mumble rooms, most notably the fleet and general lounge channels are linked to other channels. The purpose of these sub channels is to give the group within the option to talk to each other without all of the linked channels being able to hear it. 

For example the commander of the logistics group can now talk to only the Logistic pilots without confusing everyone else.

A whisper key allows you to talk to just your current channel instead of broadcasting your voice to all of the linked channels.

You should already see your existing push-to-talk key set up.  It's a good idea to check the Suppress box on any shortcuts, as that will prevent other applications from recognizing your key and performing unforeseen tasks you had not expected (e.g. warp scrambling stargates).  

  1. ## Setting up your whisper key
# Click the Add button in the bottom left, which will bring up a new Unassigned shortcut in the window.
# Click the word Unassigned and select Whisper/Shout from the drop-down list.
# Click the word Empty next to it, which should cause a [...] button to appear next to that - click that [...] button to open a new Whisper Target window.
# Select the Shout to Channel box, and check that “Current channel” is highlighted, and then click OK. 
# Finally click the Shortcut column of your new shortcut and press the key you wish to use.

You now have your Whisper chat key setup!

By default you should always use a Whisper Key to chat in EVE University Mumble channels.

  1. # Notifications
Go to Configure > Settings... > Messages. From there you can disable popup and sound notifications about events you don't care about.  By default Mumble makes a loud PING and gives you a notification popup for almost any event on the server - this gets annoying pretty fast.

Mac version: From the Mumble --> Preferences window (make sure the 'Advanced' checkbox in the upper right is checked), select the 'Messages' tab. The only way to eliminate audio notifications is to uncheck items in the 'Soundfile' column.

  1. # Overlay
It can be useful to have the Mumble Overlay set up for fleet operations as it eliminates the need for checking the Mumble client to see who is talking. See the **Mumble Overlay** for a step-by-step guide.

1. # Chat policies
Please remember that our **Communications Policy** applies in the Uni Mumble. Moderation can include muting and/or banning. Note that this can severely affect your participation in fleets, classes, and other activities.

1. # Channel rules & access
Mumble is currently set up in the following configuration:
- **General Lounges** - Two channels,  one for members and one for the public.  A general hangout space for everyone
- **Classrooms** - Open to everyone who joins mumble and used by the Teachers to run classes
- **Public Fleets** - Open to everyone for public roams and fleets (EVE Uni Comms Policy still applies)
- **Uni Fleets** - Restricted to Uni Members for Uni only roams/fleets or QRF’s
- **Standing Fleets** - Be in standing fleet and in here if your just hanging out around our staging areas
- **Special Interest Groups** - Rooms to allow members to connect your content and interests no matter which area of space the operate in
- **On Demand Channels** - Anyone in EVE Uni can create temporary channels here if there is no suitable channel for their needs.
- **Staff Offices** - Restricted to EVE University Officers and Management
- **AFK & Idle Room** - If you're muting your speakers anyways, idle here

1. # Moderation
Any of our officers, managers or directors are able to moderate our mumble server.

1. # Note for MacOS users
When updating or reinstalling Mumble on MacOS, it is necessary to go into System Preferences > Privacy & Security > Privacy

For BOTH the "Accessibility" AND "Input Monitoring" lists: Remove Mumble from the list, then re-add Mumble to the list by clicking-and-dragging the NEW Mumble application from the "Applications" folder to the list.

If installing Mumble for the first time ever (on a given Macintosh), then just add Mumble to these two lists.

Forgetting to do this when installing, reinstalling, or updating Mumble will result in Mumble being unable to detect keyboard inputs for Push-To-Talk and Whisper/Shout features.

  1. # Warning
Do <em>NOT</em> upgrade from mumble <=1.3.x to 1.5.x+. If you accidentally did upgrade, follow these steps to recover:
# When referring to delete, that is dragging app, file or folder icon to trash can or using Command-Delete
# Delete Mumble app by going to your Applications folder
# Reveal hidden directories by going to Finder, open up your Macintosh HD folder. Press Command+Shift+Dot
# Delete mumble database directory: <code>$HOME/Library/Application Support/Mumble/</code>
</references>
