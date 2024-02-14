import os.path

import pygame as pg

from src.base_scene import Scene
from src.chart import Chart, parse_chart
from src.result_screen import ResultScreen
from src.song_select import SongSelect

from src.config import Config
from src.utils import Timer, render_text, gradient
from src.user import User

from src import note, chart, lane, result_screen, song_select

class QuaTrythm(Scene):
    "The whole entire game in a class because why not"
    def __init__(self, sc: pg.Surface, window: pg.Window):
        self.sc = sc
        self.window = window

        note.init()
        result_screen.init(self.sc)
        lane.init(self.sc)
        song_select.init(self.sc, self.window)

        chart.init(self.sc, self.window)

        self.active_chart: Chart = None
        self.chart_loaded = False
        self.loaded_song_id = 0

        self.current_scene: Scene = None
        self.current_scene = SongSelect()

        self.timer = Timer()
        self.volume_gradient: pg.Surface = None
        self.volume_change_type = 0 # 0 music, 1 sfx

        User.load()
        Config.load()
        pg.mixer.music.set_volume(Config._().VOLUME_Music)

    def load_chart(self, song_select_scene: SongSelect):
        chart = parse_chart(song_select_scene.current_song.chart_path)
        self.active_chart = chart
        self.chart_loaded = True

    def update(self, dt: float):
        self.timer.tick(dt)
        self.current_scene.update(dt)

        if self.active_chart and self.active_chart.show_result_screen:
            self.current_scene = ResultScreen(self.active_chart)
            User._().set_score(self.loaded_song_id, self.active_chart.score)
            if self.active_chart.combo == self.active_chart.note_count:
                User._().set_fc(self.loaded_song_id)
            User._().save()
            self.active_chart = None

        if isinstance(self.current_scene, SongSelect):
            if self.current_scene.begin_load_chart:
                self.load_chart(self.current_scene)
            if self.current_scene.done and self.chart_loaded:
                self.loaded_song_id = self.current_scene.current_song.id
                self.current_scene = self.active_chart

        if isinstance(self.current_scene, ResultScreen):
            if self.current_scene.done:
                self.current_scene = SongSelect()
                self.current_scene.update(dt)

    def draw(self, sc: pg.Surface):
        self.current_scene.draw(sc)

        if self.timer.have("volume_fade"):
            if self.timer.is_done("volume_fade"):
                self.timer.delete("volume_fade")
            else:
                alpha = min(self.timer.get("volume_fade") * 255, 255)
                volume_text = render_text("Music Volume" if self.volume_change_type == 0 else "Sound Volume", 30, (255, 255, 255))
                bar = pg.Surface((self.sc.get_width() / 2, 10), pg.SRCALPHA)
                bar.fill((0, 0, 0))
                bar.blit(self.volume_gradient, (0, 0))

                volume_text.set_alpha(alpha)
                bar.set_alpha(alpha)

                sc.blit(volume_text, (25, 25))
                sc.blit(bar, (25, 25 + volume_text.get_height() + 5))

    def keydown(self, ev: pg.Event):
        self.current_scene.keydown(ev)

    def keyup(self, ev: pg.Event):
        self.current_scene.keyup(ev)

    def event(self, ev: pg.Event) -> bool:
        if ev.type == pg.QUIT:
            User._().save()
            Config._().save()
            quit()

        keys = pg.key.get_pressed()

        scene_ev_parse = self.current_scene.event(ev)
        if scene_ev_parse: return scene_ev_parse

        if ev.type == pg.MOUSEWHEEL:
            multiplier = 0.1
            if keys[pg.K_LSHIFT]:
                multiplier = 0.05

            if keys[pg.K_LCTRL]:
                volume = max(0, min(1, Config._().VOLUME_Sound + ev.y * multiplier))
                Config._().VOLUME_Sound = volume
                self.volume_change_type = 1
            else:
                volume = max(0, min(1, Config._().VOLUME_Music + ev.y * multiplier))
                Config._().VOLUME_Music = volume
                pg.mixer.music.set_volume(volume)
                self.volume_change_type = 0

            self.timer.set("volume_fade", 1.5)
            self.volume_gradient = gradient((200, 200, 200, 255), (125, 125, 125, 150), 90, (volume * (self.sc.get_width() / 2), 10))
