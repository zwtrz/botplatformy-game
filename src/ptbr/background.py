import pygame
from settings import WIDTH, HEIGHT

class ParallaxBackground:
    """Fundo com camadas em parallax (só desenha e pronto)."""
    def __init__(self, layers):
        self.layers = []
        for layer in layers:
            img = layer['image']
            spd = float(layer.get('speed', 0.5))
            w, h = img.get_size()
            esc = HEIGHT / h if h else 1.0
            escalada = pygame.transform.smoothscale(img, (int(w * esc), int(HEIGHT)))
            self.layers.append({'image': escalada, 'speed': spd})

    def draw(self, surf, camera_x: float):
        for layer in self.layers:
            img = layer['image']
            spd = layer['speed']
            iw, ih = img.get_size()
            off_x = -camera_x * spd
            start_x = int(off_x) % iw - iw
            x = start_x
            while x < WIDTH:
                surf.blit(img, (x, HEIGHT - ih))
                x += iw
