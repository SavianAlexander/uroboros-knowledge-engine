# Upscaling & Ray-traced Shadows – Now Live!

- **Date**: 2025-08-18T11:00:00.000Z
- **Category**: news
- **Author**: EVE Online Team
- **Source**: https://www.eveonline.com/news/view/upscaling-and-ray-traced-shadows-now-live
- **Tags**: #eve-evolved, #development-updates, #news

## Overview
This month, EVE Evolved introduces a three-part series of dev blogs and their corresponding releases. First up: ray-traced shadows and advanced upscaling. Stay tuned for more news for EVE Evolved soon.

---

Greetings, capsuleers!

CCP is thrilled to introduce two major graphical enhancements now live for EVE Online, delivering elevated visual fidelity and improved performance.


## **Advanced Upscaling: Modern Solutions, Enhanced Performance**


Upscaling is an innovative graphics technique that boosts game performance by rendering at a lower resolution and intelligently enhancing the image quality to match your display's native resolution. This allows for smoother gameplay, higher frame rates, and significantly reduced graphics card load without sacrificing visual clarity. In mobile environments, upscaling also helps extend battery life, offering a great experience wherever you play.

Previously, AMD FSR 1 offered a solid performance improvement, albeit with visual compromises. This update advances visual quality and performance even further with new state-of-the-art upscaling technologies:


- **AMD FSR 3** AMD’s powerful upscaling solution, providing near native quality and smoother frame rates.
- **NVIDIA DLSS** DLSS upscaling technology from NVIDIA features advanced frame generation for exceptional image quality and optimized performance on NVIDIA GPUs.
- **Intel XeSS** Intel’s sophisticated upscaling technology, expanding compatibility and enhancing overall performance.
- **MetalFX for macOS** Specialized support for Apple Silicon macOS users, ensuring all capsuleers enjoy breathtaking graphics.


Unlike traditional shader-based methods such as FSR 1, these advanced solutions utilize sophisticated algorithms that deliver significantly improved image quality while optimizing performance. Each upscaler offers multiple quality settings, allowing you to fine-tune your visual experience based on your GPU capabilities and preferences. Only the upscalers supported by your system will appear as selectable options. If your system supports multiple technologies, feel free to experiment and find the best match for your setup.


## **Ray-traced Shadows: Superior Accuracy and Immersion**


In 2023, EVE's shadow system received a significant upgrade to cascaded shadows, dramatically enhancing visual depth compared to the older system, which had not seen updates for many years.

CCP are now excited to introduce ray-traced shadows, offering unparalleled accuracy in shadow rendering. Leveraging dedicated hardware found in modern graphics cards, ray-traced shadows can even outperform traditional methods in certain scenes.

Ray-traced shadows are generated using a sophisticated rendering technique, which simulates the physical behavior of light. It calculates the precise paths rays of light take from the game's primary light source (the star in each solar system) through the scene, accurately determining how those rays interact with surfaces and objects. Unlike traditional shadow-rendering methods, ray-traced shadows precisely replicate how shadows form based on object positions, distances, angles, and surface textures.

For example, consider sunlight hitting a ship orbiting a station. With ray-traced shadows, the shadows cast by that ship onto nearby structures like the station will dynamically change based on the relative positions of objects, creating sharp, more believable shadows that enhance visual realism and depth. While the existing shadow system can provide shadows in these situations, ray-traced shadows raise the quality significantly. EVE Online is particularly suited to benefit from ray-traced shadows due to its visually striking environments dominated by a single, strong primary light source—the local star. 

While ray tracing as a technology can potentially provide additional visual enhancements, such as reflections or global illumination, EVE Online will currently utilize raytracing exclusively for shadows. This focused implementation allows us to ensure optimal performance and fidelity. Future adoption of other ray tracing features could be explored later, but for now, ray-traced shadows represent the next exciting step toward integrating modern advanced rendering techniques. 

****


## **Technical Considerations**


Both advanced upscaling and ray-traced shadows depend on compatible software and hardware. If you do not see an expected option in the settings page of the game, you should:

**Update your OS**. Windows 10 version 1809 (October 2018 Update) and macOS Ventura are the minimum supported versions for some of these features.

**Update your GPU drivers**. Old drivers may not support these features.

**Check hardware compatibility**. Ray tracing requires the client running in DX12 with a DirectX ray tracing supported graphics card and certain upscaling solutions are locked to a manufacturer or GPU generation.

If you’re uncertain why a specific option isn’t available in the client after checking these, please post on our forums [here](https://forums.eveonline.com/).

Fly safe and immerse yourself in the enhanced beauty of New Eden!
