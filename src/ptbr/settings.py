# Config do jogo
WIDTH, HEIGHT = 960, 540
TITLE = "Protótipo de Plataforma"
FPS = 60

TILE_SIZE = 48
GRAVITY = 0.8
JUMP_VELOCITY = -16

# câmera segue o player com folga
CAMERA_MARGIN_X = 200
CAMERA_MARGIN_Y = 100

# caiu = morreu
KILL_PLANE_Y = HEIGHT + 200

# velocidade horizontal do player
PLAYER_SPEED = 5

# níveis de exemplo (não usados quando gera procedural)
LEVELS = [
    [
        "........................................",
        "........................................",
        ".............C..........................",
        "....................C...................",
        "...............XXX......................",
        "........................................",
        ".....P.........................C........",
        "XXXXXXXXXXXX....XXXX...........XXXXXXX..",
        "...............XX....C..................",
        "........E....XXXXX............XXXXXXX...",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
    [
        "........................................",
        "........................................",
        "..................C.....................",
        "........................................",
        ".............XXX........................",
        "........................C...............",
        "....P...............XXXXX...............",
        "XXXXXXX...C..................XXXX.......",
        ".........XXXXXX..................E......",
        "........................................",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ],
]
