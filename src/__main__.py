import pygame as pg
from pygame.window import Window

from src.quatrythm import QuaTrythm
from src.chart import parse_chart

pg.init()
desktop_size = pg.display.get_desktop_sizes()[0]
window = Window("QuaTrythm", (desktop_size[0] / 4 * 3, desktop_size[1] / 4 * 3))
sc = window.get_surface()

game = QuaTrythm(sc, window)
game.active_chart = parse_chart(r"C:\Users\helli\PycharmProjects\QuaTrythm\src\charts\test.json5")
game.current_scene = game.active_chart

dt = 1
clock = pg.Clock()

while True:
    dt = clock.tick() / 1000

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            exit()
        elif ev.type == pg.KEYDOWN:
            game.keydown(ev)
        elif ev.type == pg.KEYUP:
            game.keyup(ev)
        else:
            game.event(ev)

    sc.fill((0, 0, 0))

    game.update(dt)
    game.draw(sc)

    window.flip()
