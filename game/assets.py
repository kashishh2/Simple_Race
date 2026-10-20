"""Cached project-relative asset loading with explicit sprite-sheet cropping."""
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets"

class AssetManager:
    def __init__(self):
        self.cache = {}
        self.warned = set()

    def find_path(self, relative):
        rel = Path(relative)
        candidates = [ASSET_ROOT / rel, ROOT / rel]
        if not rel.is_absolute() and ASSET_ROOT.exists():
            candidates.extend(ASSET_ROOT.rglob(rel.name))
        for p in candidates:
            if p.is_file():
                return p
        return None

    def image(self, relative, size=None):
        key = (str(relative), tuple(size) if size else None)
        if key in self.cache:
            return self.cache[key]
        path = self.find_path(relative)
        if path is None:
            if key not in self.warned:
                print(f"[assets] Missing: {relative}")
                self.warned.add(key)
            return None
        try:
            image = pygame.image.load(str(path)).convert_alpha()
            if size:
                image = pygame.transform.smoothscale(image, (max(1,int(size[0])), max(1,int(size[1]))))
            self.cache[key] = image
            return image
        except (pygame.error, OSError) as exc:
            print(f"[assets] Failed to load {path}: {exc}")
            return None

    def first(self, candidates):
        for candidate in candidates:
            img = self.image(candidate)
            if img is not None:
                return img, candidate
        return None, None

    def crop_sheet(self, relative, rect, size=None):
        """Crop one sprite using (x, y, width, height); never blit the whole sheet."""
        sheet = self.image(relative)
        if sheet is None:
            return None
        x, y, w, h = map(int, rect)
        bounds = pygame.Rect(0, 0, *sheet.get_size())
        crop = pygame.Rect(x, y, w, h).clip(bounds)
        if crop.width <= 0 or crop.height <= 0:
            print(f"[assets] Invalid crop {rect} for {relative} ({sheet.get_size()})")
            return None
        sprite = sheet.subsurface(crop).copy()
        if size:
            sprite = pygame.transform.smoothscale(sprite, (max(1,int(size[0])), max(1,int(size[1]))))
        return sprite

    def background(self, surface, candidates):
        image, _ = self.first(candidates)
        if image is None:
            return False
        sw, sh = surface.get_size()
        iw, ih = image.get_size()
        scale = max(sw / iw, sh / ih)
        image = pygame.transform.smoothscale(image, (int(iw*scale), int(ih*scale)))
        surface.blit(image, ((sw-image.get_width())//2, (sh-image.get_height())//2))
        return True

assets = AssetManager()
