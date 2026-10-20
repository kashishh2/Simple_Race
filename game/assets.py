import os
import pygame
import logging

class AssetManager:
    """Manages loading and caching of game assets."""
    def __init__(self, root_dir=None):
        self.root_dir = root_dir or os.path.dirname(os.path.abspath(__file__))
        self.images = {}
        self.fonts = {}
        self.logger = logging.getLogger("AssetManager")

    def get_image(self, relative_path, scale=None):
        """Loads and caches a PNG image. Supports scaling."""
        if relative_path in self.images:
            img = self.images[relative_path]
            if scale:
                scale_key = (relative_path, scale)
                if scale_key in self.images:
                    return self.images[scale_key]
                img = self._scale_image(img, scale)
                self.images[scale_key] = img
            return img

        full_path = os.path.join(self.root_dir, relative_path)
        try:
            img = pygame.image.load(full_path).convert_alpha()
            self.images[relative_path] = img
            
            if scale:
                scale_key = (relative_path, scale)
                self.images[scale_key] = self._scale_image(img, scale)
            
            return img
        except pygame.error as e:
            self.logger.error(f"Failed to load image: {full_path} - {e}")
            # Return a placeholder surface (magenta square) to avoid crashing
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (255, 0, 255), (0, 0, 64, 64), 2)
            return placeholder
        except FileNotFoundError:
            self.logger.error(f"Image not found: {full_path}")
            placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (255, 0, 255), (0, 0, 64, 64), 2)
            return placeholder

    def _scale_image(self, img, scale):
        """Internal helper for scaling."""
        new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
        return pygame.transform.smoothscale(img, new_size)

    def clear_cache(self):
        """Clears the image cache."""
        self.images.clear()
        self.fonts.clear()

# Global instance for easy access across modules
assets = AssetManager()
