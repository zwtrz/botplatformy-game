import pygame
from tile import Tile
from coin import Coin
from player import Player
from background import ParallaxBackground
from settings import TILE_SIZE, KILL_PLANE_Y, WIDTH, HEIGHT, CAMERA_MARGIN_X, CAMERA_MARGIN_Y

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
        self.parallax = ParallaxBackground(self.assets.get('parallax_layers', []))

    def build(self):
        self.tiles.empty()
        self.coins.empty()
        self.flags.empty()
        self.player = None

        grid = self.layout
        rows = len(grid)
        cols = len(grid[0]) if rows else 0

        def in_bounds(r, c):
            return 0 <= r < rows and 0 <= c < cols

        def cell(r, c):
            return grid[r][c] if in_bounds(r, c) else '.'

        tile_imgs = self.assets.get('tiles', {})
        grass_mid = tile_imgs.get('grass_mid')
        grass_cl = tile_imgs.get('grass_corner_left') or grass_mid
        grass_cr = tile_imgs.get('grass_corner_right') or grass_mid
        dirt_mid = tile_imgs.get('dirt_mid') or grass_mid
        dirt_cl = tile_imgs.get('dirt_corner_left') or dirt_mid
        dirt_cr = tile_imgs.get('dirt_corner_right') or dirt_mid
        box_img = tile_imgs.get('box')

        for r in range(rows):
            for c in range(cols):
                ch = grid[r][c]
                x, y = c * TILE_SIZE, r * TILE_SIZE

                if ch == 'X':
                    acima = cell(r - 1, c) == 'X'
                    esquerda_ar = cell(r, c - 1) != 'X'
                    direita_ar = cell(r, c + 1) != 'X'
                    if not acima:
                        img = grass_mid
                        if esquerda_ar and not direita_ar:
                            img = grass_cl
                        elif direita_ar and not esquerda_ar:
                            img = grass_cr
                    else:
                        img = dirt_mid
                        if esquerda_ar and not direita_ar:
                            img = dirt_cl
                        elif direita_ar and not esquerda_ar:
                            img = dirt_cr
                    if img is None:
                        img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        img.fill((100, 200, 100))
                    self.tiles.add(Tile((x, y), img, TILE_SIZE))

                elif ch == 'B':
                    if box_img is None:
                        box_img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        pygame.draw.rect(box_img, (180, 140, 80), (4, 4, TILE_SIZE - 8, TILE_SIZE - 8), 0, border_radius=6)
                        pygame.draw.rect(box_img, (100, 70, 40), (4, 4, TILE_SIZE - 8, TILE_SIZE - 8), 2, border_radius=6)
                    self.tiles.add(Tile((x, y), box_img, TILE_SIZE))

                elif ch == 'C':
                    coin_img = self.assets['coin_image']
                    self.coins.add(Coin((x + TILE_SIZE // 2, y + TILE_SIZE // 2), coin_img, TILE_SIZE))

                elif ch == 'E':
                    self.flags.add(Tile((x, y - TILE_SIZE // 2), self.assets['flag'], TILE_SIZE))

                elif ch == 'P':
                    self.spawn = (x, y)
                    if self.player is None:
                        self.player = Player(self.spawn, self.assets['player_anims'])

        if self.player is None:
            self.player = Player(self.spawn, self.assets['player_anims'])

    def respawn(self):
        """Volta o player pro spawn."""
        self.lost = False
        if self.player:
            self.player.rect.topleft = self.spawn
            if hasattr(self.player, "vel"):
                self.player.vel.update(0, 0)

    def update(self, dt, keys):
        self.player.update(dt, self.tiles.sprites(), keys)
        self.coins.update(dt)

        # câmera com margem
        px = self.player.rect.centerx
        py = self.player.rect.centery
        esquerda = self.camera.x + CAMERA_MARGIN_X
        direita = self.camera.x + WIDTH - CAMERA_MARGIN_X
        if px < esquerda:
            self.camera.x = max(0, px - CAMERA_MARGIN_X)
        elif px > direita:
            self.camera.x = px - (WIDTH - CAMERA_MARGIN_X)

        topo = self.camera.y + CAMERA_MARGIN_Y
        fundo = self.camera.y + HEIGHT - CAMERA_MARGIN_Y
        if py < topo:
            self.camera.y = max(0, py - CAMERA_MARGIN_Y)
        elif py > fundo:
            self.camera.y = py - (HEIGHT - CAMERA_MARGIN_Y)

        if self.player.rect.top > KILL_PLANE_Y:
            self.lost = True

    def draw(self, surf):
        if hasattr(self, "parallax") and self.parallax:
            self.parallax.draw(surf, self.camera.x)
        else:
            surf.fill((25, 30, 45))

        for t in self.tiles:
            surf.blit(t.image, (t.rect.x - self.camera.x, t.rect.y - self.camera.y))
        for coin in self.coins:
            surf.blit(coin.image, (coin.rect.x - self.camera.x, coin.rect.y - self.camera.y))
        for f in self.flags:
            surf.blit(f.image, (f.rect.x - self.camera.x, f.rect.y - self.camera.y))

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
