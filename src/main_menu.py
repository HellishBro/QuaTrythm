import pygame as pg

from base_scene import Scene
from utils import render_text, gradient, Timer, play_sound, path
from config import Config

import json5
import random
from pathlib import Path
import math

WinWidth, WinHeight = 0, 0
def init(sc: pg.Surface):
    global WinWidth, WinHeight
    WinWidth, WinHeight = sc.get_size()

class MainMenu(Scene):
    def __init__(self):
        self.title_text = render_text("QuaTrythm", 100, (255, 255, 255))
        self.start_text = render_text("[SPACE] to start", 40, (255, 255, 255))
        self.title_y = (WinHeight - self.title_text.get_height()) * 0.3
        self.start_y = self.title_y + self.title_text.get_height() + 100
        self.title_constant = random.randint(3, 10)

        self.timer = Timer()

        with open(path("charts/", "charts.json5")) as f:
            charts = json5.loads(f.read())["charts"]
        random_chart = random.choice(charts)
        self.song_text = render_text(f"Music : {random_chart['name']} - {random_chart['artist']}", 30, (255, 255, 255))
        pg.mixer.music.load(path("charts/", random_chart["directory"], "song.mp3"))
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(Config._().VOLUME_Music)

        rand_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 125)
        self.gradient = gradient((0, 0, 0, 0), rand_color, 0, (WinWidth, WinHeight), pg.SRCALPHA)
        self.other_gradient = pg.transform.rotate(self.gradient, 180)
        self.other_gradient.set_alpha(75)

        self.info_text = render_text(
            "Made for Rhythm Jam 2024! Thanks to all the song artists for allowing me to use your song!",
            25, tuple(map(lambda n: n * 0.75,rand_color)), int(WinWidth / 4)
        )

        self.time = 0
        self.done = False

    def update(self, dt: float):
        self.timer.tick(dt)
        self.time += dt

        self.title_y = (WinHeight - self.title_text.get_height()) * 0.3 + math.sin(self.time * math.pi) * (WinWidth / 32)
        self.start_y = (WinHeight - self.title_text.get_height()) * 0.3 + self.title_text.get_height() + 100 + (math.cos(self.time * self.title_constant)) * (WinWidth / 32)

    def draw(self, sc: pg.Surface):
        sc.blit(self.gradient, (0, 0))
        sc.blit(self.other_gradient, (0, 0))
        sc.blit(self.song_text, (10, WinHeight - self.song_text.get_height() - 10))
        sc.blit(self.title_text, ((WinWidth - self.title_text.get_width()) / 2, self.title_y))
        sc.blit(self.start_text, ((WinWidth - self.start_text.get_width()) / 2, self.start_y))

        sc.blit(self.info_text, (WinWidth - self.info_text.get_width() - 10, WinHeight - self.info_text.get_height() - 10))

    def keydown(self, ev: pg.Event):
        if ev.key in (pg.K_SPACE, pg.K_RETURN):
            self.done = True
            pg.mixer.music.fadeout(1000)
            play_sound("assets/enter.wav")
