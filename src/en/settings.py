
WIDTH, HEIGHT = 960, 540
TITLE = "Platformer Prototype"
FPS = 60

TILE_SIZE = 48  # Render size
GRAVITY = 0.8
JUMP_VELOCITY = -16
# Camera settings
CAMERA_MARGIN_X = 200   # how close player can go to screen edge before camera moves horizontally
CAMERA_MARGIN_Y = 100   # vertical margin before scrolling vertically
# If player falls below this, they respawn at the level spawn
KILL_PLANE_Y = HEIGHT + 200
# Horizontal speed the Player uses when moving left/right (see player.handle_input)
PLAYER_SPEED = 5


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
