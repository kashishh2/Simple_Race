# ASSET SPECIFICATION

This document outlines the technical requirements for all visual and audio assets for the Simple Race project.

## Visual Style
- **Era:** Late 1990s/Early 2000s Arcade Racing.
- **Perspective:** Rear-view, slightly elevated chase view for motorcycles.
- **Format:** Transparent PNG for all sprites/objects.
- **Consistency:** Consistent lighting (top-down/angled), color palette, and rider proportions.

## 1. Motorcycles
| Asset ID | Canvas Size | States | Viewpoint |
| :--- | :--- | :--- | :--- |
| `player_bike` | 256x256 | upright, lean_left, lean_right | Rear/Chase |
| `rival_bike_01` | 256x256 | upright, lean_left, lean_right | Rear/Chase |
| `rival_bike_02` | 256x256 | upright, lean_left, lean_right | Rear/Chase |
| `rival_bike_03` | 256x256 | upright, lean_left, lean_right | Rear/Chase |
| `rival_bike_04` | 256x256 | upright, lean_left, lean_right | Rear/Chase |

## 2. Roadside Scenery
| Category | Asset Name | Canvas Size | Notes |
| :--- | :--- | :--- | :--- |
| Trees | `tree_01`, `tree_02`, `tree_03` | 256x256 | Transparent PNG |
| Bushes/Rocks | `prop_01`, `prop_02` | 256x256 | Transparent PNG |
| Signs | `sign_01`, `sign_02` | 256x256 | Transparent PNG |
| Guardrail | `guardrail_segment` | 512x256 | Seamless-capable |
| Building | `building_01` | 512x512 | Transparent PNG |
| Background | `sky_mountain_bg` | 1600x600 | Seamless/Looped |

## 3. Road Textures
*All textures should be 256x256 and tileable/seamless.*
- `road_asphalt`
- `road_shoulder`
- `terrain_grass`
- `road_lane_marking`
- `road_rumble_strip`

## 4. Interface (UI)
*UI elements should be separate panels; text is rendered dynamically.*
- `ui_speedo_panel`
- `ui_race_pos_panel`
- `ui_nitro_meter`
- `ui_damage_meter`
- `ui_countdown_overlay`
- `ui_menu_panel`
- `ui_results_bg`

## 5. Audio
*Formats: .wav (SFX), .ogg (Music/Loops).*
- `sfx_sparks`, `sfx_dust`, `sfx_collision`, `sfx_crash`
- `music_main_loop`
- `sfx_engine_idle`, `sfx_engine_high`
- `sfx_ui_select`, `sfx_ui_crash`
