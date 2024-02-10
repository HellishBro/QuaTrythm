import pygame as pg

def render_text(text, size, color, warp_length = 0):
    return pg.font.Font("assets/roboto.ttf", size).render(text, True, color, None, warp_length)
