# VISUAL PROTOTYPE PLAN: Simple Race - Sprite-Driven Pseudo-3D

This plan outlines the implementation of the first visual prototype for **Simple Race: Highway Rush**. The objective is to transition the game from primitive-based rendering to a sprite-driven, layered pseudo-3D environment that captures the "XP-era arcade" aesthetic.

## 1. Prototype Objectives
*   **Depth-Correct Road:** A scrolling road with perspective-accurate textures and lane markings.
*   **Parallax Environment:** A multi-layered background (Sky -> Mountains -> Skyline) that provides a sense of speed.
*   **Sprite-Based Entities:** The player and at least one rival rendered as sprites rather than primitives.
*   **Depth-Ordered Scenery:** Roadside objects (trees/signs) that scale and move based on their Z-depth.
*   **Retro HUD:** A stylized telemetry overlay.

## 2. Visual & Technical Specifications

### 2.1 Coordinate System & Projection
*   **Projection Method:** Continue using the existing `World.project` logic (perspective-based scaling and Y-offset).
*   **Coordinate Convention:** 
    *   **World Space:** `progress` (distance traveled) and `lane` (-1.0 to 1.0).
    *   **Screen Space:** `x, y` (800x600).
*   **Depth Calculation:** `d = player_progress - object_progress`.

### 2.2 Asset Requirements (The "MVP Set")
The following assets must be provided or generated (using placeholder sprites if necessary for the first run) to satisfy the prototype requirements.

| Asset Category | Asset ID | Description | Dimensions (approx) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Vehicles** | `SPR_PLAYER_IDLE` | Player motorcycle (side/rear view) | 250x126 | `Planned` |
| | `SPR_RIVAL_BASE` | Rival motorcycle (generic) | 80x50 | `Planned` |
| | `SPR_TRAFFIC_CAR` | Generic car for traffic | 120x60 | `Planned` |
| **Road** | `TEX_ROAD_ASPHALT` | Seamless asphalt texture | 256x64 | `Planned` |
| | `TEX_ROAD_LANE` | White lane marker (strip) | 10x40 | `Planned` |
| **Environment** | `SPR_TREE_PINE` | Roadside pine tree | 80x150 | `Planned` |
| | `SPR_SIGN_POST` | Roadside sign | 40x80 | `Planned` |
| **Background** | `BG_SKY_LAYER` | Gradient sky | 800x300 | `Planned` |
| | `BG_MTN_LAYER` | Distant mountain silhouette | 1600x200 | `Planned` |
| **UI** | `UI_HUD_ELEMENTS`| HUD frames/icons | N/A | `Planned` |

### 2.3 Animation Format
*   **Method:** Sprite sheet or sequential file naming (e.g., `player_01.png`, `player_02.png`).
*   **Implementation:** A simple state machine within the `Entity` class (IDLE, MOVING, TURNING, CRASH).

## 3. Module Responsibilities

*   **`AssetManager` (New):** 
    *   Load all assets in `assets/` during game startup.
    *   Handle `convert_alpha()` for performance.
    *   Provide a `get_sprite(id)` interface.
*   **`World` (Updated):** 
    *   Implement texture-based road rendering (instead of `pygame.draw.polygon`).
    *   Manage parallax layer scrolling based on `player.speed`.
*   **`Entities` (Updated):** 
    *   Replace `draw` methods with `surface.blit` calls.
    *   Add `current_frame` and `animation_timer` properties.
*   **`UI` (Updated):** 
    *   Shift from `PixelFont` drawing to pre-rendered UI sprite overlays for the HUD.

## 4. Integration Sequence

1.  **Step 1: Asset Foundation:** Implement `AssetManager` and ensure the game loads without crashing using placeholder colored rects as "proxies" for actual assets.
2.  **Step 2: Environment Layering:** Integrate parallax backgrounds and the textured road.
3.  **Step 3: Entity Sprite Transition:** Replace `Player` and `Rival` primitives with the first set of motorcycle sprites.
4.  **Step 4: Scenery & Depth:** Implement the scaling roadside objects using the `World.project` logic.
5.  **Step 5: HUD & VFX:** Integrate the stylized HUD and simple particle effects (smoke/nitro).

## 5. Acceptance Criteria & Review

### 5.1 Measurable Criteria
*   **Visual Accuracy:** The road must exhibit a clear vanishing point and perspective scaling.
*   **Performance:** The game must maintain a stable 60 FPS with at least 5 sprite-based entities and 2 parallax layers active.
*   **Asset Integrity:** No "missing asset" errors; all textures must be loaded via the `AssetManager`.
*   **Visual Coherence:** All sprites must follow the established "XP-era" color palette and art style.

### 5.2 Visual Review Procedure
*   **Static Check:** Ensure no pixelated "holes" appear in the road texture during rapid movement.
*   **Depth Check:** Verify that distant objects (mountains) move slower than the player than roadside trees.
*   **Scaling Check:** Confirm that the scale of vehicles and scenery matches the mathematical projection defined in `world.py`.
