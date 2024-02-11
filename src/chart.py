import pygame as pg

from src.lane import Lane
from src.config import Config
from src.note import TapNote, DragNote
from src.utils import render_text, gradient, Timer

import json5
import os
import random

WinWidth: int = 0
WinHeight: int = 0
Window: pg.Window = None

def init(sc: pg.Surface, window: pg.Window):
    global WinWidth, WinHeight, Window
    WinWidth, WinHeight = sc.get_size()
    Window = window

class Chart:
    def __init__(self, lanes: list[Lane], song: str, name: str, difficulty: str, bg_img: str):
        self.lanes = lanes
        for lane in self.lanes:
            lane.chart = self

        self.note_count = sum(len(lane.notes) for lane in self.lanes)
        self.notes_hit = 0
        self.combo = 0
        self.goods = 0
        self.perfects = 0
        self.bads = 0
        self.misses = 0
        self.early = 0
        self.late = 0
        self.max_combo = 0
        self.accuracy_offsets = []

        self.config = Config._()

        self.active_lane = 0
        self.timer = Timer()

        self.combo_text = render_text("COMBO", 24, (255, 255, 255))
        self.combo_text_size = 50

        pg.mixer.music.load(song)
        pg.mixer.music.set_volume(Config._().VOLUME_Music)
        self.song_started = False

        self.chart_name = name
        self.name_text = render_text(self.chart_name, 30, (255, 255, 255))
        self.chart_difficulty = difficulty
        self.difficulty_text = render_text(self.chart_difficulty, 30, (255, 255, 255))

        self.notes_odd_bg = gradient((0, 0, 0, 0), (125, 125, 125, 255), 0, (self.curr_lane.width / 4, WinHeight), pg.SRCALPHA)
        self.notes_even_bg = gradient((0, 0, 0, 0), (150, 150, 150, 255), 0, (self.curr_lane.width / 4, WinHeight), pg.SRCALPHA)
        self.score = 0

        self.show_result_screen = False

        self.background = pg.image.load(bg_img).convert_alpha()
        sw, sh = WinWidth / self.background.get_width(), WinHeight / self.background.get_height()
        scale = min(sw, sh)

        self.background = pg.transform.smoothscale_by(self.background, scale)
        self.background.set_alpha(Config._().BGDim)

    def update(self, dt: float):
        self.timer.tick(dt)

        for lane in self.lanes:
            lane.update(dt)

        self.max_combo = max(self.max_combo, self.combo)
        if self.combo_text_size > 50:
            self.combo_text_size -= dt * 100
        else:
            self.combo_text_size = 50

        if not self.timer.is_done("shake_time"):
            Window.position = (Window.position[0] + random.randint(-1, 1), Window.position[1] + random.randint(-1, 1))
        elif self.timer.is_done("shake_time"):
            Window.position = (pg.WINDOWPOS_CENTERED, pg.WINDOWPOS_CENTERED)
            self.timer.delete("shake_time")

        self.score = int(1_000_000 * (self.notes_hit / self.note_count))

        if sum([len(lane.notes) for lane in self.lanes]) == 0 and not self.timer.have("result_sleep"):
            self.timer.set("result_sleep", 2)
        if self.timer.have("result_sleep") and self.timer.is_done("result_sleep"):
            self.show_result_screen = True

    def draw(self, sc: pg.Surface):
        sc.blit(self.background, ((WinWidth - self.background.get_width()) / 2, (WinHeight - self.background.get_height()) / 2))

        offset = (self.curr_lane.x - 1) * (self.curr_lane.width / 2) + (WinWidth - self.curr_lane.width) / 2
        for i in range(4):
            sc.blit((self.notes_even_bg, self.notes_odd_bg)[i % 2], (offset + i * self.curr_lane.width / 4, 0))
        pg.draw.line(sc, (255, 255, 255), (0, self.curr_lane.hit_y), (WinWidth, self.curr_lane.hit_y))

        for lane in self.lanes:
            offset_x = (lane.x - self.curr_lane.x) * lane.width + (self.curr_lane.x - 1) * (self.curr_lane.width / 2)

            surface = pg.Surface((lane.width, WinHeight), pg.SRCALPHA)
            surface.fill((0, 0, 0, 0))
            lane.draw(surface)

            # actual positioning logic
            sc.blit(surface, (offset_x + (WinWidth - lane.width) / 2, 0))

        sc.blit(self.combo_text, ((WinWidth - self.combo_text.get_width()) // 2, 10))
        combo_text = render_text(str(self.combo), int(self.combo_text_size), (255, 255, 255))
        sc.blit(combo_text, ((WinWidth - combo_text.get_width()) // 2, 30))
        score_text = render_text(f"{self.score:,}", 30, (255, 255, 255))
        sc.blit(score_text, ((WinWidth - score_text.get_width()) / 2, WinHeight - score_text.get_height() - 10))

        sc.blit(self.name_text, (10, WinHeight - self.name_text.get_height() - 10))
        sc.blit(self.difficulty_text, (WinWidth - self.difficulty_text.get_width() - 10, WinHeight - self.difficulty_text.get_height() - 10))

    def keydown(self, ev: pg.Event):
        switches = (self.config.KEY_Lane1, self.config.KEY_Lane2, self.config.KEY_Lane3)
        if ev.key in switches:
            for i, switch in enumerate(switches):
                if ev.key == switch:
                    old_held = self.curr_lane.lanes_held.copy()
                    self.curr_lane.lanes_held = []
                    self.curr_lane.lanes_pressed = []
                    self.curr_lane = i
                    self.curr_lane.lanes_held = old_held

        else:
            self.curr_lane.keydown(ev)

    def keyup(self, ev: pg.Event):
        if ev.key not in (self.config.KEY_Lane1, self.config.KEY_Lane2, self.config.KEY_Lane3):
            self.curr_lane.keyup(ev)

    @property
    def curr_lane(self):
        return self.lanes[self.active_lane]

    @curr_lane.setter
    def curr_lane(self, new: int):
        self.active_lane = new

def parse_chart(file: str) -> Chart:
    with open(file) as f:
        json = json5.loads(f.read())

    json_lanes = json.get('lanes')
    lanes = []
    bpm = json.get('bpm', 0)
    mode = json.get('mode', 'time')

    for i, lane in enumerate(json_lanes):
        lanes.append(Lane([], i, 600))

        for note in lane:
            cls = (TapNote, DragNote)[note[0]]
            x = note[1]
            if mode == "time":
                time = note[2]
            else:
                time = 60 / bpm * note[2]

            lanes[-1].notes.append(cls(x, time))

        lanes[-1].update_notes()

    return Chart(lanes, os.path.join(os.path.dirname(file), json.get("song")), json.get('name'), json.get('difficulty'), os.path.join(os.path.dirname(file), json.get("background")))
