---
title: "Mumble Overlay"
url: "https://wiki.eveuniversity.org/Mumble_Overlay"
pageid: 21819
source: "EVE University Wiki"
categories: ["Applications", "Candidates for merging", "EVE University History", "Guides"]
harvested_at: "2026-08-16 23:22:28 UTC"
---

# Mumble Overlay

- [Mumble](https://www.mumble.info/)** is a third-party VOIP (Voice Over Internet Protocol) application that allows people to communicate verbally both in- and out-of-game.

1. # Mumble Overlay

The Mumble client for PC has a function included called Overlay that can show connected and/or talking voice participants.

The Overlay can give you feedback about who is connected or who is talking when the application would otherwise obscure this information, basically overlaying it over the top of your game client. Even if you have Mumble open on a second monitor, the overlay may be a useful addition as it can be positioned freely on the primary monitor. 

This is especially useful during fleet operations where you have not necessarily flown with the members previously so you may not recognize their voices yet. During high pressure PvP fights it happens often enough that someone calls out "Warp to me", so with the Overlay running you have a quick and easy way to see at a glance who that was.

  1. # Deactivating DirectX 12

Currently (as of May 2023) the Overlay does not work with DirectX 12 so the first step is to deactivate that in your EVE game client: 

1. Open your EVE launcher
1. Go to <u>*Game Client Settings*</u>
1. Remove the tick from the <u>*Run EVE with DirectX 12*</u> checkbox

  1. # Setting up the Overlay

Open your Mumble application and go to <u>*Configure*</u>, then <u>*Settings*</u> and then select <u>*Overlay*</u>:

1. The first important step is to reduce the clutter on screen so you only see who is currently talking or was talking a short while ago:
  1. Right-click one of the items on the layout screen (e.g. *Whisper*), select <u>*Filter*</u> and select <u>*Talking and recently active*</u>
  1. <u>*Always show yourself*</u> can be helpful if you want to see if you have muted yourself in Mumble (though in the interest of less clutter this is highly optional)
  1. You can also configure the time how long the recently active talkers will remain in the Overlay (appearing as greyed out names)
1. Move the position of the Overlay by dragging the red dot around (for example to the top middle of the screen)
1. Use your mousewheel to resize how large the names will appear
1. <u>*Columns*</u> gives you the possibility to choose how many names will appear in one left to right row. Depending on where on your screen you have positioned the Overlay it can be useful to have them show in only one column from top to bottom or as far left to right as possible (i.e. 5)
1. Play around with those settings to get the Overlay positioned and sized so you can at a glance get all the information you need without it obstructing crucial elements of the game itself
1. Under <u>*Edit*</u> you have further options to manipulate the different states of how people show up in the Overlay. Make certain the *Username* checkbox is ticked and again in the name of reducing clutter that *Avatar* is unchecked

Congratulations, you now have a way to see who it was who screamed "HELP! I am tackled at the gate!" or "Point! Warp to me!".

1. # Troubleshooting

- Q: The Overlay does not show up although I have done everything above.
- A: Try starting and connecting to Mumble before you start the EVE client.

- Q: It works! But now my ships look wonky!
- A: Deactivating DirectX 12 may lead to some of the ship skins not showing up correctly.  There may also be other graphic fidelity losses by deactivating DirectX 12.

- Q: I tried absolutely everything and simply cannot get the Overlay to work. :(
- A: Sadly the Overlay is quite fickle and does not work for everyone. A slightly more clunky alternative to see who is currently talking is the **Talking UI**, also directly embedded in Mumble:
  - Go to <u>*Configure*</u> and then select <u>*Talking UI*</u>. This opens up a new window which will always stay on top of other applications so you can drag it in front of your EVE client and tuck it away in a quiet corner of your screen. This window works the same as the Overlay as it will show who is currently talking.
  - Under <u>*Configure*</u>, then <u>*Settings*</u> and then <u>*User Interface*</u> there are some options for the Talking UI although they are quite barebones compared to the Overlay.

1. # References
