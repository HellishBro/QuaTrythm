import pygame as pg
from pygame.window import Window
import mouseinfo

from quatrythm import QuaTrythm

pg.init()

def get_monitor(point):
    curr_x = 0
    sizes = pg.display.get_desktop_sizes()
    for i, window in enumerate(sizes):
        bbox = (curr_x, 0, curr_x + window[0], window[1])
        if pg.Rect(bbox).collidepoint(*point):
            return i, window, curr_x

        curr_x += window[0]

monitor_index, desktop_size, x_pos = get_monitor(mouseinfo.position())
size = desktop_size[0] / 5 * 3, desktop_size[1] / 5 * 3
window = Window("QuaTrythm", size, (
    x_pos + (desktop_size[0] - size[0]) // 2,
    (desktop_size[1] - size[1]) // 2
))
sc = window.get_surface()

game = QuaTrythm(sc, window)

dt = 1
clock = pg.Clock()

while True:
    dt = clock.tick() / 1000

    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            game.keydown(ev)
        elif ev.type == pg.KEYUP:
            game.keyup(ev)
        else:
            game.event(ev)

    sc.fill((0, 0, 0))

    game.update(dt)
    game.draw(sc)

    window.flip()
