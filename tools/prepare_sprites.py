import argparse
import os
import sys
import sysconfig

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Error: The 'Pillow' library is required for this tool.")
    print("Install it with: pip install Pillow")
    sys.exit(1)

def process_sprite(input_path, output_path, crop_rect=None, size=None, center=True, overwrite=False):
    if os.path.exists(output_path) and not overwrite:
        print(f"Error: File '{output_path}' already exists. Use --overwrite to replace it.")
        return

    try:
        with Image.open(input_path).convert("RGBA") as img:
            # 1. Crop if rect provided (left, top, right, bottom)
            if crop_rect:
                img = img.crop(crop_rect)

            # 2. Resize while preserving aspect ratio
            if size:
                target_w, target_h = size
                img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
                
                # 3. Center on a transparent canvas
                new_img = Image.new("RGBA", size, (0, 0, 0, 0))
                if center:
                    # Calculate centering offsets
                    x = (target_w - img.width) // 2
                    y = (target_h - img.height) // 2
                    new_img.paste(img, (x, y), img)
                else:
                    new_img.paste(img, (0, 0), img)
                img = new_img

            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PNG")
            print(f"Successfully saved: {output_path}")

    except Exception as e:
        print(f"Error processing image: {e}")

def main():
    parser = argparse.ArgumentParser(description="Prepare sprites for Simple Race asset pipeline.")
    parser.add_argument("input", help="Input PNG file")
    parser.add_argument("output", help="Output PNG file")
    parser.add_argument("--crop", nargs=4, type=int, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'), help="Crop rectangle")
    parser.add_argument("--size", nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), help="Target canvas size")
    parser.add_argument("--no-center", action="store_false", dest="center", help="Don't center the sprite on the canvas")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing file")

    args = parser.parse_args()

    process_sprite(
        input_path=args.input,
        output_path=args.output,
        crop_rect=args.crop,
        size=args.size,
        center=args.center,
        overwrite=args.overwrite
    )

if __name__ == "__main__":
    main()
