import pygame as pg

from src.config import Config
from src.note import Note, TapNote, DragNote

BaseNoteWidth: int = 0
BaseNoteHeight: int = 0
WinWidth: int = 0
WinHeight: int = 0

def init(sc: pg.Surface):
    global BaseNoteWidth, BaseNoteHeight, WinWidth, WinHeight
    from src.note import BaseNoteDimensions as BND
    BaseNoteWidth, BaseNoteHeight = BND
    WinWidth, WinHeight = sc.get_size()

PERFECT_TIMING = 0.08
GOOD_TIMING = 0.16
BAD_TIMING = 0.28

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
            note.y = note.time * self.speed

        self.width = BaseNoteWidth * 4

        self.chart = None

    def update_notes(self):
        for note in self.notes:
            note.y = note.time * self.speed

    def __repr__(self):
        return f"Lane{self.notes}"

    def update(self, dt: float):
        self.scroll += dt * self.speed

        pops = []
        for i, note in enumerate(self.notes):
            note.y -= self.speed * dt
            if note.x in self.lanes_pressed and isinstance(note, TapNote):
                time_offset = abs(note.y / self.speed)
                if time_offset <= PERFECT_TIMING:
                    self.chart.notes_hit += 1
                    self.chart.combo += 1
                elif time_offset <= GOOD_TIMING:
                    self.chart.notes_hit += 0.65
                    self.chart.combo += 1
                elif time_offset <= BAD_TIMING:
                    self.chart.combo = 0
                    self.lanes_pressed.remove(note.x)
                    pops.append(i)
                    continue
                else:
                    continue

                pops.append(i)
                note.play_sound()
                self.lanes_pressed.remove(note.x)

            elif note.x in self.lanes_held and isinstance(note, DragNote):
                if note.y <= 0 and abs(note.y / self.speed) < BAD_TIMING:
                    self.chart.combo += 1
                    note.play_sound()
                    pops.append(i)

            elif (note.y / self.speed) < -BAD_TIMING:
                pops.append(i)
                self.chart.combo = 0

        for i in pops:
            del self.notes[i]

        self.lanes_pressed = []

    def draw(self, sc: pg.Surface):
        for i, note in enumerate(self.notes):
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
