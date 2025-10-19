import pygame

def load_spritesheet(path, frame_w, frame_h):
    """Corta spritesheet horizontal simples."""
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    sheet_w, sheet_h = sheet.get_size()
    for x in range(0, sheet_w, frame_w):
        frame = sheet.subsurface(pygame.Rect(x, 0, frame_w, frame_h))
        frames.append(frame)
    return frames

def scale_surface(surf, scale):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (int(w*scale), int(h*scale)))
