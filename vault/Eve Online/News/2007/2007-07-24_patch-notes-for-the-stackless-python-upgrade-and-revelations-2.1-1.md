# Patch Notes for the Stackless Python upgrade and Revelations 2.1

- **Date**: 2007-07-24T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-the-stackless-python-upgrade-and-revelations-2.1-1
- **Tags**: #patch-notes

## Overview
Similar in scope to the code change from the Bloodlines branch to the Dragon branch, EVE Online is receiving a major update to the language in which she is written. Our migration from Stackless Python 2.3 to version 2.5 is the fruition of efforts from the Python community, and CCP Games. For more

---

Similar in scope to the code change from the Bloodlines branch to the Dragon branch, EVE Online is receiving a major update to the language in which she is written. Our migration from Stackless Python 2.3 to version 2.5 is the fruition of efforts from the Python community, and CCP Games. For more of the story behind the upgrade to Stackless 2.5, please read Porkbelly's [Dev Blog](//myeve.eve-online.com/devblog.asp?a=blog&bid=488).

The result of the upgrade will be increased performance in many areas of EVE Online.

**Changes, Fixes and Improvements**

**Stackless Python**


- Stackless Python has been upgraded from version 2.3 to version 2.5.


**Desynchronization Issues**


- We've run numerous tests with fix candidates for the desync issue and have had very positive results. However, we can never fully replicate all instances of Tranquility issues on Singularity, so we ask you to report all desync issues you experience after the patch immediately through the bug-report system. We believe we have resolved the desync issue, but will continue to monitor Tranquility's performance and stability.


**Ships**


- In some circumstances, Dreadnoughts entering siege mode would cause all players in the same grid to suffer large memory leaks and eventually crash. This has been resolved.
- [Cowbell](//staff.ccpgames.com/stuart/cowbell/875.mp3)


**Starbases**


- In certain circumstances, bringing a Cynosural System Jammer would prevent the anchoring of any other structures at that starbase, nor would it be possible to take the Cynosural System Jammer offline. This has been resolved and this structure is now working as intended. NOTE: Cynosural System Jammers no longer produce system-wide beacons.


**Agents**


- Agents studying mechanical engineering returned to school for certification renewal. They have completed their studies and are accepting projects.
- Monitoring agents, as mentioned in Lingorm's [Dev Blog](//myeve.eve-online.com/devblog.asp?a=blog&bid=483), are now appearing in-space. These NPCs can be tracked, but cannot be interacted with or targeted.
- [More cowbell](//staff.ccpgames.com/stuart/cowbell/more_cowbell.wav)


**Market:**


- The required skill icon displayed when browsing items on the market was incorrectly showing skill prerequisites had not been met. This bug has been firmly whacked over the head and now displays the correct icon.
