# Simple_Race vehicle selection and rendering changes

## Exact behavior changed
- Main menu now has START RACE, VEHICLE: BIKE/CAR, CONTROLS, QUIT.
- Use Up/Down to move through the menu. On VEHICLE, Left/Right or Enter toggles BIKE/CAR.
- The selected vehicle is preserved when a race starts/restarts.
- BIKE mode loads individual files such as assets/bikes/player_bike_upright.png and lean variants. It never blits an entire sprite sheet.
- CAR mode first tries assets/cars/player_car.png, assets/cars/player_car_rear.png, or assets/traffic/player_car.png; if none exist it uses the previous car drawing as fallback.
- Asset manager supports project-relative paths and explicit crop_sheet(relative, (x,y,w,h)) for later integration once sheet coordinates are known.
- Background loading is restricted to named background files, not arbitrary PNGs/sprite sheets.
- Pygame font initialization guarded.

## Critical limitation
The actual assets directory and the current running version of the code were not uploaded. The provided recording shows a sprite sheet appearing over gameplay, but its exact filename and sprite-cell coordinates cannot be established from the Python source files alone. No new vehicle artwork files are fabricated in this code bundle. To use car artwork, place a transparent rear-view car sprite at assets/cars/player_car.png. To use the bike, retain the three named bike PNGs from the project.
