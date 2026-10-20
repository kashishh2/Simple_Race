# OPENCLAW_CONTEXT.md

## 1. Project Identity and Goal
- **Name:** Simple Race: Highway Rush
- **Vision:** A Windows XP-era arcade racing game inspired by classic Road Rash-style presentation.
- **Core Tech:** Python, Pygame.
- **Goal:** A polished, asset-driven game featuring sprite-based pseudo-3D graphics, not a primitive-shape graphics demo.

## 2. Approved Decisions
- **Engine:** Keep Pygame for rendering and input.
- **Graphics:** Transition from procedural shapes to real visual assets (sprites, textures).
- **Perspective:** Maintain and refine the existing pseudo-3D road perspective.
- **Approach:** Incremental improvement of the existing codebase.
- **Migration:** Do not migrate to Godot or other engines without explicit approval.

## 3. Current Verified Architecture
### Python Modules
- `main.py`: Game engine, state management (Menu, Racing, Gameover), and orchestration.
- `config.py`: Global constants (dimensions, colors, physics, track curves).
- `entities.py`: Car hierarchy (`Car` -> `Player`, `Rival`) and physics/AI logic.
- `world.py`: Pseudo-3D rendering, road projection, and scenery placement.
- `ui.py`: HUD and custom `PixelFont` rendering.

### Environment
- **Python Version:** Verified via `exec: python --version` (pending verification)
- **Virtual Environment:** `.venv/` (detected in root)
- **Launch Command:** `python main.py` (standard)

### Uncertainties
- Exact Python version and dependency list (requires `pip freeze` or `requirements.txt` verification).

## 4. Visual Direction
- **Theme:** High-contrast, vibrant "early 2000s arcade" look.
- **Assets Needed:**
    - Motorcycle/Rider sprites (Player and Rival).
    - Road texture segments (asphalt, lane markings).
    - Scenery sprites (trees, bushes, signs, buildings).
    - Parallax background layers (sky, mountains, skyline).
    - HUD and Menu UI assets.
- **Animation:** Sprite-based movement, wheel rotation, and vehicle tilting/leaning.

## 5. Target Directory Structure
- `assets/` (Planned): Sprite sheets and textures.
- `docs/` (Existing): Project audit and documentation.
- `tools/` (Existing): Helper utilities.
- `backups/` (Existing): System backups.
- `media/` (Existing): Placeholder/temporary assets.

## 6. Development Roadmap
1. **Audit & Design:** (Current Phase) Project audit and architectural review.
2. **Asset Acquisition:** Define and create/collect the Asset Manifest.
3. **Visual Prototype:** One polished, playable segment using actual sprites.
4. **Mechanics Expansion:** Refined AI, combat (hitting rivals), and traffic.
5. **Content & Polish:** Multiple tracks, menu progression, audio, and final packaging.

## 7. Engineering Rules
- **Inspection:** Always read relevant files before editing.
- **Modularity:** Make small, coherent changes; preserve working functionality.
- **Asset-First:** Use actual image files for final visuals; avoid procedural drawing for cars/scenery.
- **Validation:** Verify asset paths and loading logic; do not assume files exist.
- **Safety:** Keep backups before significant structural changes.

## 8. Verification Requirements
- **Syntax:** Verify Python files compile/load without errors.
- **Asset Check:** Confirm all loaded textures/sprites are present in `assets/`.
- **Runtime:** Run the game to verify visual rendering and physics integration.

## 9. Session Handoff
- **New Sessions:** Read this file first. Review `docs/SESSION_LOG.md` if present.
- **End of Session:** Record completed work, changed files, tests run, and the next immediate task.

## 10. Current State and Next Task
- **Current State:** Audit complete. The project is functional with primitive graphics and requires an asset-driven transition.
- **Next Task:** Review the project audit (`docs/PROJECT_AUDIT.md`) and propose an **Asset Manifest** and **Visual Prototype Plan**.
