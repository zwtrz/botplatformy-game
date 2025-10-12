import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, image, size):
        super().__init__()
        # Break a HORIZONTAL spritesheet into square frames
        self.frames = []
        sheet = image
        sheet_w, sheet_h = sheet.get_size()
        frame_w = sheet_h  # frames are square: width == height == sheet height
        for x in range(0, sheet_w, frame_w):
            frame = sheet.subsurface(pygame.Rect(x, 0, frame_w, frame_w))
            self.frames.append(pygame.transform.scale(frame, (size, size)))

        self.index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=pos)
        self.anim_speed = 10  # frames per second

    def update(self, dt):
        self.index = (self.index + self.anim_speed * dt) % len(self.frames)
        self.image = self.frames[int(self.index)]
