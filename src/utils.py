import pygame as pg
import math

def render_text(text, size, color, warp_length = 0) -> pg.Surface:
    return pg.font.Font("assets/roboto.ttf", size).render(text, True, color, None, warp_length)

def gradient(start_color, end_color, angle, size, flags = 0) -> pg.Surface:
    "Very expensive operation"
    surf = pg.Surface((1, 2), flags)
    surf.fill(start_color)
    surf.set_at((0, 1), end_color)
    surf = pg.transform.smoothscale(surf, size)
    surf = pg.transform.rotate(surf, angle)
    return surf

def ease_sine(start, end, percentage) -> float:
    return (-math.cos(math.pi * percentage) + 1) / 2 * (end - start) + start

class Timer:
    def __init__(self):
        self.timers = {}

    def set(self, name, countdown):
        self.timers[name] = countdown

    def tick(self, segment):
        for k, v in self.timers.items():
            self.timers[k] -= segment

    def have(self, name):
        return name in self.timers.keys()

    def is_done(self, name):
        return self.timers.get(name, 0) <= 0

    def delete(self, name):
        try:
            del self.timers[name]
        except KeyError:
            pass
