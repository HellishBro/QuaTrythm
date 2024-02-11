import pygame as pg
from pygame.window import Window

from src import note, chart, lane, result_screen

pg.mixer.pre_init(44100, 16, 2,  1024)
pg.init()
window = Window("QuaTrythm", (1000, 600))
sc = window.get_surface()

note.init()
result_screen.init(sc)
lane.init(sc)
chart.init(sc, window)

current_scene = chart.parse_chart(r"C:\Users\helli\PycharmProjects\QuaTrythm\src\charts\test.json5")

dt = 1
clock = pg.Clock()

while True:
    dt = clock.tick() / 1000

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            exit()
        elif ev.type == pg.KEYDOWN:
            current_scene.keydown(ev)
        elif ev.type == pg.KEYUP:
            current_scene.keyup(ev)

    sc.fill((0, 0, 0))

    current_scene.update(dt)
    current_scene.draw(sc)

    if isinstance(current_scene, chart.Chart) and current_scene.show_result_screen:
        current_scene = result_screen.ResultScreen(current_scene)

    window.flip()
