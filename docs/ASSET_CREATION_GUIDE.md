# ASSET CREATION GUIDE

This document provides detailed briefs for artists/generators to ensure visual consistency in Simple Race.

## 1. Motorcycles (Player & Rivals)
- **Viewpoint:** Third-person chase view (looking from slightly above and behind).
- **Composition:** Centered on the rider. The rear wheel and the rider's back/helmet must be the focal point.
- **States:**
  - `upright`: Rider centered, bike perpendicular to camera.
  - `lean_left`: Rider/bike tilted to the left (viewer's perspective).
  - `lean_right`: Rider/bike tilted to the right (viewer's perspective).
- **Dimensions:** 256x256 px.
- **Technical:** Transparent background. Lighting should be consistent (e.g., sun at top-center).

## 2. Roadside Props (Trees, Bushes, Signs)
- **Viewpoint:** Eye-level or slightly elevated to match the pseudo-3D perspective.
- **Dimensions:** 256x256 px (standard).
- **Technical:** Transparent background. Assets should be able to be placed close to or far from the camera without breaking the perspective logic.

## 3. Backgrounds
- **Viewpoint:** Distant, fixed horizon.
- **Composition:** Wide panoramic view.
- **Dimensions:** 1600x600 px.
- **Technical:** Seamless tiling preferred for scrolling. No transparency needed (usually solid).

## 4. Road Textures
- **Viewpoint:** Top-down/Flat.
- **Dimensions:** 256x256 px.
- **Technical:** Must be perfectly seamless (tiling) to avoid visible lines when scaled/distorted by the engine.

## 5. HUD / Interface
- **Viewpoint:** 2D Overlay.
- **Style:** Arcade/Retro (High contrast, bold borders).
- **Dimensions:** Variable (individual components).
- **Technical:** Transparent background. Avoid embedded text; use engine-rendered fonts.

## 6. Effects
- **Viewpoint:** Dynamic (follows bike or collision point).
- **Dimensions:** Variable.
- **Technical:** High transparency/alpha blending capability.
