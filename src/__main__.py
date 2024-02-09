import pygame as pg

from src import note, chart, lane
from src.note import TapNote, DragNote

pg.init()
sc = pg.display.set_mode((1000, 600))

note.init()
lane.init(sc)
chart.init(sc)
this_chart = chart.parse_chart(r"C:\Users\helli\PycharmProjects\QuaTrythm\src\charts\test.json5")

dt = 1
clock = pg.Clock()

while True:
    dt = clock.tick(120) / 1000

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            exit()
        elif ev.type == pg.KEYDOWN:
            this_chart.keydown(ev)
        elif ev.type == pg.KEYUP:
            this_chart.keyup(ev)

    sc.fill((0, 0, 0))

    this_chart.update(dt)
    this_chart.draw(sc)

    pg.display.update()
