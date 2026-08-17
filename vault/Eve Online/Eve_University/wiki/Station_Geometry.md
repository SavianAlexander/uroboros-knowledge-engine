---
title: "Station Geometry"
url: "https://wiki.eveuniversity.org/Station_Geometry"
pageid: 2540
source: "EVE University Wiki"
categories: ["Candidates for verification", "Game mechanics", "Needing updates", "Structures"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Station Geometry

This article aims to provide geometry data on dockable stations in EVE Online for players who have difficulty making use of the CCP Data Dump. Each station has a "type" which may be seen by using SHOW INFO on the station in question and then viewing the 3-D model. The station type also appears in the Type column of the Overview while in space in the same solar system as the station. For all stations of the same type: the point where undocking ships spawn is in the same location relative to the center of the station (X0, Y0, and Z0 in meters); the direction in which undocking ships initially move is a random distribution centered on a given vector (Vx, Vy, Vz in dimensionless units); and the radius of the station is a fixed value.

Locations in a solar system are stored internally in EVE Online as XYZ coordinates in units of meters. Taking the upwards direction on the Solar System Mapbrowser (by default ; this is the Mapbrowser, not the Map) as north, then +X is West, +Y is above the ecliptic plane, and +Z is South. A player ship's current location in this coordinate system (provided that the ship is not moving) may be viewed in **NeoCom** > Locations > ADD BOOKMARK.

Coordinates for stations and undock statistics are taken from the **Static Data Export**.

Station radii are taken from http://games.chruker.dk/eve_online/inventory.php?group_id=15 but there is reason to believe that these radii are incorrect. Player-measured values are given where available. For values where the measured radius is available, the "Undock Distance" is also provided and is defined as the distance an undocking ship has to travel along the original undock vector to reach the zero-meter sphere of the station. The shorter the Undock Distance, the easier it is for a ship to drift (or be bumped) outside of docking range before the 30-second session change timer elapses.

Station geometry size also affects **grid size**.

| Station Type | X0 | Y0 | Z0 | Vx | Vy | Vz | Chruker Radius | Measured Radius | Undock Distance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Amarr Industrial Station | 0.00 | -21316.45 | 0.00 | 0 | -1.000000119 | 0 | 24276 | 22830 | 1514 |
| Amarr Mining Station | -10709.00 | -9721.00 | -2069.00 | 0 | -1 | 0 | 22283 |  |  |
| Amarr Research Station | -13.00 | -5689.27 | 0.00 | 0 | -0.99999994 | 0 | 29162 |  |  |
| Amarr Standard Station | 199.79 | -12936.94 | 51.99 | 0 | -1 | 0 | 20081 |  |  |
| Amarr Station Hub | 0.00 | 11158.47 | 0.00 | 0 | 0.99999994 | 0 | 42489 |  |  |
| Amarr Station Hub (Damaged) | 0.00 | 11158.47 | 0.00 | 0 | 0.99999994 | 0 | 42489 |  |  |
| Amarr Station Military | 0.00 | -21987.53 | 0.00 | 0 | -0.99999994 | 0 | 48492 |  |  |
| Amarr Station Military (Damaged) | 0.00 | -21946.96 | 0.00 | 0 | -1 | 0 | 48532 |  |  |
| Amarr Trade Post | -1749.89 | -9967.83 | 27.00 | 0 | -1 | 0 | 13887 |  |  |
| Amarr Trade Post (Damaged) | -1749.89 | -9967.83 | 27.00 | 0 | -1 | 0 | 13887 |  |  |
| Caldari Food Processing Plant Station | -33431.21 | -2574.00 | 2477.00 | -1 | -1.19E-07 | 0 | 55741 |  |  |
| Caldari Mining Station | -27844.55 | -1354.31 | 2399.00 | -1 | 5.96E-08 | 0 | 47854 |  |  |
| CONCORD Starbase | -3152.71 | -39840.25 | -8244.80 | -2.19E-06 | -5.39E-05 | -1 | 60432 |  |  |
| Jovian Construct | -1203.00 | -18300.00 | 5400.00 | 0 | -4616 | 0 | 47270 |  |  |
| Minmatar Hub | -2909.00 | -1437.88 | 20657.00 | 0 | 5.96E-08 | 1 | 33811 |  |  |
| Minmatar Industrial Station | 6299.00 | 2654.04 | -11165.65 | 0 | 0.006261647 | -0.99998045 | 27681 |  |  |
| Minmatar Military Station | 30416.31 | -1172.00 | 3099.96 | 0.99999994 | 5.96E-08 | 0 | 36902 |  |  |
| Minmatar Mining Station | 11903.65 | 8452.42 | -9744.42 | 0.99998045 | 0.006261468 | 0 | 30592 |  |  |
| Minmatar Research Station | 1390.30 | 27.00 | 28047.04 | 0.031338226 | 0.00616767 | 0.999489784 | 33481 |  |  |
| Minmatar Station | 17.00 | 3115.00 | 18255.20 | 0 | 5.96E-08 | 1 | 19714 |  |  |
| Minmatar Trade Post | 17.00 | 10096.00 | 12607.21 | 0 | 5.96E-08 | 1 | 15733 |  |  |
| Station (Caldari 1 Wrecked) | 875.93 | 4958.73 | -1991.93 | 0.921267271 | 0.122105479 | 0.369265169 | 52868 |  |  |
| Station (Caldari 1) | -170.00 | 3217.00 | -12112.15 | 0 | 5.96E-08 | -0.99999994 | 45734 |  |  |
| Station (Caldari 2) | 11384.43 | 7499.13 | -270.25 | 0.981180847 | 0.193091094 | 1.38E-08 | 26782 |  |  |
| Station (Caldari 3) | 2447.21 | -3841.00 | -2988.00 | 0.951056123 | 0.309018254 | 0 | 33413 |  |  |
| Station (Caldari 4) | 36.00 | 6854.26 | -7948.47 | 0 | 5.96E-08 | -1 | 15351 |  |  |
| Station ( Caldari 5 ) | 123.39 | -4043.97 | 17010.32 | -2.32E-06 | -0.239630699 | 0.970864117 | 24657 |  |  |
| Station ( Caldari 6 ) | -28557.87 | -1158.93 | 2436.08 | -1 | 5.96E-08 | 0 | 47854 |  |  |
| Station (Gallente 1) | 0.00 | -5000.00 | 4800.00 | 0 | -1 | 0 | 23386 |  |  |
| Station (Gallente 2) | 0.00 | 6143.53 | -3100.01 | 1.07E-05 | 0.107010782 | 0.994257867 | 27072 | 32533 | 34314 |
| Station ( Gallente 3 ) | -1004.37 | 4872.75 | 5903.60 | 0.35010922 | 6.31E-06 | 0.936708868 | 45151 |  |  |
| Station ( Gallente 4 ) | 9264.68 | 884.00 | 0.00 | 0.99999994 | 5.96E-08 | 0 | 24871 |  |  |
| Station ( Gallente 5 ) | 7933.67 | 208.24 | -18212.35 | 0.280802876 | -0.008255527 | -0.95972997 | 29746 | 24874 | 5040 |
| Station ( Gallente 6 ) | 9956.19 | 1058.91 | 0.00 | 0.999796927 | 0.020150529 | 0 | 17876 |  |  |
| Station ( Gallente 7 ) | 10679.88 | 1006.77 | 14350.24 | 0.999426365 | 0.033865333 | 8.08E-09 | 37560 |  |  |
| Station ( Gallente 8 ) | 9788.61 | 938.00 | 0.00 | 0.999713182 | -0.01204008 | 0.020701097 | 28083 |  |  |
