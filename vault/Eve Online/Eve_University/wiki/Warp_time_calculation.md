---
title: "Warp time calculation"
url: "https://wiki.eveuniversity.org/Warp_time_calculation"
pageid: 10976
source: "EVE University Wiki"
categories: ["Candidates for merging", "Game mechanics"]
harvested_at: "2026-08-16 23:22:29 UTC"
---

# Warp time calculation

This page explains the calculations for the amount of time taken to travel while warping. Please note, this does not cover the time spent getting in to warp (accelerating to 75% maximum velocity), or the time spent slowing down after you regain control of your ship.

1. # Time taken to warp

It is possible to work out how long it should take for a ship to complete warp (once it enters warp) based on formulae released by CCP.

Warp consists of 3 stages:
# Acceleration
# Cruising
# Deceleration

Calculating the time taken to warp is done by calculating the time spent in each of these phases and adding them together. This requires calculating acceleration and deceleration time first, followed by cruise time.

Total time in warp is given by:

> <math> t_{total} = t_{accel} + t_{cruise} + t_{decel} </math>

# Long warps
A "long warp" is any warp where there is time to reach maximum warp speed before having to start decelerating.

1. # Acceleration

  1. # The formulae
CCP provided formulae for both distance traveled and velocity reached after *t* seconds of acceleration. If *d* is distance in meters, *v* is speed in meters per second, *k* is a (sort of) constant defined as the warp speed (in AU/s) and a = 149,597,870,700 meters (1 AU).

> <math>
\begin{align}
d & = e^{kt} \\
v & = k*e^{kt}\\
v_{warp} & = k * a\\
\end{align}
</math>

  1. # Distance
To calculate distance traveled while accelerating

> <math>
\begin{align}
d & = e^{kt} \\
v & = k*e^{kt}\\
& = k*d\\
\therefore d & = \frac{v}{k}
\end{align}
</math>

The distance covered while accelerating to v<sub>warp</sub> is 

> <math>
\begin{align}
d_{accel} & = \frac{v_{warp}}{k}
& = \frac{k*a}{k}
& = a
\end{align}
</math>

This means that every ship covers exactly 1 AU while accelerating to its maximum warp speed.

  1. # Time
To calculate the time spent accelerating to warp speed, the equation for *v* should be rearranged to be in terms of *t*, and then solved for the case of *v* being equal to the warp speed (in m/s)

> <math>
\begin{align}
v & = k*e^{kt}\\
\frac{v}{k} & = e^{kt}\\
kt & = \ln{(\frac{v}{k})}\\
t & =\frac{\ln{(\frac{v}{k})}}{k}\\
\end{align}
</math>

We want to find the time taken to maximum warp:

> <math>
\begin{align}
v_{warp} & = k * a\\
t_{accel} & = \frac{\ln{(\frac{v_{warp}}{k})}}{k}\\
\end{align}
</math>

This formula can be simplified further to <math>\frac{\ln{a}}{k}</math>, although you may choose not to do this for implementation reasons. Because <math>a</math> is a constant, if warp distance is long enough for a ship to reach full speed, the warp acceleration time can be simplified down to

> <math>
t_{accel} \approx \frac{25.7312}{k}
</math>

1. # Deceleration
Deceleration is calculated slightly differently. Instead of using *k* to calculate distance and velocity, it uses *j*, which is defined as <math>\min(\frac{k}{3},2)</math>. A different rate of deceleration is used to prevent ships suddenly transitioning from "many, many AU away" to "on grid and out of warp" more rapidly than other pilots (or the server / client) can keep up with.

There is a complication with deceleration calculations. Ships do not drop out of warp at 0 m/s. Instead, they drop out of warp at *s* m/s, after which normal sub-warp calculations take over.

> <math>s = \min(100, v_{subwarp}/2)</math>

Where v<sub>subwarp</sub> is the maximum subwarp velocity of the ship; this varies greatly depending on the ship hull and pilot skills.

  1. # Distance
This changes the formulae used slightly. Remember that distance travelled is the integral of velocity.

> <math>
\begin{align}
v & = k * e^{jt}\\
d & = \int_{0}^{\infty}k*e^{jt}\,dt = \frac{k*e^{jt}}{j}\\
 & = \frac{v}{j}
\end{align}
</math>

The distance covered while decelerating from v<sub>warp</sub> is

> <math>
\begin{align}
d_{decel} & = \frac{v_{warp}}{j}
= \frac{k*a}{j}
\end{align}
</math>

Note that for ships that travel at up to 6 AU/s, k / j  = k / (k/3) = 3, so these ships cover 3 AU while decelerating. The complication of not stopping warp at 0 can be safely ignored for distance calculations, because the distance that would be covered while decelerating from 100 m/s is insignificant compared to the ~450 billion meters it takes to decelerate from warp speed to warp drop speed.

  1. # Time
As with acceleration, time to decelerate from maximum warp velocity is worked out by rearranging the velocity equation.

> <math>
\begin{align}
v &= k*e^{jt}\\
\frac{v}{k} & = e ^ {jt}\\
t & = \frac{\ln{(\frac{v}{k})}}{j}
\end{align}
</math>

While the deceleration from *s* to 0 was insignificant in terms of distance, it is significant in terms of time. This means that the time to decelerate is calculated as follows:

> <math>
\begin{align}
t_{decel} & = t_{decel\_warp} - t_{decel\_s}\\
& = \frac{\ln{(\frac{v_{warp}}{k})}}{j} - \frac{\ln{(\frac{s}{k})}}{j}\\
& = \frac{\ln{(\frac{v_{warp}}{k})} - \ln{(\frac{s}{k})}}{j}\\
& = \frac{\ln{v_{warp}} - \ln{k} - \ln{s} + \ln{k}}{j}\\
& = \frac{\ln{v_{warp}} - \ln{s}}{j}\\
& = \frac{\ln{(\frac{v_{warp}}{s})}}{j}
\end{align}
</math>

1. # Cruising

  1. # Distance
The distance covered while cruising is the total warp distance minus any distance covered while accelerating or decelerating.

> <math>d_{cruise} = d_{total} - d_{accel} - d_{decel}</math>

For all but the fastest ships, this will be *d<sub>total</sub> - 4 AU*.

  1. # Time
This one is easy. Time spent cruising is simply 

> <math>t_{cruise} = \frac{d_{cruise}}{v_{warp}}</math>

# Short Warps
The above calculations work as long as some time is spent at maximum warp speed; <math>d_{total} \geq d_{accel} + d_{decel}</math>. If the warp is short enough that the ship never reaches top speed, a different set of calculations are needed.

> <math>
\begin{align}
d_{accel} & = \frac{v_{max}}{k}, d_{decel} = \frac{v_{max}}{j}\\
d_{total} & = d_{accel} + d_{decel} = v_{max}(\frac{1}{k} + \frac{1}{j})\\
v_{max} & = \frac{d_{total}*k*j}{k + j}
\end{align}
</math>

This enables the calculation of new acceleration and deceleration times using the formulae described in the previous sections, but substituting in the new v<sub>max</sub>

> <math>
\begin{align}
t_{accel} & = \frac{\ln{(\frac{v_{max}}{k})}}{k}\\
t_{decel} & = \frac{\ln{(\frac{v_{max}}{s})}}{j}\\
t_{total} & = t_{accel} + t_{decel}
\end{align}
</math>

# Implementation

The following python 3 code is one possible implementation of the above. It attempts to generate the same data as presented by CCP in the forums. It matches with their numbers, except for 50 AU titan warps, which are one second out. Note that the sub warp speed of the ship is fixed at 200 m/s. This is because the CCP-produced tables assume that every ship drops out of warp at 100 m/s. If trying to run calculations for actual ships, this value will need to be replaced with a more appropriate one. The output values are also passed through the ceil() function, as this is what seems to match the rounding mode that CCP used.

import math
AU_IN_M=149597870700

def get_distance(dist):
    if dist > 1e9:
        return (dist / AU_IN_M, "AU")
    else:
        return (dist/1000, "KM")

# Warp speed in AU/s, subwarp speed in m/s, distance in m
def calculate_time_in_warp(max_warp_speed, max_subwarp_speed, warp_dist):

    k_accel = max_warp_speed
    k_decel = min(max_warp_speed / 3, 2)

    warp_dropout_speed = min(max_subwarp_speed / 2, 100)
    max_ms_warp_speed = max_warp_speed * AU_IN_M

    accel_dist = AU_IN_M
    decel_dist = max_ms_warp_speed / k_decel

    minimum_dist = accel_dist + decel_dist

    cruise_time = 0

    if minimum_dist > warp_dist:
        max_ms_warp_speed = warp_dist * k_accel * k_decel / (k_accel + k_decel)
    else:
        cruise_time = (warp_dist - minimum_dist) / max_ms_warp_speed

    accel_time = math.log(max_ms_warp_speed / k_accel) / k_accel
    decel_time = math.log(max_ms_warp_speed / warp_dropout_speed) / k_decel

    total_time = cruise_time + accel_time + decel_time
    distance = get_distance(warp_dist)
    return total_time

distances = [150e3, 1e9, AU_IN_M * 1, AU_IN_M * 2, AU_IN_M * 5, AU_IN_M * 10, AU_IN_M * 20, AU_IN_M * 50, AU_IN_M * 100, AU_IN_M * 200]
speeds = [1.36, 1.5, 2, 2.2, 2.5, 2.75, 3, 3.3, 4.5, 5, 5.5, 6, 8]

result = {}
for speed in speeds:
    for dist in distances:
        result[(dist, speed)] = calculate_time_in_warp(speed, 200, dist)

print("{:9s}".format(""), end="")
for speed in speeds:
    print("{:9.2f}".format(speed), end="")

last_dist = 1e999
for x,y in sorted(result.keys()):
    dist = get_distance(x)
    if (y < last_dist):
        print("\n{:7.5n} {:s}".format(dist[0],dist[1]), end="")
    last_dist = y

    print("{:9.0f}".format(math.ceil(result[x,y])), end="")

print()

  1. # Output

                                                          Warp Speed (AU/s)
  Distance     1.36     1.50     2.00     2.20     2.50     2.75     3.00     3.30     4.50     5.00     5.50     6.00     8.00
    150 KM       22       20       16       14       13       12       11       10        8        7        7        6        6
  1e+06 KM       48       44       33       30       27       25       23       21       16       14       13       12       11
      1 AU       63       57       43       40       35       32       29       27       20       18       17       15       14
      2 AU       65       59       45       41       36       33       30       28       21       19       17       16       15
      5 AU       67       61       47       43       38       34       32       29       22       19       18       16       15
     10 AU       71       65       49       45       40       36       33       30       23       20       19       17       16
     20 AU       78       71       54       49       44       40       37       33       25       22       21       19       17
     50 AU      100       91       69       63       56       51       47       43       32       28       26       24       21
    100 AU      137      125       94       86       76       69       63       58       43       38       35       32       27
    200 AU      211      191      144      131      116      105       97       88       65       58       53       49       40

# References
