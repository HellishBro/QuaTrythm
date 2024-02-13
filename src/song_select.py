import pygame as pg

from src.base_scene import Scene
from src.utils import render_text, gradient, Timer, rank_image
from src.user import User

from src.constants import *

import json5

WinWidth, WinHeight = (0, 0)
def init(sc: pg.Surface):
    global WinWidth, WinHeight
    WinWidth, WinHeight = sc.get_size()

class Song:
    def __init__(self, name, chart, artist, charter, highlight, id):
        self.name = name
        self.chart = chart
        self.artist = artist
        self.charter = charter
        self.id = id

        self.highlight_start, self.highlight_end = highlight

        with open("charts/" + self.chart) as f:
            chart_info = json5.loads(f.read())

        self.song = chart_info["song"]
        self.difficulty = chart_info["difficulty"]
        self.background = chart_info["background"]
        self.bpm = chart_info["bpm"]

    @classmethod
    def from_json(cls, json: dict):
        return cls(json["name"], json["chart"], json["artist"], json["charter"], json["song_highlight"], json["id"])

class SongSelect(Scene):
    def __init__(self):
        with open("charts/charts.json5") as f:
            data = json5.loads(f.read())

        self.songs: list[Song] = []
        for chart in data["charts"]:
            self.songs.append(Song.from_json(chart))

        self.selected_chart = 0
        self.song_list_height = 100
        self.song_list_width = WinWidth / 3

        self.selected_song_gradient = gradient((200, 200, 200, 255), (0, 0, 0, 0), 90, (self.song_list_width, self.song_list_height))
        self.user = User._()
        self.timer = Timer()

        self.change_music = True
        self.song_banner: pg.Surface = None
        self.current_song_score = 0
        self.current_song_score_image: pg.Surface = None
        self.current_song_score_gradient: pg.Surface = None

        self.done = False
        self.begin_load_chart = False

    @property
    def current_song(self):
        return self.songs[self.selected_chart]

    def update(self, dt: float):
        self.timer.tick(dt)

        if self.change_music:
            pg.mixer.music.fadeout(500)
            self.timer.set("song_play", 0.5)
            self.change_music = False
            self.song_banner = pg.image.load("charts/" + self.current_song.background).convert_alpha()

            sw, sh = (WinWidth / 2) / self.song_banner.get_width(), (WinHeight / 2) / self.song_banner.get_height()
            scale = min(sw, sh)
            self.song_banner = pg.transform.scale_by(self.song_banner, scale)

            self.current_song_score = User._().get_score(self.current_song.id)
            rank, self.current_song_score_image = rank_image(self.current_song_score, User._().get_fc(self.current_song.id))
            self.current_song_score_image = pg.transform.scale_by(self.current_song_score_image, 0.25)
            self.current_song_score_gradient = gradient((0, 0, 0, 0), RANK_COLORS[rank], 90, (WinWidth / 2, WinHeight), pg.SRCALPHA)

        if self.timer.have("song_play") and self.timer.is_done("song_play"):
            pg.mixer.music.load("charts/" + self.current_song.song)
            pg.mixer.music.play()
            pg.mixer.music.rewind()
            pg.mixer.music.set_pos(self.current_song.highlight_start)
            self.timer.set("rewind", self.current_song.highlight_end - self.current_song.highlight_start)
            self.timer.delete("song_play")

        if self.timer.is_done("rewind") and not self.timer.have("song_play"):
            pg.mixer.music.rewind()
            pg.mixer.music.set_pos(self.current_song.highlight_start)
            self.timer.set("rewind", self.current_song.highlight_end - self.current_song.highlight_start)

        if self.timer.have("enter") and self.timer.is_done("enter"):
            self.timer.delete("enter")
            self.done = True

    def draw(self, sc: pg.Surface):
        sc.blit(self.current_song_score_gradient, (WinWidth / 2, 0))
        sc.blit(pg.transform.rotate(self.current_song_score_gradient, 180), (0, 0))

        for i, song in enumerate(self.songs):
            offset = i - self.selected_chart
            offset *= self.song_list_height
            offset += (WinHeight - self.song_list_height) / 2

            song_text = render_text(song.name, self.song_list_height // 2, (255, 255, 255))
            if song_text.get_width() > self.song_list_width - 25:
                scale_by = (self.song_list_width - 25) / song_text.get_width()
                song_text = pg.transform.scale_by(song_text, scale_by)

            if self.selected_chart == i:
                sc.blit(self.selected_song_gradient, (0, offset))

            sc.blit(song_text, (25, offset + song_text.get_height() / 2))

        banner_x, banner_y = WinWidth / 5 * 3, (WinHeight - self.song_banner.get_height()) / 5 * 2
        sc.blit(self.song_banner, (banner_x, banner_y))

        charter_text = render_text("Charter: " + self.current_song.charter, 24, (255, 255, 255))
        sc.blit(charter_text, (banner_x, banner_y - charter_text.get_height() - 5))
        artist_test = render_text("Artist: " + self.current_song.artist, 24, (255, 255, 255))
        sc.blit(artist_test, (banner_x, banner_y - artist_test.get_height() - charter_text.get_height() - 10))

        score_text = render_text(f"{self.current_song_score:07d}", 30, (255, 255, 255))
        sc.blit(score_text, (banner_x, banner_y + self.song_banner.get_height() + 5))
        sc.blit(self.current_song_score_image, (banner_x + self.song_banner.get_width() - self.current_song_score_image.get_width(), banner_y + self.song_banner.get_height() + 5))

        sc.blit(render_text(self.current_song.difficulty, 30, (255, 255, 255)), (banner_x + 5, banner_y + 5))

    def keydown(self, ev: pg.Event):
        if ev.key == pg.K_DOWN:
            self.selected_chart += 1
            self.selected_chart %= len(self.songs)
            self.change_music = True
            pg.mixer.Sound("assets/click.wav").play()
        elif ev.key == pg.K_UP:
            self.selected_chart -= 1
            self.selected_chart %= len(self.songs)
            self.change_music = True
            pg.mixer.Sound("assets/click.wav").play()

        elif ev.key in (pg.K_SPACE, pg.K_RETURN):
            pg.mixer.Sound("assets/enter.wav").play()
            pg.mixer.music.fadeout(1000)
            self.timer.set("enter", 1)
            self.begin_load_chart = True
