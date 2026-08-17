---
title: "Access Lists"
url: "https://wiki.eveuniversity.org/Access_Lists"
pageid: 17696
source: "EVE University Wiki"
categories: ["User Interface"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Access Lists

- Access Lists** (**ACL**) are part of the system to control access to shared resources like **Upwell structures** and **bookmark**s.

1. # Overview
An access list controls <em>who</em> has access to a shared resource. <em>What</em> permissions are set is handled by **shared folders** for **bookmark**s and **profile**s for **Upwell structures**. An Access List has one or more members who are assigned one of the roles.

  1. # Role
Members of an access list have one of the following roles:
- Admin - Can edit and delete the list. Can add and remove members (all roles). Can assign all roles.
  - An admin <em>can</em> demote, block and remove themself.
- Manager - Can add members. Can remove members with the Member or Blocked role. Can assign the Member and Blocked role, but not to Admins or Managers.
  - A manager <em>can</em> demote, block and remove themself.
- Member - Gains the permissions that are granted to the access list. Can not see the list in their Access List window and thus can not see who its members are.
- Blocked - Is effectively for shared bookmark folders or profiles "removed" from the list. It is used to exclude an entity that is added by a "higher" entity.
The Admin and Manager roles apply only to the access list itself. The permissions set on shared folders or in profiles count as having the Member role. However, as the Admin or Manager role needed to "see" the access list only admins and managers can assign access lists to shared folders or profiles provided they have the permission/corporation-role to do so.

 button, (4) Member **search** bar]]
  1. # Member
Members of an access list can be:
- Everyone (Can only have the Member role)
- Alliances (Can not be Admin or Manager)
- Corporations (Can not be Admin or Manager)
- Capsuleers

Access lists are governed by the most granular setting available:
- Alliance supersedes "Everyone"
- Corporation supersedes Alliance
- Capsuleer supersedes Corporation.

  1. # Built-in
There is one built-in access list with one (Admin) member, the corporation the capsuleer is part of. It is named for the corporation (e.g. the one for the NPC corporation Republic University is named Republic University.) and can not be modified. So while the corporation has the Admin role (In contradiction with the rule that corporations can not be Admin or Manager) it effectively only makes the list visible and usable for all members of the corporation.

  1. # Access Lists window
Access Lists are managed through the Access Lists window. The Access Lists window can be opened
- using the **Neocom** menu: Social > Access Lists
- using the Neocom short-cut icon: Access Lists
- using a **hot-key** (There is no default)

The Access Lists window has the following components:
# List of access lists
# Access list details of the selected access list
1. * Access list name
1. * Access list description
1. * Role icon bar
1. * List of members (tab)
1. * Access list log (tab)
# Add **Everyone** button
# Member **search** bar

1. # Create
Access Lists are created through the "Create a New Access List" window which has the following fields:
- Access List Name - The name of the access list (Required)
  - This name is only a label, duplicates are accepted with no warning!
- Access List Description - A description of the access list (Optional). The description shows at the top of the member list and as a tool-tip when hovering over the list name.

To create an access list:
- open the Access Lists window
- click the  button
- enter the name (Required)
- enter the description (Optional)
- click
This will create an access list with one member, the creator, with the Admin role.

1. # Manage members
Members are managed via the **Access Lists window**. The left side of the window shows the available access lists. The right side shows the details of the selected access list. The details shown are: name of the list, description of the list, the member list, and the logs. All changes to an access list are logged. The log can be viewed by selecting the "Access List Logs" tab on the right side of the Access List window.

  1. # Add

Members are added to an access list with the Member role and can be added in several ways.

- Clicking the  button.
> Opens the Add Member window. The Add Member window has Search and All Contacts tabs and activates an  button when one or more entities are selected. Using the button adds the selected entities to the selected Access List. The Search tab only finds eligible entities. Entities can also be dragged, either into the Access List Members tab of the selected Access List or on top of an access list name, adding the selected entities to that list.
- Using the Add Members option accessed by right-clicking the Access List name or by clicking the hamburger in the top right.
> Opens the **Contacts** window. The Contacts window has Contacts, Agents and Search tabs. The Agents tab is irrelevant as agents can not be members of an access list. The Search tab, by default, finds all types of entities but can be configured to only search characters or corporations etc. The Contacts window only supports dragging entities into the Access List Members tab of the selected access list or on top of an access list name, adding the selected entities to that list.

- Besides these methods, members can be added to an access list by dragging them from:
  - a chat channel or chat channel member list.
  - the Guests list in a station or player structure
  - the portrait/icon from an info window

- Members can also be copied from one access list to another by dragging them on top of an access list name.  This also copies the role.

  1. ## Everyone
Everyone can only be added in one way. Clicking on the globe icon on the bottom right of the member list, adds everyone to the selected access list.

  1. # Change role
A member's role can be changed in several ways. Multiple members can be selected to change in one go.

- Drag members to the role icon bar on top of the member list
- Use the options in the member menu. This menu can be activated by right-clicking the member name or by clicking the hamburger in the top right.
  - The menu shows only applicable options - The possible options are:
    - Block Member
    - Unblock Member
    - Make Admin
    - Make Manager
    - Strangely enough, there is no option "Make Member". This is done by the options "Remove Admin Role" and "Remove Manager Role".
  - Corporations and alliances can not be blocked or unblocked via the menu they must be dragged to the role icon bar.

  1. # Remove
Members can be removed from an access list by the "Remove Member" option of the member menu. This menu can be activated by right-clicking the member name or by clicking the hamburger in the top right.

  1. # Search

The **Access Lists window** has a search function (top-right of the window). The function acts as a filter. It limits the visible list members to those that match the filter. It also grays out Access Lists, which have no members that match the filter. The function is not dynamic, it requires hitting the  key or clicking on the magnifying glass to activate.

Note: The entry field can be hidden. To make it visible again click on the magnifying glass or the << marker to the left of it.

1. # Edit
An access list can be edited (name and description), through the option "Edit Access List" in the Access List menu. This menu can be activated by right-clicking the Access List name or by clicking the hamburger in the top right.

1. # Delete
An access list can be deleted through the option "Delete Access List" in the Access List menu. This menu can be activated by right-clicking the Access List name or by clicking the hamburger in the top right.

1. # Publish
Access lists can be "published" by dragging them into chat, a chat channel's MOTD, EVEmail, a character's biography, or a corporation/alliance's description, creating a link. Clicking on the link opens a window that shows the Access List's name, description and the Admin(s), but not the Managers. This information is not dynamic i.e. it is a snapshot of the information as is on the creation of the link.

1. # See also
- EVE Support: [Access Lists](https://support.eveonline.com/hc/en-us/articles/208289645-Access-Lists)

1. # Notes
