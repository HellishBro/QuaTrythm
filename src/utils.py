import pygame as pg
import math

from src.constants import *

def render_text(text, size, color, warp_length = 0) -> pg.Surface:
    return pg.font.Font("assets/roboto.ttf", size).render(text, True, color, None, warp_length)

def gradient(start_color, end_color, angle, size, flags = 0) -> pg.Surface:
    "Very expensive operation"
    surf = pg.Surface((1, 2), flags)
    surf.fill(start_color)
    surf.set_at((0, 1), end_color)
    surf = pg.transform.rotate(surf, angle)
    surf = pg.transform.smoothscale(surf, size)
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

    def get(self, name):
        return self.timers.get(name, 0)

def rank_image(score, fc=False):
    ImgF = pg.image.load("assets/grade/f.png").convert_alpha()
    ImgD = pg.image.load("assets/grade/d.png").convert_alpha()
    ImgC = pg.image.load("assets/grade/c.png").convert_alpha()
    ImgB = pg.image.load("assets/grade/b.png").convert_alpha()
    ImgA = pg.image.load("assets/grade/a.png").convert_alpha()
    ImgV = pg.image.load("assets/grade/v.png").convert_alpha()
    ImgS = pg.image.load("assets/grade/s.png").convert_alpha()
    ImgFC = pg.image.load("assets/grade/fc.png").convert_alpha()
    ImgAP = pg.image.load("assets/grade/ap.png").convert_alpha()

    rank = Ranks.F
    if score >= 600_000:
        rank = Ranks.D
    if score >= 700_000:
        rank = Ranks.C
    if score >= 820_000:
        rank = Ranks.B
    if score >= 880_000:
        rank = Ranks.A
    if score >= 920_000:
        rank = Ranks.S
    if score >= 960_000:
        rank = Ranks.V
    if fc:
        rank = Ranks.FC
    if score == 1_000_000:
        rank = Ranks.AP

    rank_img: pg.Surface = None
    match rank:
        case Ranks.F:
            rank_img = ImgF
        case Ranks.D:
            rank_img = ImgD
        case Ranks.C:
            rank_img = ImgC
        case Ranks.B:
            rank_img = ImgB
        case Ranks.A:
            rank_img = ImgA
        case Ranks.S:
            rank_img = ImgS
        case Ranks.V:
            rank_img = ImgV
        case Ranks.FC:
            rank_img = ImgFC
        case Ranks.AP:
            rank_img = ImgAP

    return rank, rank_img