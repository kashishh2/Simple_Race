# Player Motorcycle Art Brief

This document contains precise prompts for generating the player motorcycle sprite set for **Simple Race**. 

## Visual Style Summary
- **Era/Style:** Late 1990s / Early 2000s Arcade Racing (e.g., *Road Rash*, *Cruis'n USA*). Detailed, saturated, illustrated game sprite.
- **Perspective:** Third-person chase view, looking from slightly above and behind the rider.
- **Subject:** A professional sport motorcycle and rider.
- **Color Palette:** Deep red and black bodywork, white accents, black tires/details.
- **Background:** Solid Black (to be converted to transparency) or Transparent.

---

## 1. Frame: Upright (Reference)
**Goal:** The primary neutral state.

**Prompt:**
> A high-quality, detailed 2D game sprite of a professional racing sport motorcycle and rider, seen from a rear-view chase camera perspective (looking from slightly above and behind). The bike is an aggressive red and black sportbike with white accents. The rider is wearing a matching red and black racing suit with a full-face helmet and black gloves, leaning slightly forward in a racing posture. The rear tire is broad and prominent. High-contrast arcade lighting with bright highlights on the metallic bodywork. Isolated on a plain, solid black background. No text, no shadows on the ground, no scenery, no watermarks. 90s arcade aesthetic, polished digital illustration.

---

## 2. Frame: Lean Left
**Goal:** The rider and bike tilting into a turn towards the left.

**Prompt:**
> A high-quality, detailed 2D game sprite of the same red and black sport motorcycle and rider from the previous image, seen from the same rear-view chase camera perspective. **Action:** The motorcycle and rider are visibly tilting to the left (viewer's left) as if navigating a sharp turn. The rider's body and the bike's chassis are angled leaning into the turn. Maintain identical colors (red, black, white), identical rider gear, and identical lighting. Isolated on a plain, solid black background. No text, no shadows, no scenery, no watermarks. 90s arcade aesthetic, polished digital illustration.

---

## 3. Frame: Lean Right
**Goal:** The mirror of the left lean.

**Prompt:**
> A high-quality, detailed 2D game sprite of the same red and black sport motorcycle and rider from the previous image, seen from the same rear-view chase camera perspective. **Action:** The motorcycle and rider are visibly tilting to the right (viewer's right) as if navigating a sharp turn. The rider's body and the bike's chassis are angled leaning into the turn. Maintain identical colors (red, black, white), identical rider gear, and identical lighting. Isolated on a plain, solid black background. No text, no shadows, no scenery, no watermarks. 90s arcade aesthetic, polished digital illustration.

---

## Technical Consistency Requirements for Generation
- **Viewpoint:** The horizon/camera angle must remain constant across all three images.
- **Proportions:** The scale of the bike and rider relative to the frame must be nearly identical.
- **Centerline:** The vertical centerline of the bike should remain in the same horizontal position in the frame to prevent "jittering" during animation.
- **Output Format:** High-resolution PNG or high-quality JPEG (to be processed by `prepare_sprites.py`).
