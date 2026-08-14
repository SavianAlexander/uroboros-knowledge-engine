# EVE Evolved:  More FPS for less CPU

- **Date**: 2025-03-04T11:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/eve-evolved-more-fps-for-less-cpu
- **Tags**: #eve-evolved, #development-updates, #news

## Overview
Feel the need for speed with new rendering technology

---

Performance-hungry capsuleers

A recent [EVE Evolved blog](https://www.eveonline.com/news/view/paint-your-ship-red-and-make-it-faster) discussed how Quasar allowed for big improvements in how network communication is managed for features like SKINR. In this final installment of a series of dev blogs spotlighting EVE Evolved initiatives, the conversation moves nicely onto client performance and discusses a graphical rendering improvement scheduled for release in March. 


## **Trinity**


From flying in small, beautiful dungeons to fleet fights containing thousands of players, the number of situations players can find themselves in is vast. This provides a lot of technical challenges that are unique to EVE Online, all of which impact how the game feels and plays.

One of those challenges is “How do you display all of this on a screen?” For this, EVE uses its own rendering engine, named Trinity. Rendering engines are incredibly intricate, but to summarize and simplify, they need to do a huge number of complex calculations as fast as possible, so the game looks beautiful and runs as smooth as possible.

Trinity has a lot of different potential circumstances to deal with, especially when it comes to computer hardware. Some play EVE Online on old hardware, while others upgrade their system almost every year with the latest cutting-edge technology. This range means that there is no ‘average’ hardware for playing EVE, and that rendering must be ensured on all these systems.

From a gameplay perspective, EVE has a vast number of different styles. While trading in a station is fairly deterministic when it comes to rendering, flying in nullsec and being hotdropped by a huge fleet is a bit more complex. The game has to load many assets into memory simultaneously and render all of them while trying to keep the framerate as high as possible.

To make matters more complex, EVE is 22 years old, and new assets are added constantly. Graphical features added a decade ago would have targeted the computer hardware of that time, but it will run significantly faster on modern hardware. Bringing the latest rendering features to EVE while ensuring existing assets aren’t broken in the process can be a challenge, given the thousands of unique models and textures across New Eden.

For all these reasons, changes to Trinity must be made with care. 


## **Performance**


At Fanfest 2023 a future vision for some of planned changes was presented. One of these features, known as a [GPU Driven Pipeline](https://www.youtube.com/watch?v=ycZX-mqwD9k&t=1804s), is a technical change in the way the CPU and GPU work together. Traditionally, rendering a scene involves the CPU figuring out what to send to the GPU, and then the GPU doing the work. While the linked presentation goes into more detail, a more modern rendering pipeline allows the GPU to do more of these calculations overall, reducing the CPU overhead. This is great for a few reasons: 


- EVE is often CPU-bound, meaning the CPU is the limiting factor and not the GPU. Freeing up the CPU in these situations can be very beneficial.
- A modern GPU can render more frames with this approach – it’s just simply faster due to the advances DirectX 12 (Windows) and Metal (macOS) offer with modern GPUs.
- It makes adding or changing features in the codebase easier, allowing improvements to reach capsuleers faster. In addition, it simplifies processes for artists bringing new assets to the game.


Performance improvements depend on the specific CPU and GPU combination of each PC, with the biggest benefits happening when the CPU can’t provide enough data to the GPU. This happens fairly frequently with EVE, even on well-balanced computer specifications, simply due to the engine architecture and the emergent gameplay possibilities. You may have noticed this in fleet fights, where the CPU load in the client can be quite high, causing framerate reductions even when the GPU can handle more.

In a typical computer system with balanced components, these changes result in significant improvements. In rarer cases where a fast GPU is paired with a slower CPU, the performance increase can be even more impressive.
When changes are made to Trinity, a dedicated tool called “EVE Probe” is used. It has one job: to allow testing of just the rendering and audio engines. It’s a lightweight application that excludes other systems needed to play EVE Online, such as UI, network stack, or even keyboard and mouse input! This approach enables reliable performance testing outside the chaotic live server environment.

One of our most popular test scenes is called the “Cube of Death,” which has been covered in [previous dev blogs](https://www.eveonline.com/news/view/memory-improvements). In short, the test features 1,000 evenly spaced and stationary ships. They can also shoot at each other, resulting in mesmerizing visuals! It’s proven effective for clear before-and-after performance comparisons. 

After running this test across different hardware, performance typically increased between 10 to 30% FPS on DirectX 12. In some cases, it was even higher: The AMD 6800XT saw a massive ~52% improvement at 4k in one test!

macOS is a little different. In 2020, Apple released the “M1” SoC, which has both a CPU and GPU together on the same chip. These chips have a CPU and a GPU that are well-matched and work much more closely together than in a typical Windows system. Additionally, most macOS users have high-resolution screens that push the GPU’s limit even further. At high resolutions (4k and above), performance remains roughly the same, but at lower resolutions (like 1920 x 1200) this change can easily increase framerates by 25%.

Here is a small selection of example systems and the increase they saw at the highest settings in EVE Probe:


| **CPU & GPU** | **Resolution** | **FPS Before** | **FPS After** | **FPS % Increase** |
| --- | --- | --- | --- | --- |
| i7-7700 CPU & GTX 1060 | 1920 x 1080 | 40 | 53 | +32% |
| Ryzen 7 5800X & Radeon RX 6800 XT | 3840 x 2160 | 46 | 70 | +52% |
| i7-11700 & RTX 4070 Ti | 3840 x 2160 | 44 | 61 | +38% |
| Ryzen 7 7800X3D & Radeon RX 7800 XT | 3840 x 2160 | 60 | 68 | +13% |
| Mac M1 Max | 1920 x 1200 | 34 | 43 | +26% |


The GTX 1060 is now almost nine years old, so asking it to manage 1,000 ships at the highest settings is quite demanding. These framerates can usually be increased further by lowering the graphical settings, making it fairly easy to hit 60 FPS on this card with only minor adjustments. That’s quite impressive given the age of the card and what it’s being asked to render!

This increased performance update is scheduled for release in March. Simply ensure that DirectX 12 is enabled in the launcher. If DirectX 12 is not available to you, then you will still get a small improvement on DirectX 11.


## **What’s next?**


The move to a GPU Driven Pipeline required significant refactoring of Trinity, but it sets EVE up nicely for the development of more features, unlocking better performance, and increasing graphical fidelity in the future. You may already have seen some of these improvements in mass tests last year, such as upscaling and raytraced shadows. Although not ready for release to Tranquility yet, these tests validated the approach taken. A huge thank you goes out to everyone who participated in the tests last year and this past weekend. Your contribution really helps!

With the GPU now used more efficiently, more situations in the client will be GPU-limited (even though the overall framerate is higher). Upscaling solutions will enable even higher framerates in these scenarios. More details on that will follow in future dev blogs.

This concludes the current series of blogs spotlighting EVE Evolved initiatives. We hope you have enjoyed getting a peek into the engine bay. Remember, evolution in New Eden never stops- the work continues, ever-improving and advancing. Fly safe and stay curious.

o7
