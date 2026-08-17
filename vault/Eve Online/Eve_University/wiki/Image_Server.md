---
title: "Image Server"
url: "https://wiki.eveuniversity.org/Image_Server"
pageid: 23530
source: "EVE University Wiki"
categories: ["Applications"]
harvested_at: "2026-08-16 23:22:27 UTC"
---

# Image Server

The image server is a web server provided by CCP hosting images of characters and items, as well as corporation and alliance logos.

It is part of a group of services like the **EVE Stable Infrastructure** and **Static Data Export** provided by **CCP** for building **Third-party tools**.

1. # Usage
The images follow a URL template of <code>https://images.evetech.net/{category}/{id}/{variation}</code>, where category, ID and variation must be replaced according to which image we want to see.

The following categories are available:
- alliances
- corporations
- characters
- types

The ID is either a alliance, corporation, character, or type ID depending on the category. See **How to get ID** for how to find the correct ID.

The variation part should either be <code>logo</code>,<code>render</code> or <code>portrait</code> depending on the exact object. The available options for each object are listed when opening <code>https://images.evetech.net/{category}/{id}/</code> (the URL of the image without the variation part).

  1. # Wiki template
The wiki has a couple of templates to assist in the use of the image server:
- - general
- - for NPC and player portraits
- - for ships, structures, deployables, drones and other objects in space.

1. # Examples
The alliance logo of **EVE University** with alliance ID 937872513 can be found here: <code>https://images.evetech.net/alliances/937872513/logo</code>.

The icon of the **Rifter** with type ID 587 can be found here: <code>https://images.evetech.net/types/587/render</code>.

1. # Known issue
While the image server claims to be able to display all types, for some more exotic items like the [Abaddon Aurora Universalis SKIN](https://everef.net/de/types/57016), the image server does not return any image (which should be located at  <code>https://images.evetech.net/types/57016/icon</code>) and fails with a HTTP error 404: Not found.

1. # Official documentation
More information about the image server can be found on the [documentation page](https://developers.eveonline.com/docs/services/image-server/).
