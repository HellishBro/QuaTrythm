import pygame as pg

from src.config import Config
from src.note import Note, TapNote, DragNote

from src.utils import gradient

BaseNoteWidth: int = 0
BaseNoteHeight: int = 0
WinWidth: int = 0
WinHeight: int = 0

NoteHitEffect: pg.Surface = None
IncomingGradient: pg.Surface = None

def init(sc: pg.Surface):
    global BaseNoteWidth, BaseNoteHeight, WinWidth, WinHeight, NoteHitEffect, IncomingGradient
    from src.note import BaseNoteDimensions as BND
    BaseNoteWidth, BaseNoteHeight = BND
    WinWidth, WinHeight = sc.get_size()
    NoteHitEffect = gradient((0, 125, 125, 0), (255, 255, 0, 125), 0, (BaseNoteWidth, BaseNoteWidth * 2), pg.SRCALPHA)
    IncomingGradient = gradient((150, 150, 150, 255), (0, 0, 0, 0), 0, (BaseNoteWidth * 4, BaseNoteWidth * 2), pg.SRCALPHA)

PERFECT_TIMING = 0.05
GOOD_TIMING = 0.1
BAD_TIMING = 0.2

class Lane:
    def __init__(self, notes: list[Note], x: int, speed: float):
        self.notes = notes

        self.config = Config._()

        self.x = x
        self.speed = speed

        self.scroll = -self.speed * 2

        self.lanes_held = []
        self.lanes_pressed = []

        for note in self.notes:
            note.y = note.time * self.speed - self.scroll

        self.width = BaseNoteWidth * 4

        self.chart = None
        self.note_press_effects = []
        # [[lane, accuracy={0 perfect, 1 good}, lifetime], ...]

        self.incoming = False

    def update_notes(self):
        for note in self.notes:
            note.y = note.time * self.speed - self.scroll

    def __repr__(self):
        return f"Lane{self.notes}"

    def update(self, dt: float):
        self.scroll += dt * self.speed
        if self.scroll >= 0 and not self.chart.song_started:
            pg.mixer.music.play()
            self.chart.song_started = True

        self.incoming = False
        for i, note in enumerate(self.notes):
            note.y -= self.speed * dt
            if not self.incoming and note.y / self.speed <= 2:
                self.incoming = True

            if note.x in self.lanes_pressed and isinstance(note, TapNote):
                time_offset = abs(note.y / self.speed)
                if time_offset <= PERFECT_TIMING:
                    self.chart.notes_hit += 1
                    self.note_press_effects.append([note.x, 0, 0])
                    self.chart.perfects += 1
                elif time_offset <= GOOD_TIMING:
                    self.chart.notes_hit += 0.65
                    self.note_press_effects.append([note.x, 1, 0])
                    self.chart.goods += 1
                    if note.y > 0: self.chart.early += 1
                    else: self.chart.late += 1
                elif time_offset <= BAD_TIMING:
                    self.chart.combo = 0
                    self.chart.accuracy_offsets.append(note.y / self.speed)
                    self.chart.timer.set("shake_time", 0.25)
                    self.lanes_pressed.remove(note.x)
                    self.notes.remove(note)
                    self.chart.bads += 1
                    if note.y > 0: self.chart.early += 1
                    else: self.chart.late += 1
                    continue
                else:
                    continue

                note.play_sound()
                self.chart.combo += 1
                self.chart.accuracy_offsets.append(note.y / self.speed)
                self.lanes_pressed.remove(note.x)
                self.notes.remove(note)
                self.chart.combo_text_size = 75

            elif note.x in self.lanes_held and isinstance(note, DragNote):
                if note.y <= 0 and abs(note.y / self.speed) < BAD_TIMING:
                    self.chart.combo += 1
                    self.chart.notes_hit += 1
                    self.chart.perfects += 1
                    note.play_sound()
                    self.note_press_effects.append([note.x, 0, 0])

                    self.notes.remove(note)
                    self.chart.combo_text_size = 75

            elif (note.y / self.speed) < -BAD_TIMING:
                self.chart.combo = 0
                self.chart.timer.set("shake_time", 0.25)
                self.chart.misses += 1
                self.notes.remove(note)

        for press_effect in self.note_press_effects:
            if press_effect[2] >= 0.5:
                self.note_press_effects.remove(press_effect)
            else:
                press_effect[2] += dt

        self.lanes_pressed = []

    def draw(self, sc: pg.Surface):
        if self.incoming:
            sc.blit(IncomingGradient, (0, 0))

        for lane in self.lanes_held:
            sc.blit(NoteHitEffect, (self.note_x(lane), self.hit_y - BaseNoteWidth * 2))

        for press_effect in self.note_press_effects:
            lane, type, time = press_effect
            color = (255, 255, 0)
            if type == 1: color = (0, 125, 255)

            pg.draw.rect(sc, color, (
                int(self.note_x(lane)),
                int(self.hit_y - BaseNoteHeight / 2),
                int(BaseNoteWidth),
                int(BaseNoteHeight + time * 20)
            ), max(int(5 - time * 10), 1))

        for i, note in enumerate(self.notes):
            if note.y <= WinHeight + BaseNoteHeight:
                note_img = note.image
                try:
                    if note.time == self.notes[i - 1].time or note.time == self.notes[i + 1].time:
                        note_img = note.simultaneous
                except IndexError: pass

                sc.blit(note_img, (self.note_x(note.x), self.hit_y - note.y - note.h / 2))

    def keydown(self, ev: pg.Event):
        valid = (self.config.KEY_Note1, self.config.KEY_Note2, self.config.KEY_Note3, self.config.KEY_Note4)
        for i, k in enumerate(valid):
            if ev.key == k:
                self.lanes_held.append(i)
                self.lanes_pressed.append(i)

    def keyup(self, ev: pg.Event):
        valid = (self.config.KEY_Note1, self.config.KEY_Note2, self.config.KEY_Note3, self.config.KEY_Note4)
        for i, k in enumerate(valid):
            if ev.key == k and i in self.lanes_held:
                self.lanes_held.remove(i)

    def note_x(self, note):
        return note * BaseNoteWidth

    @property
    def hit_y(self):
        return int(WinHeight * 0.9)
