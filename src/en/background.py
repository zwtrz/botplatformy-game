
import pygame
from settings import WIDTH, HEIGHT

class ParallaxBackground:
    """
    Draws horizontally tiling parallax background layers.
    Each layer is a dict with keys: 'image' (Surface) and 'speed' (0..1 parallax factor).
    The image will be scaled to HEIGHT and tiled horizontally across WIDTH.
    """
    def __init__(self, layers):
        # Pre-scale to window height to keep blits cheap
        self.layers = []
        for layer in layers:
            img = layer['image']
            spd = float(layer.get('speed', 0.5))
            # scale to height, keep aspect
            w, h = img.get_size()
            scale = HEIGHT / h if h else 1.0
            scaled = pygame.transform.smoothscale(img, (int(w * scale), int(HEIGHT)))
            self.layers.append({'image': scaled, 'speed': spd})

    def draw(self, surf, camera_x: float):
        for layer in self.layers:
            img = layer['image']
            spd = layer['speed']
            iw, ih = img.get_size()
            # Parallax offset moves opposite the camera
            offset_x = -camera_x * spd
            # Tile horizontally to cover the whole screen
            start_x = int(offset_x) % iw - iw
            x = start_x
            while x < WIDTH:
                # Align layers to bottom of the screen
                surf.blit(img, (x, HEIGHT - ih))
                x += iw
