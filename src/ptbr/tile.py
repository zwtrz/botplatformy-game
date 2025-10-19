import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image, size):
        super().__init__()
        self.image = pygame.transform.scale(image, (size, size))
        self.rect = self.image.get_rect(topleft=pos)
