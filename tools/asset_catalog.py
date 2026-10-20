import os
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

try:
    from PIL import Image
except ImportError:
    Image = None

@dataclass
class AssetFile:
    id: str
    path: str
    size_bytes: int
    format: str
    dimensions: str = "Unknown"
    has_alpha: bool = False
    type: str = "unknown"

class AssetCatalog:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.assets: List[AssetFile] = []
        self.missing: List[Dict[str, str]] = []
        self.planned_inventory = {
            "bikes": [
                "player_bike_upright.png", "player_bike_lean_left.png", "player_bike_lean_right.png",
                "rival_bike_01_upright.png", "rival_bike_01_lean_left.png", "rival_bike_01_lean_right.png",
                "rival_bike_02_upright.png", "rival_bike_02_lean_left.png", "rival_bike_02_lean_right.png",
                "rival_bike_03_upright.png", "rival_bike_03_lean_left.png", "rival_bike_03_lean_right.png",
                "rival_bike_04_upright.png", "rival_bike_04_lean_left.png", "rival_bike_04_lean_right.png",
            ],
            "scenery": ["tree_01.png", "tree_02.png", "tree_03.png", "prop_01.png", "prop_02.png", 
                        "sign_01.png", "sign_02.png", "guardrail_segment.png", "building_01.png", "sky_mountain_bg.png"],
            "textures": ["road_asphalt.png", "road_shoulder.png", "terrain_grass.png", "road_lane_marking.png", "road_rumble_strip.png"],
            "ui": ["ui_speedo_panel.png", "ui_race_pos_panel.png", "ui_nitro_meter.png", "ui_damage_meter.png", 
                   "ui_countdown_overlay.png", "ui_menu_panel.png", "ui_results_bg.png"],
            "audio": ["sfx_sparks.wav", "sfx_dust.wav", "sfx_collision.wav", "sfx_crash.wav", 
                      "music_main_loop.ogg", "sfx_engine_idle.wav", "sfx_engine_high.wav", 
                      "sfx_ui_select.wav", "sfx_ui_crash.wav"]
        }

    def scan(self):
        image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
        audio_exts = {'.wav', '.ogg', '.mp3'}

        for root, _, files in os.walk(self.root_dir):
            for file in files:
                full_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in image_exts:
                    info = AssetFile(id=file, path=full_path, size_bytes=os.path.getsize(full_path), format=ext[1:], type="image")
                    if Image:
                        try:
                            with Image.open(full_path) as img:
                                info.dimensions = f"{img.width}x{img.height}"
                                info.has_alpha = img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)
                        except Exception as e:
                            info.dimensions = f"Error: {str(e)}"
                    self.assets.append(info)
                
                elif ext in audio_exts:
                    info = AssetFile(id=file, path=full_path, size_bytes=os.path.getsize(full_path), format=ext[1:], type="audio")
                    self.assets.append(info)

    def check_missing(self):
        found_names = {a.id.split('.')[0] for a in self.assets} # Simple name matching
        # Realistically we should check exact paths for the inventory, but for this tool:
        for category, files in self.planned_inventory.items():
            for f in files:
                basename = os.path.splitext(f)[0]
                if not any(basename in a.id for a in self.assets):
                    self.missing.append({"category": category, "asset": f})

    def write_json(self, out_path: str):
        with open(out_path, 'w') as f:
            json.dump([asdict(a) for a in self.assets], f, indent=4)

    def write_md(self, out_path: str):
        with open(out_path, 'w') as f:
            f.write("# Asset Catalog\n\n")
            if not self.assets:
                f.write("No assets found.\n")
            else:
                f.write("| ID | Path | Format | Dimensions | Alpha | Type |\n")
                f.write("| --- | --- | --- | --- | --- | --- |\n")
                for a in self.assets:
                    f.write(f"| {a.id} | {a.path} | {a.format} | {a.dimensions} | {a.has_alpha} | {a.type} |\n")
            
            f.write("\n## Missing Assets\n")
            if not self.missing:
                f.write("All planned assets are present.\n")
            else:
                for m in self.missing:
                    f.write(f"- [{m['category']}] {m['asset']}\n")

def main():
    catalog = AssetCatalog(".")
    catalog.scan()
    catalog.check_missing()
    catalog.write_json("docs/ASSET_CATALOG.json")
    catalog.write_md("docs/ASSET_CATALOG.md")
    print(f"Cataloged {len(catalog.assets)} assets. Found {len(catalog.missing)} missing.")

if __name__ == "__main__":
    main()
