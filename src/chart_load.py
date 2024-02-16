import pygame as pg

from utils import render_text
from chart import parse_chart, Chart

from base_scene import Scene

class ChartLoading(Scene):
    def __init__(self, chart_file: str):
        self.chart_file = chart_file
        self.loading_text = render_text("Loading...", 50, (255, 255, 255))
        self.cooldown = 0
        self.parsed_chart: Chart = None

    def draw(self, sc: pg.Surface):
        sc.blit(self.loading_text, (sc.get_width() - self.loading_text.get_width() - 25, sc.get_height() - self.loading_text.get_height() - 25))

    def update(self, dt: float):
        if self.cooldown is not None:
            if self.cooldown >= 1.25:
                self.cooldown = None
                self.parsed_chart = parse_chart(self.chart_file)

            else:
                self.cooldown += dt
