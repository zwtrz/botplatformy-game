import pygame
from settings import GRAVITY, JUMP_VELOCITY, TILE_SIZE, PLAYER_SPEED

class Player(pygame.sprite.Sprite):
    """Personagem controlado pelo jogador."""
    def __init__(self, pos, anims):
        super().__init__()
        self.anims = anims  # 'idle','run','jump','fall'
        self.anim_state = 'idle'
        self.anim_index = 0.0
        self.anim_speed = 10.0

        self.image = self.anims['idle'][0]

        # hitbox um pouco menor que o sprite
        largura_colisao = int(TILE_SIZE * 0.6)
        altura_colisao = TILE_SIZE
        self.rect = pygame.Rect(pos[0], pos[1], largura_colisao, altura_colisao)

        # centraliza a hitbox no centro do sprite
        self.rect.centerx = pos[0] + TILE_SIZE // 2

        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False
        self.facing = 1  # 1 direita, -1 esquerda

    def handle_input(self, keys):
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
            self.facing = 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel.y = JUMP_VELOCITY
            self.on_ground = False

    def apply_gravity(self):
        self.vel.y += GRAVITY
        if self.vel.y > 20:
            self.vel.y = 20

    def _set_anim_state(self):
        if not self.on_ground:
            self.anim_state = 'jump' if self.vel.y < 0 else 'fall'
        else:
            self.anim_state = 'run' if abs(self.vel.x) > 0.1 else 'idle'

    def _animate(self, dt):
        frames = self.anims[self.anim_state]
        self.anim_index += self.anim_speed * dt
        if self.anim_index >= len(frames):
            self.anim_index = 0.0
        frame = frames[int(self.anim_index)]
        if self.facing == -1:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def horizontal_movement(self, tiles):
        self.rect.x += self.vel.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right

    def vertical_movement(self, tiles):
        self.rect.y += self.vel.y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0

    def update(self, dt, tiles, keys):
        self.handle_input(keys)
        self.apply_gravity()
        self.horizontal_movement(tiles)
        self.vertical_movement(tiles)
        self._set_anim_state()
        self._animate(dt)
