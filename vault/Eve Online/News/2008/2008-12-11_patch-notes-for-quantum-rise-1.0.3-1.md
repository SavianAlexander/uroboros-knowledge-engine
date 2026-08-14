# Patch Notes for Quantum Rise 1.0.3

- **Date**: 2008-12-11T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-quantum-rise-1.0.3-1
- **Tags**: #patch-notes

## Overview
Patch notes for Quantum Rise 1.0.3, released 11 December 2008   Table of Contents CRITICAL CHANGES FIXES CRITICAL We are changing the way the patcher behaves. Previously, if the patcher encountered locked files while patching it would suggest that you reboot to complete the

---

**Patch notes for Quantum Rise 1.0.3, released 11 December 2008**

**Table of Contents**

[CRITICAL](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=178#critical)

[CHANGES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=178#changes)

[FIXES](//myeve.eve-online.com/updates/patchnotes.asp?patchlogID=178#fixes)

**CRITICAL**


- We are changing the way the patcher behaves. Previously, if the patcher encountered locked files while patching it would suggest that you reboot to complete the patching (but allow you to cancel the reboot, in case you wanted to do something else before rebooting). Now it insists on a reboot before you continue. People will still have the option to close other programs before pressing the OK button to start the reboot. There were problems with locked files, reboot requests and Vista. That has now been fixed and should work normally on both XP and Vista.
- The client will now check files and folders before starting the patching process. Previously, if it found extra files it would automatically move them to a temporary folder before continuing. Now it will suggest rebooting to complete patching (because these might be patch files for a pending reboot) or suggest that you should manually remove the extra files.


**CHANGES**

**Need for Speed**


- In our continuing efforts to improve fleet fights, we have made various improvements that have resulted in a much better overall performance. CCP Atlas details these changes in [The EVE Client - A Love Story](//myeve.eve-online.com/devblog.asp?a=blog&bid=613).
- We have made various performance improvements to UI rendering in the graphics engine.
- Turrets and turret effects now work in the same way for both the Classic and Premium clients. A turret is no longer loaded into a scene unless it is either fired at you or you are “looking at” the owner’s ship. Now, iff you disable turret effects you will only see the turret models of your own ship or any ship that you are explicitly look at. This reduces the loading time of scenes with a large number of turret ships substantially and increases the framerate per second on such scenes dramatically in Premium but has no effect on the Classic client. If you disable turrets, any turret model that is already in the scene will continue to be there. However, warping away and back again will clean out turret models.
- Sentry gun turrets will also behave in the same manner as ship turrets. They will not appear unless you are looking at them or unless they are firing on you.
- Drone models can now be disabled. Disabling the models has an incredible impact in loading up heavy scenes on both the Classic and Premium clients. The impact on the framerate per second once the scene is loaded will only be measurable if your camera is zoomed in far enough for the drones to resolve into models. When drone models are set to disabled then the turrets are automatically also set to disabled.
- You can now disable camera shaking which both disables camera shake when missiles hit and when you're in warp.
- You can now disable ship explosions. Ship explosions had the ability to add heavy load in major fleet engagements and can now be completely turned off.
- Tactical notifications can now be disabled. Warp scrambling messages and self destruct are two examples of these notifications. Please note that these notifications will still display if it is your ship which is being affected.
- We have added a new option called “Hide all brackets” which is the inverse of the existing “Show all brackets” and will function in the same way. The two options are mutually exclusive so activating one will disable the other. This is a new and easier way to disable brackets.


**Graphics General**


- We discovered that certain memory re-allocation behavior gave bad performance on Windows XP. We switched from regular memory heaps to low fragmentation heaps, which gave a tremendous boost to model loading on Windows XP. This change had no effect on Windows Vista, but the behavior on Vista both before and after is much better than on XP. Players who use Windows 2000 as an operating system must upgrade to Service Pack 4 (SP4) in order to connect to Tranquility since low fragmentation heaps are only available in Windows 2000 SP4 and above. It should also be noted that we no longer officially provide support for Windows 2000. The only supported operating systems for Windows are XP and Vista.
- Bracket loading in heavy scenes has been substantially improved.


**FIXES**

**Graphics General**


- A memory leak has been identified and fixed resulting in a much smoother performance overall.
- Under certain conditions the graphics engine would find objects that did not exist in the scene anymore. This has now been fixed and will no longer result in performance degradation.
- Found and fixed an issue where the graphics engine DLL could not be loaded on certain older hardware


**Miscellaneous**


- An error will no longer be generated when jumping between two clones which both have implants.


**Exploit Fixes**


- Several exploits have been fixed making New Eden a better place for everyone.
