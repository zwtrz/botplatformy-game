import pygame
from tile import Tile
from coin import Coin
from player import Player
from utils import load_spritesheet
from settings import TILE_SIZE, KILL_PLANE_Y, WIDTH, HEIGHT


class Level:
    lost: bool = False

    def __init__(self, layout, assets):
        self.lost = False
        self.layout = layout
        self.assets = assets
        self.camera = pygame.Vector2(0, 0)
        self.tiles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.flags = pygame.sprite.Group()
        self.player = None
        self.spawn = (64, 64)

        self.build()

    def build(self):
        tile_img = self.assets['tile']
        coin_image = self.assets['coin_image']
        flag_img = self.assets['flag']
        player_anims = self.assets['player_anims']

        # Parse layout
        for row_idx, row in enumerate(self.layout):
            for col_idx, ch in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                if ch == 'X':
                    self.tiles.add(Tile((x, y), tile_img, TILE_SIZE))
                elif ch == 'C':
                    self.coins.add(Coin((x + TILE_SIZE // 2, y + TILE_SIZE // 2), coin_image, int(TILE_SIZE * 0.75)))
                elif ch == 'P':
                    self.spawn = (x, y - 8)
                elif ch == 'E':
                    flag = Tile((x, y - TILE_SIZE // 2), flag_img, int(TILE_SIZE))
                    self.flags.add(flag)

        # Player
        self.player = Player(self.spawn, player_anims)

        # Add invisible left/right boundary walls and a shallow floor extension to avoid falling forever
        # Left wall at x = -TILE_SIZE, right wall at right of widest row
        widest_cols = max(len(r) for r in self.layout)
        world_width = widest_cols * TILE_SIZE
        left_wall = Tile((-TILE_SIZE, 0), self.assets['tile'], TILE_SIZE)
        right_wall = Tile((world_width, 0), self.assets['tile'], TILE_SIZE)
        # Make the walls tall by duplicating vertically
        for i in range(int(HEIGHT / TILE_SIZE) + 6):
            lw = Tile((left_wall.rect.x, i * TILE_SIZE), self.assets['tile'], TILE_SIZE)
            rw = Tile((right_wall.rect.x, i * TILE_SIZE), self.assets['tile'], TILE_SIZE)
            # make them very transparent to visually disappear if we ever draw them (we won't)
            lw.image.set_alpha(0);
            rw.image.set_alpha(0)
            self.tiles.add(lw);
            self.tiles.add(rw)

    def respawn(self):
        self.player.rect.topleft = self.spawn
        self.player.vel.update(0, 0)
        self.player.on_ground = False

    def update(self, dt, keys):
        self.player.update(dt, self.tiles.sprites(), keys)
        self.coins.update(dt)
        # Kill plane check
        if self.player.rect.top > KILL_PLANE_Y:
            self.lost = True

    def draw(self, surf, background):
        self.camera.x = self.player.rect.centerx - WIDTH // 2
        self.camera.y = self.player.rect.centery - HEIGHT // 2
        self.camera.x = max(0, self.camera.x)
        self.camera.y = max(0, self.camera.y)
        if background:
            bg = pygame.transform.scale(background, surf.get_size())
            surf.blit(bg, (0, 0))
        for group in (self.tiles, self.coins, self.flags):
            for sprite in group:
                surf.blit(sprite.image, sprite.rect.move(-self.camera.x, -self.camera.y))

        # Draw sprite centered on collision rect
        sprite_x = self.player.rect.centerx - TILE_SIZE // 2
        sprite_y = self.player.rect.top
        surf.blit(self.player.image, (sprite_x - self.camera.x, sprite_y - self.camera.y))

    def collected_all(self):
        return len(self.coins) == 0

    def at_exit(self):
        for flag in self.flags:
            if self.player.rect.colliderect(flag.rect):
                return True
        return False

    def try_collect(self):
        pygame.sprite.spritecollide(self.player, self.coins, dokill=True)