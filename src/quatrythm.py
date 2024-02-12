import pygame as pg

from src.base_scene import Scene
from src.chart import Chart, parse_chart
from src.result_screen import ResultScreen
from src.config import Config
from src import note, chart, lane, result_screen

class QuaTrythm(Scene):
    "The whole entire game in a class because why not"
    def __init__(self, sc: pg.Surface, window: pg.Window):
        self.sc = sc
        self.window = window

        note.init()
        result_screen.init(self.sc)
        lane.init(self.sc)
        chart.init(self.sc, self.window)

        self.active_chart: Chart = None

        self.current_scene: Scene = None

    def update(self, dt: float):
        self.current_scene.update(dt)

        if self.active_chart and self.active_chart.show_result_screen:
            self.current_scene = ResultScreen(self.active_chart)
            self.active_chart = None

    def draw(self, sc: pg.Surface):
        self.current_scene.draw(sc)

    def keydown(self, ev: pg.Event):
        self.current_scene.keydown(ev)

    def keyup(self, ev: pg.Event):
        self.current_scene.keyup(ev)

    def event(self, ev: pg.Event) -> bool:
        scene_ev_parse = self.current_scene.event(ev)
        if scene_ev_parse: return scene_ev_parse

        if ev.type == pg.MOUSEWHEEL:
            Config._().VOLUME_Music = max(0, min(100, Config._().VOLUME_Music + ev.y * 0.1))
            pg.mixer.music.set_volume(Config._().VOLUME_Music)
