---
title: "Acceleration"
url: "https://wiki.eveuniversity.org/Acceleration"
pageid: 13290
source: "EVE University Wiki"
categories: ["Game mechanics"]
harvested_at: "2026-08-16 23:22:26 UTC"
---

# Acceleration

The **acceleration** of objects in EVE is not based on classical physics. The physics engine is based on a fluid dynamics model, which assumes that space has some substance to it and thus some friction. This means that when a ship's engine is inactive, the ship will decelerate, ultimately to a standstill. As a result, all acceleration is proportional to agility, relative to maximum velocity, and exponential.

Although this article refers only to ships, the acceleration mechanics apply to any object moving under power in the EVE universe, for example missiles and drones.

1. # How do ships in EVE accelerate and decelerate?
In terms of kinematic motion, when the ship starts to accelerate it will quickly increase its speed, but as the speed increases toward the maximum, the acceleration decreases exponentially. (In theory, the ship will never reach its top speed, however in reality, it won't take long to get so close to top speed that the difference is negligible and EVE rounds up the figure on the HUD.)

Deceleration is simply acceleration in a direction opposed to the one and object is traveling in, i.e. 'braking'. The closer to the ship's top speed it is traveling, the faster it will decelerate.

1. # What decides how quickly a ship accelerates?
The idea of acceleration = force/mass can be thrown away for now, because there are only two basic attributes which determine the relative acceleration (how quickly a ship accelerates to its maximum speed): Mass and Inertial Modifier. The latter can be reduced with both skills and modules while mass can only be reduced in very specific circumstances (on the other hand, it may be increased by armor plates and active propulsion modules). The product of Mass and the Inertia Modifier gives the ship's agility which determines how quickly the ship accelerates (and thus how quickly it turns); lower values imply better acceleration and turning speed. On the other hand, the maximum velocity of a ship does not affect relative acceleration at all. So on a ship equipped with Nanofiber Internal Structure, for example, while both the inertia and maximum speed modifier make the ship accelerate in classical terms faster, only the inertia will make its relative acceleration faster, making it align to warp faster.

To demonstrate, here's an example of this exponential acceleration:

Two ships with identical mass and inertial modifier but different top speeds will reach their respective top speeds in the same period. Thus, a ship with a higher top speed will have a higher acceleration in ms^-2 but will take the same time to reach the speed required to use warp engines.

  1. # Accelerating to warp

To initiate **warp travel**, a ship must be aligned to its target and traveling at 75% of its maximum velocity or higher. The "time to warp" from a standstill can be calculated for any ship using the formulas presented here (see the **example** below). The time to warp can change depending on a ship's speed and alignment in relation to its destination at the time the command to initiate warp is issued.

There are two methods by which the time to warp can be greatly reduced below its normal value. The first involves cycling a microwarpdrive once to quickly increase a ship's maximum and current velocity, then suddenly decrease its maximum velocity in the span of a few seconds. The second uses a companion ship to activate multiple **stasis webifiers** on the aligning ship, decreasing its maximum velocity while keeping its current velocity the same, allowing it to enter warp more quickly.

1. # Mathematics and formulae
The following formula describes the velocity of a ship accelerating from a standstill after a particular time:

> <math >V_{\rm{t}} = V_{\rm{max}} \times \left( 1 - e^{ \frac{-t\times10^6}{I\times M} }  \right) </math>

where:

***t* : Time in seconds**:

***V<sub>t</sub>* : Velocity after time *t* in m/s**:

***V<sub>max</sub>* : Ship's maximum velocity in m/s**:

***I* : Ship's inertia modifier, in s/kg**:

***M* : Ship's mass in kg**:

***e* : **Euler's Number** ≈ 2.71828**:

  1. # Explanation
The final term (with the exponent) gives the fraction of maximum velocity that is reached after time *t*. This is multiplied by the maximum velocity to find the absolute velocity at time *t*. Note that this only depends on time, inertia modifier and mass (*e* is a constant).

The 10<sup>6</sup> term cancels out a factor of one million in the mass term. So to simplify you can ignore the 10<sup>6</sup> and use the mass of the ship in millions of kg instead of kg.

As for acceleration itself, this is just the first derivative of velocity with respect to time.

Rearranging the formula for t we arrive at the formula for time taken to accelerate from zero to V:

> <math> \displaystyle t_{V} = -I \times M \times 10^{-6} \times \ln\left( 1 - \frac{V}{V_{\rm{max}} } \right) </math>

Where *t<sub>V</sub>* is the time to accelerate to velocity *V* in seconds. Note that at *V* = *V<sub>max</sub>*, 1 - *V* / *V<sub>max</sub>* = 0, but ln 0 is undefined, so in theory it takes infinite time to reach maximum speed (technically, the limit of *t<sub>V</sub>* as *V* approaches *V<sub>max</sub>* is positive infinity). In practice the game simulation is not perfectly accurate and it actually takes finite time to reach maximum speed to within whatever precision the simulation uses. (Strictly speaking, velocity is a vector, so it has both direction and magnitude, but the game is really only concerned with its absolute value (i.e. the magnitude part) more commonly called 'speed'.)

  1. ## Example
Pete has just got himself a new freighter, a . The Charon has a mass of 1,200,000,000 kg and an inertia modifier of 0.02176875 (after adjustment for skills). Pete wants to know how long it takes for his ship to reach the speed needed to enter warp. Since this is 75% of the ship's top speed regardless of what that top speed actually is, he doesn't bother calculating it, but instead simplifies by substituting 0.75 and 1 for *V* and *V<sub>max</sub>* respectively.

 Time to Warp = 0.02176875 × 1.2 × 10^9 × 10^-6 × -ln (1 - 0.75 / 1)
              = 0.02176875 × 1.2 × 10^3 × -ln (1 - 0.75)
              = 0.02176875 × 1200 × -ln 0.25
              = 26.1225 × 1.38629436
              = 36.2134744 seconds.
