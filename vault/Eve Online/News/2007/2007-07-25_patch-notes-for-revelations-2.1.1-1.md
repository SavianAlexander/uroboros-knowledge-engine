# Patch Notes for Revelations 2.1.1

- **Date**: 2007-07-25T00:00:00.000Z
- **Category**: patch-notes
- **Author**: CCP CAPSLOCK
- **Source**: https://www.eveonline.com/news/view/patch-notes-for-revelations-2.1.1-1
- **Tags**: #patch-notes

## Overview
Fixes and Improvements Miscellaneous The memory leak, most visible when autopilot jumping long distances, has been plugged. The game client no longer randomly crashes because of network traffic. Character portraits that normally appear in the chat window are no longer deleted from t

---

**Fixes and Improvements**

**Miscellaneous**


- The memory leak, most visible when autopilot jumping long distances, has been plugged.
- The game client no longer randomly crashes because of network traffic.
- Character portraits that normally appear in the chat window are no longer deleted from the user's cache upon starting the game client.
- Users with EVE Voice enabled will no longer suffer from the disappearance of Corporation or Alliance chat channels.
- The In Game Browser works again with IGB-compliant websites.
- Cloaking no longer spams Logserver with stacktrace errors.


**Revelations 2.1.1-1 Server-side Changes deployed 1 August**


- Optimizations to the load balancer.


**Revelations 2.1.1-2 Server-side Changes deployed 7 August**


- Further optimizations to the load balancer.


**Revelations 2.1.1-3 Server-side Changes deployed 9 August**


- Fixes for occasional proxy crashes we have been experiencing on TQ.
- Database procedure optimizations to reduce database lag and increase response time performance.
- Starbase structures in incorrect states will now be handled gracefully by the servers (note- a side effect of this is Beam Laser Batteries will appear to continue firing after being incapacitated. This is a graphic error, the batteries are not inflicting damage. This graphic error will be resolved in the future).
- The claim to sovereignty for an alliance with Constellation Sovereignty in that constellation has been increased to two downtimes.


**Revelations 2.1.1-4 Server-side Changes deployed 14 August**


- Fixing an error in Starbase sentries that would cause them to continue firing after being incapacitated.
- Fixing an issue with server startup that was causing sol nodes to fail to start.
