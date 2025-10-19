import pygame, sys
from pathlib import Path
import random
from settings import WIDTH, HEIGHT, TITLE, FPS, TILE_SIZE
from utils import load_spritesheet
from level import Level

from score import load_score, add_points, subtract_points

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_VICTORY = "victory"
STATE_LOST = "lost"

class Button:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.hovered = False

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def was_clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN and
            event.button == 1 and
            self.rect.collidepoint(event.pos)
        )

    def draw(self, screen):
        cor = (120, 160, 255) if self.hovered else (80, 120, 200)
        pygame.draw.rect(screen, cor, self.rect, border_radius=8)
        label = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(label, label.get_rect(center=self.rect.center))

# ===== Geração Procedural =====
def _jump_tiles_from_settings():
    from settings import JUMP_VELOCITY, GRAVITY, TILE_SIZE
    v = abs(JUMP_VELOCITY)
    g = GRAVITY
    px_height = (v * v) / (2.0 * g)
    return max(2, int(px_height // TILE_SIZE))

def _derived_reach_tiles():
    from settings import JUMP_VELOCITY, GRAVITY, TILE_SIZE, PLAYER_SPEED
    v = abs(JUMP_VELOCITY)
    g = GRAVITY
    max_height_px = (v * v) / (2.0 * g)
    max_up_tiles = max(1, int(max_height_px // TILE_SIZE))
    airtime_frames = int((2.0 * v) / g)
    horiz_px = PLAYER_SPEED * airtime_frames
    max_gap_tiles = max(1, int(horiz_px // TILE_SIZE) - 1)
    return max_up_tiles, max_gap_tiles

def generate_level_layout(width_tiles=42, height_tiles=11, seed=None, gem_count=None):
    """Gera um layout de fase simples, jogável e com moedas."""
    rnd = random.Random(seed) if seed is not None else random
    MAX_UP, MAX_GAP = _derived_reach_tiles()
    W, H = width_tiles, height_tiles
    GY = H - 1

    grid = [['.' for _ in range(W)] for _ in range(H)]
    for x in range(W):
        grid[GY][x] = 'X'

    pit_ranges = []
    pit_x = 8
    while pit_x < W - 10:
        if rnd.random() < 0.3:
            pit_w = rnd.randint(2, 3)
            pit_start = pit_x
            pit_end = min(W - 4, pit_x + pit_w)
            for px in range(pit_start, pit_end):
                grid[GY][px] = '.'
            pit_ranges.append((pit_start, pit_end - 1))
            pit_x += pit_w + rnd.randint(6, 10)
        else:
            pit_x += rnd.randint(4, 8)

    def platform_crosses_pit(x0, x1, y):
        if y != GY:
            return False
        for pit_start, pit_end in pit_ranges:
            if not (x1 < pit_start or x0 > pit_end):
                return True
        return False

    spawn_x, spawn_y = 3, GY - 1
    grid[spawn_y][spawn_x] = 'P'

    def headroom_clear(y, x0, x1, hr=2):
        for x in range(max(1, x0), min(W - 1, x1) + 1):
            for k in range(1, hr + 1):
                yy = y - k
                if 0 <= yy < H:
                    grid[yy][x] = '.'

    def stamp_platform(y, x0, x1, hr=2):
        for x in range(max(1, x0), min(W - 1, x1) + 1):
            grid[y][x] = 'X'
        headroom_clear(y, x0, x1, hr)

    def chunk_flat(x0, y):
        length = rnd.randint(5, 9)
        x1 = x0 + length - 1
        if platform_crosses_pit(x0, x1, y):
            for pit_start, pit_end in pit_ranges:
                if x0 < pit_start <= x1:
                    x1 = pit_start - 1
                    break
            if x1 - x0 < 3:
                return x0, y, []
        stamp_platform(y, x0, x1, 2)
        mid = x0 + (x1 - x0) // 2
        return x1, y, [(mid, y - 1)]

    def chunk_gap(x0, y):
        gap = rnd.randint(2, min(MAX_GAP, 3))
        left_x1 = x0 + 2
        if platform_crosses_pit(x0, left_x1, y):
            return x0, y, []
        stamp_platform(y, x0, left_x1, 2)
        headroom_clear(y, x0 + 3, x0 + 2 + gap, 2)
        rx0 = x0 + 3 + gap
        rx1 = rx0 + 2
        if platform_crosses_pit(rx0, rx1, y):
            return left_x1, y, []
        stamp_platform(y, rx0, rx1, 2)
        return rx1, y, []

    def chunk_stairs_up(x0, y):
        import builtins
        rnd_steps = rnd.randint(2, min(3, MAX_UP))
        width = 3
        gem_spots = []
        cx, cy = x0, y
        for _ in range(rnd_steps):
            if platform_crosses_pit(cx, cx + width - 1, cy):
                break
            stamp_platform(cy, cx, cx + width - 1, 2)
            gem_spots.append((cx + 1, cy - 1))
            cx += width
            cy -= 1
        if not platform_crosses_pit(cx, cx + width - 1, cy):
            stamp_platform(cy, cx, cx + width - 1, 2)
        return cx + width - 1, cy, gem_spots

    def chunk_stairs_down(x0, y):
        max_steps_possible = GY - y - 1
        steps = rnd.randint(2, min(3, MAX_UP, max(2, max_steps_possible)))
        width = 3
        gem_spots = []
        cx, cy = x0, y
        for _ in range(steps):
            if cy >= GY:
                break
            if platform_crosses_pit(cx, cx + width - 1, cy):
                break
            stamp_platform(cy, cx, cx + width - 1, 2)
            if cy > 0:
                gem_spots.append((cx + 1, cy - 1))
            cx += width
            cy += 1
        cy = min(cy, GY)
        if not platform_crosses_pit(cx, cx + width - 1, cy):
            stamp_platform(cy, cx, cx + width - 1, 2)
        return cx + width - 1, cy, gem_spots

    def chunk_floater(x0, y):
        dy = rnd.randint(-min(MAX_UP, 2), min(MAX_UP, 2))
        ny = max(2, min(GY - 2, y + dy))
        length = rnd.randint(3, 5)
        x1 = x0 + length - 1
        if platform_crosses_pit(x0, x1, ny):
            ny = max(2, GY - 2)
        stamp_platform(ny, x0, x1, 2)
        return x1, ny, [(x0 + length // 2, ny - 1)]

    chunks = [("flat", 3), ("gap", 2), ("stairs_up", 2), ("stairs_down", 2), ("floater", 2)]

    x = spawn_x + 2
    y = spawn_y
    footholds = [(spawn_x, spawn_y)]

    while x < W - 8:
        available_chunks = chunks[:]
        if y >= GY - 2:
            available_chunks = [c for c in chunks if c[0] != "stairs_down"]
        if not available_chunks:
            available_chunks = [("flat", 1)]
        name = rnd.choices([c[0] for c in available_chunks], weights=[c[1] for c in available_chunks])[0]

        if name == "flat":
            nx, ny, gems = chunk_flat(x, y)
        elif name == "gap":
            nx, ny, gems = chunk_gap(x, y)
        elif name == "stairs_up":
            nx, ny, gems = chunk_stairs_up(x, y)
        elif name == "stairs_down":
            nx, ny, gems = chunk_stairs_down(x, y)
        else:
            nx, ny, gems = chunk_floater(x, y)

        if abs(ny - y) > MAX_UP or (nx - x) > (MAX_GAP * 2):
            nx, ny, gems = chunk_flat(x, y)

        footholds.append((nx, ny))
        x = nx + 2
        y = ny

    last_x, last_y = footholds[-1]
    exit_x = min(W - 3, last_x + min(MAX_GAP, W - 3 - last_x))
    exit_y = last_y
    grid[exit_y][exit_x] = 'E'

    if gem_count is None:
        gem_count = rnd.randint(3, 6)
    candidates = []
    for fx, fy in footholds[1:-1]:
        if fy - 2 >= 0 and grid[fy - 1][fx] == '.' and grid[fy - 2][fx] == '.':
            candidates.append((fx, fy - 1))
    rnd.shuffle(candidates)
    for (cx, cy) in candidates[:gem_count]:
        grid[cy][cx] = 'C'

    return [''.join(row) for row in grid]

def generate_level_pack(num_levels=3, width_tiles=42, height_tiles=11, seed=None):
    rnd = random.Random(seed) if seed is not None else random
    return [
        generate_level_layout(width_tiles, height_tiles, seed=rnd.randint(0, 1_000_000))
        for _ in range(num_levels)
    ]

# ===== Fim Procedural =====

def load_assets():
    # descobre uma pasta 'assets' válida
    import os
    here = Path(__file__).resolve().parent
    candidate_roots = [
        here / "assets",
        here.parent / "assets",
        Path(os.getcwd()) / "assets",
    ]
    ASSETS_ROOT = None
    for c in candidate_roots:
        if c.exists():
            ASSETS_ROOT = c
            break
    if ASSETS_ROOT is None:
        ASSETS_ROOT = here / "assets"

    def ap(*parts):
        return ASSETS_ROOT.joinpath(*parts)

    assets = {}

    # player (32x32 -> escala pra TILE_SIZE)
    assets['player_anims'] = {
        'idle': load_spritesheet(str(ap("player", "Idle.png")), 32, 32),
        'run' : load_spritesheet(str(ap("player", "Run.png")), 32, 32),
        'jump': load_spritesheet(str(ap("player", "Jump.png")), 32, 32),
        'fall': load_spritesheet(str(ap("player", "Fall.png")), 32, 32),
    }
    for k, frames in assets['player_anims'].items():
        assets['player_anims'][k] = [pygame.transform.scale(f, (TILE_SIZE, TILE_SIZE)) for f in frames]

    # tiles
    def _load_img(p):
        try:
            return pygame.image.load(p).convert_alpha()
        except Exception:
            return None

    tileset_dir = ap("tileset")
    assets['tiles'] = {
        'grass_mid'        : _load_img(str(tileset_dir / "grasstilemid.png")),
        'grass_corner_left': _load_img(str(tileset_dir / "grasstilecornerleft.png")),
        'grass_corner_right': _load_img(str(tileset_dir / "grasstilecornerright.png")),
        'dirt_mid'         : _load_img(str(tileset_dir / "dirttilemid.png")),
        'dirt_corner_left' : _load_img(str(tileset_dir / "dirttilecornerleft.png")),
        'dirt_corner_right': _load_img(str(tileset_dir / "dirttilecornerright.png")),
        'box'              : _load_img(str(tileset_dir / "box.png")),
        'platform'         : _load_img(str(tileset_dir / "platform.png")),
    }
    if not assets['tiles']['grass_mid']:
        fallback = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        fallback.fill((100, 200, 100))
        assets['tiles']['grass_mid'] = fallback

    # moeda e bandeira (placeholders se faltar arquivo)
    try:
        assets['coin_image'] = pygame.image.load(str(ap("coin.png"))).convert_alpha()
    except Exception:
        coin_h = 16
        coin_w = coin_h * 4
        surf = pygame.Surface((coin_w, coin_h), pygame.SRCALPHA)
        for i in range(4):
            pygame.draw.circle(surf, (255, 215, 0), (coin_h//2 + i*coin_h, coin_h//2), coin_h//2)
            pygame.draw.circle(surf, (255, 240, 170), (coin_h//2 + i*coin_h, coin_h//2), coin_h//3, 2)
        assets['coin_image'] = surf

    try:
        assets['flag'] = pygame.image.load(str(ap("flag.png"))).convert_alpha()
    except Exception:
        flag = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(flag, (80, 50, 30), (10, 8, 6, TILE_SIZE-12))
        pygame.draw.polygon(flag, (200, 40, 50), [(16, 10),(36, 18),(16, 26)])
        assets['flag'] = flag

    # parallax de fundo
    par_dir = ap("parallax", "forest")
    layers = []
    def add_layer(name, speed):
        p = par_dir / name
        img = _load_img(str(p))
        if img:
            layers.append({'image': img, 'speed': speed})
    add_layer("forest_sky.png",      0.05)
    add_layer("forest_moon.png",     0.08)
    add_layer("forest_mountain.png", 0.12)
    add_layer("forest_back.png",     0.22)
    add_layer("forest_mid.png",      0.35)
    add_layer("forest_short.png",    0.55)
    assets['parallax_layers'] = layers

    return assets

def draw_centered_text(screen, font, text, y, color=(240, 240, 240)):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, y))

def main():
    import os
    if os.path.basename(os.getcwd()) == "src":
        os.chdir(os.path.dirname(os.getcwd()))

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big = pygame.font.SysFont(None, 48)

    pontuacao = load_score()
    assets = load_assets()
    level_pack = []

    state = STATE_MENU
    level_index = 0
    level = None

    rodando = True
    while rodando:
        dt = clock.tick(FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                rodando = False

        keys = pygame.key.get_pressed()

        if state == STATE_MENU:
            screen.fill((20, 25, 40))
            draw_centered_text(screen, big, "Protótipo de Plataforma", HEIGHT // 2 - 100)

            btn_jogar = Button((WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50), "Começar", font)
            btn_sair  = Button((WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50), "Sair", font)

            mouse_pos = pygame.mouse.get_pos()
            btn_jogar.update_hover(mouse_pos)
            btn_sair.update_hover(mouse_pos)

            for e in events:
                if e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = STATE_PLAYING
                    level_pack = generate_level_pack(num_levels=3)
                    level_index = 0
                    level = Level(level_pack[level_index], assets)
                if btn_jogar.was_clicked(e):
                    state = STATE_PLAYING
                    level_pack = generate_level_pack(num_levels=3)
                    level_index = 0
                    level = Level(level_pack[level_index], assets)
                if btn_sair.was_clicked(e):
                    rodando = False

            btn_jogar.draw(screen)
            btn_sair.draw(screen)
            pygame.display.flip()
            continue

        if state == STATE_PLAYING:
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    state = STATE_PAUSED
                    break

            level.update(dt, keys)
            if level.lost:
                pontuacao = subtract_points(3)
                state = STATE_LOST
            level.try_collect()

            level.draw(screen)

            restantes = len(level.coins)
            txt = font.render(f"Nível {level_index + 1}/3  |  Moedas restantes: {restantes}", True, (20, 20, 20))
            screen.blit(txt, (16, 12))

            hud_score = font.render(f"Pontuação: {pontuacao}", True, (20, 20, 20))
            screen.blit(hud_score, (WIDTH - hud_score.get_width() - 16, 12))

            if restantes == 0 and level.at_exit():
                pontuacao = add_points(1)
                level_index += 1
                if level_index >= 3:
                    state = STATE_VICTORY
                else:
                    level = Level(level_pack[level_index], assets)

            pygame.display.flip()
            continue

        if state == STATE_PAUSED:
            screen.fill((0, 0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            draw_centered_text(screen, big, "Pausado", HEIGHT // 2 - 30)
            draw_centered_text(screen, font, "ESC = Voltar  •  Q = Sair", HEIGHT // 2 + 20)
            pygame.display.flip()

            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        state = STATE_PLAYING
                    elif e.key == pygame.K_q:
                        rodando = False
            continue

        if state == STATE_LOST:
            screen.fill((20, 25, 40))
            draw_centered_text(screen, big, "Você caiu!", HEIGHT // 2 - 100)
            btn_tentar = Button((WIDTH // 2 - 120, HEIGHT // 2 - 10, 240, 50), "Recomeçar do Nível 1", font)
            btn_sair  = Button((WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 50), "Sair", font)
            mouse_pos = pygame.mouse.get_pos()
            btn_tentar.update_hover(mouse_pos)
            btn_sair.update_hover(mouse_pos)
            btn_tentar.draw(screen)
            btn_sair.draw(screen)
            for e in events:
                if btn_tentar.was_clicked(e) or (e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_SPACE)):
                    state = STATE_PLAYING
                    level_pack = generate_level_pack(num_levels=3)
                    level_index = 0
                    level = Level(level_pack[level_index], assets)
                if btn_sair.was_clicked(e) or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                    rodando = False
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if state == STATE_VICTORY:
            screen.fill((10, 10, 10))
            draw_centered_text(screen, big, "Você Venceu!", HEIGHT // 2 - 20)
            draw_centered_text(screen, font, "ENTER = Menu  •  ESC = Sair", HEIGHT // 2 + 30)
            pygame.display.flip()

            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        rodando = False
                    if e.key == pygame.K_RETURN:
                        state = STATE_MENU
            continue

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
