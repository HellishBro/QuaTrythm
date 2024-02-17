import pygame as pg

from lane import Lane
from config import Config
from note import TapNote, DragNote
from utils import render_text, gradient, Timer, play_sound, path
from base_scene import Scene

import json5
import os
from pathlib import Path
import random

WinWidth: int = 0
WinHeight: int = 0
Window: pg.Window = None

def init(sc: pg.Surface, window: pg.Window):
    global WinWidth, WinHeight, Window
    WinWidth, WinHeight = sc.get_size()
    Window = window

class Chart(Scene):
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
        self.total_time = max([max([note.time for note in lane.notes] if lane.notes else [0]) for lane in self.lanes])

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
        self.quit = False
        self.pause = False
        self.restart = False

        self.unpause_button = pg.transform.scale_by(pg.image.load(path("assets/", "continue.png")).convert_alpha(), 0.75)
        self.unpause_button_x = (WinWidth - self.unpause_button.get_width()) / 2
        self.quit_button = pg.image.load(path("assets/", "quit.png")).convert_alpha()
        self.quit_button_x = self.unpause_button_x - self.quit_button.get_width() - 50
        self.restart_button = pg.image.load(path("assets/", "restart.png")).convert_alpha()
        self.restart_button_x = self.unpause_button_x + self.unpause_button.get_width() + 50

        self.pause_menu_selection = 1

        self.background = pg.image.load(bg_img).convert_alpha()
        sw, sh = WinWidth / self.background.get_width(), WinHeight / self.background.get_height()
        scale = min(sw, sh)

        self.background = pg.transform.smoothscale_by(self.background, scale)
        self.background.set_alpha(Config._().BGDim)
        self.black = pg.Surface((WinWidth, WinHeight))
        self.black.fill((0, 0, 0))

        self.time = -2

    def update(self, dt: float):
        if self.pause:
            return

        self.timer.tick(dt)
        self.time += dt

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
        pg.draw.line(sc, (255, 255, 255), (0, self.curr_lane.hit_y), (WinWidth, self.curr_lane.hit_y), 5)
        pg.draw.line(sc, (0, 255, 255), (0, self.curr_lane.hit_y), (self.time / self.total_time * WinWidth, self.curr_lane.hit_y), 5)

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

        if self.timer.have("result_sleep"):
            alpha = self.timer.get("result_sleep") / 2 * 255
            sc.set_alpha(alpha)
        elif self.show_result_screen:
            sc.set_alpha(255)

        if self.pause:
            sc.blit(self.black, (0, 0))
            sc.blit(self.unpause_button, (self.unpause_button_x, (WinHeight - self.unpause_button.get_height()) / 2))
            restart_button_y = (WinHeight - self.restart_button.get_height()) / 2
            sc.blit(self.restart_button, (self.restart_button_x, restart_button_y))
            sc.blit(self.quit_button, (self.quit_button_x, (WinHeight - self.quit_button.get_height()) / 2))

            xes = [self.restart_button_x, self.quit_button_x, self.unpause_button_x - 10]
            box_x = xes[self.pause_menu_selection]
            pg.draw.rect(sc, (255, 255, 255), (box_x, restart_button_y, *self.restart_button.get_size()), 5)

            paused_text = render_text("Paused", 40, (255, 255, 255))
            sc.blit(paused_text, ((WinWidth - paused_text.get_width()) / 2, restart_button_y - paused_text.get_height() - 50))

    def keydown(self, ev: pg.Event):
        switches = (self.config.KEY_Lane1, self.config.KEY_Lane2, self.config.KEY_Lane3)
        if ev.key in switches and not self.pause:
            for i, switch in enumerate(switches):
                if ev.key == switch:
                    old_held = self.curr_lane.lanes_held.copy()
                    self.curr_lane.lanes_held = []
                    self.curr_lane.lanes_pressed = []
                    self.curr_lane = i
                    self.curr_lane.lanes_held = old_held

        elif ev.key == pg.K_ESCAPE:
            self.pause = not self.pause
            if self.pause:
                self.black.set_alpha(125)
                pg.mixer.music.pause()
                self.pause_menu_selection = 2
                Window.position = (pg.WINDOWPOS_CENTERED, pg.WINDOWPOS_CENTERED)
            else:
                self.black.set_alpha(0)
                pg.mixer.music.unpause()

        elif ev.key == pg.K_r:
            self.restart = True

        elif self.pause and ev.key in (pg.K_LEFT, pg.K_RIGHT, pg.K_RETURN, pg.K_SPACE):
            if ev.key in (pg.K_RETURN, pg.K_SPACE):
                if self.pause_menu_selection == 1:
                    self.quit = True
                elif self.pause_menu_selection == 2:
                    self.pause = False
                    self.black.set_alpha(0)
                    pg.mixer.music.unpause()
                elif self.pause_menu_selection == 0:
                    self.restart = True
            else:
                play_sound("assets/click.wav")
                self.pause_menu_selection += (ev.key == pg.K_RIGHT) - (ev.key == pg.K_LEFT)
                self.pause_menu_selection %= 3

        elif not self.pause:
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

    for i, lane in enumerate(json_lanes):
        lanes.append(Lane([], i, Config._().ScrollSpeed))

        for note in lane:
            cls = (TapNote, DragNote)[note[0]]
            x = note[1]
            time = 60 / bpm * note[2]

            lanes[-1].notes.append(cls(x, time))

        lanes[-1].update_notes()

    directory_path = Path(os.path.dirname(file))
    return Chart(lanes, directory_path / "song.mp3" , json.get('name'), json.get('difficulty'), directory_path / "thumbnail.jpg")
